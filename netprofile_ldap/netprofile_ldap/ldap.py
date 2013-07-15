#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import ldap
from sqlalchemy import event
from ldappool import ConnectionManager
from pyramid.settings import asbool
#from pyramid.threadlocal import get_current_request
#from netprofile.ext.data import ExtModel
#from netprofile.common.modules import IModuleManager
from netprofile.common.hooks import register_hook

# _ = TranslationStringFactory('netprofile_ldap')

LDAPPool = None

_LDAP_ORM_CFG = 'netprofile.ldap.orm.%s.%s'
_ldap_active = False

# model-level:
# ldap_classes
# ldap_rdn

# column-level:
# ldap_attr (can be a list)
# ldap_value (can be a callable)

class LDAPConnector(object):
	def __init__(self, pool, req):
		self.pool = pool
		self.req = req

	def connection(self, login=None, pwd=None):
		return self.pool.connection(login, pwd)

def _gen_search_attrs(em, settings):
	attrs = []
	sname = _LDAP_ORM_CFG % (em.name, 'base')
	if sname not in settings:
		sname = _LDAP_ORM_CFG % ('default', 'base')
	attrs.append(settings.get(sname))

	sname = _LDAP_ORM_CFG % (em.name, 'scope')
	if sname not in settings:
		sname = _LDAP_ORM_CFG % ('default', 'scope')
	val = settings.get(sname, 'base')
	if val == 'base':
		val = ldap.SCOPE_BASE
	elif val == 'one':
		val = ldap.SCOPE_ONELEVEL
	elif val == 'sub':
		val = ldap.SCOPE_SUBTREE
	attrs.append(val)

	return attrs

def _gen_attrlist(cols, settings, info):
	object_classes = info.get('ldap_classes')
	def _attrlist(tgt):
		attrs = {
			'objectClass' : []
		}
		for oc in object_classes:
			attrs['objectClass'].append(oc.encode())
		for cname, col in cols.items():
			try:
				ldap_attr = col.column.info['ldap_attr']
			except KeyError:
				continue
			prop = tgt.__mapper__.get_property_by_column(col.column)
			if 'ldap_value' in col.column.info:
				cb = col.column.info['ldap_value']
				try:
					cb = getattr(tgt, cb)
				except AttributeError:
					continue
				if not callable(cb):
					continue
				try:
					val = cb(settings)
				except ValueError:
					continue
			else:
				# TODO: handle multiple values
				val = getattr(tgt, prop.key)
			if (not isinstance(val, bytes)) and (val is not None):
				if not isinstance(val, str):
					val = str(val)
				val = val.encode()
			if isinstance(ldap_attr, (list, tuple)):
				for la in ldap_attr:
					attrs[la] = [val]
			else:
				if val is None:
					attrs[ldap_attr] = None
				else:
					attrs[ldap_attr] = [val]
		extra = getattr(tgt, 'ldap_attrs', None)
		if extra and callable(extra):
			attrs.update(extra(settings))
		return attrs
	return _attrlist

def get_rdn(obj):
	ldap_rdn = obj.__table__.info.get('ldap_rdn')
	col = obj.__table__.columns[ldap_rdn]
	prop = obj.__mapper__.get_property_by_column(col)
	try:
		ldap_attr = col.info['ldap_attr']
	except KeyError:
		ldap_attr = ldap_rdn
	if isinstance(ldap_attr, (list, tuple)):
		ldap_attr = ldap_attr[0]
	return '%s=%s' % (ldap_attr, getattr(obj, prop.key))

def get_dn(obj, settings):
	sname = _LDAP_ORM_CFG % (obj.__class__.__name__, 'base')
	if sname not in settings:
		sname = _LDAP_ORM_CFG % ('default', 'base')
	base = settings.get(sname)
	return '%s,%s' % (get_rdn(obj), base)

def _gen_ldap_object_rdn(em, rdn_col):
	col = em.get_column(rdn_col)
	prop = em.model.__mapper__.get_property_by_column(col.column)
	try:
		ldap_attr = col.column.info['ldap_attr']
	except KeyError:
		ldap_attr = rdn_col
	if isinstance(ldap_attr, (list, tuple)):
		ldap_attr = ldap_attr[0]
	def _ldap_object_rdn(tgt):
		return '%s=%s' % (ldap_attr, getattr(tgt, prop.key))
	return _ldap_object_rdn

def _gen_ldap_object_load(em, info, settings):
	attrs = _gen_search_attrs(em, settings)
	rdn_attr = info.get('ldap_rdn')
	object_classes = info.get('ldap_classes')
	object_classes = '(objectClass=' + ')(objectClass='.join(object_classes) + ')'
	get_rdn = _gen_ldap_object_rdn(em, rdn_attr)
	def _ldap_object_load(tgt, ctx):
		ret = None
		rdn = get_rdn(tgt)
		flt = '(&(%s)%s)' % (rdn, object_classes)
		with LDAPPool.connection() as lc:
			ret = lc.search_s(attrs[0], attrs[1], flt)
		if isinstance(ret, list) and (len(ret) > 0):
			tgt._ldap_data = ret[0]
	return _ldap_object_load

def _gen_ldap_object_store(em, info, settings):
	cols = em.get_read_columns()
	cfg = _gen_search_attrs(em, settings)
	rdn_attr = info.get('ldap_rdn')
	get_attrlist = _gen_attrlist(cols, settings, info)
	get_rdn = _gen_ldap_object_rdn(em, rdn_attr)
	def _ldap_object_store(mapper, conn, tgt):
		attrs = get_attrlist(tgt)
		dn = '%s,%s' % (get_rdn(tgt), cfg[0])
		ldap_data = getattr(tgt, '_ldap_data', False)
		with LDAPPool.connection() as lc:
			if ldap_data:
				if dn != ldap_data[0]:
					lc.rename_s(ldap_data[0], dn)
					tgt._ldap_data = ldap_data = (dn, ldap_data[1])
				xattrs = []
				del_attrs = []
				for attr in attrs:
					val = attrs[attr]
					if val is None:
						if attr in ldap_data[1]:
							xattrs.append((ldap.MOD_DELETE, attr, val))
						del_attrs.append(attr)
					else:
						xattrs.append((ldap.MOD_REPLACE, attr, val))
				for attr in del_attrs:
					del attrs[attr]
				lc.modify_s(ldap_data[0], xattrs)
				tgt._ldap_data[1].update(attrs)
			else:
				lc.add_s(dn, list(attrs.items()))
				tgt._ldap_data = (dn, attrs)
	return _ldap_object_store

def _gen_ldap_object_delete(em, info, settings):
	cfg = _gen_search_attrs(em, settings)
	rdn_attr = info.get('ldap_rdn')
	get_rdn = _gen_ldap_object_rdn(em, rdn_attr)
	def _ldap_object_delete(mapper, conn, tgt):
		dn = '%s,%s' % (get_rdn(tgt), cfg[0])
		with LDAPPool.connection() as lc:
			lc.delete_s(dn)
	return _ldap_object_delete

@register_hook('np.model.load')
def _proc_model_ldap(mmgr, model):
	if not _ldap_active:
		return
	info = model.model.__table__.info
	if ('ldap_classes' not in info) or ('ldap_rdn' not in info):
		return

	settings = mmgr.cfg.registry.settings

	event.listen(model.model, 'load', _gen_ldap_object_load(model, info, settings))
	event.listen(model.model, 'after_insert', _gen_ldap_object_store(model, info, settings))
	event.listen(model.model, 'after_update', _gen_ldap_object_store(model, info, settings))
	event.listen(model.model, 'after_delete', _gen_ldap_object_delete(model, info, settings))

def includeme(config):
	global _ldap_active, LDAPPool

	settings = config.registry.settings
	ldap_cfg = {}
	ldap_names = (
		'uri', 'bind', 'passwd',
		'size', 'retry_max', 'retry_delay',
		'use_tls', 'timeout', 'use_pool'
	)
	for name in ldap_names:
		qname = 'netprofile.ldap.connection.%s' % name
		value = settings.get(qname, None)
		if value is not None:
			if name in {'size', 'retry_max', 'timeout'}:
				value = int(value)
			elif name == 'retry_delay':
				value = float(value)
			elif name in {'use_tls', 'use_pool'}:
				value = asbool(value)
			ldap_cfg[name] = value

	LDAPPool = ConnectionManager(**ldap_cfg)

	def get_system_ldap(request):
		return LDAPConnector(LDAPPool, request)
	config.add_request_method(get_system_ldap, str('ldap'), reify=True)

	_ldap_active = True

	config.scan()

