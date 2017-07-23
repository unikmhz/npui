#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: LDAP module
# Copyright © 2013-2017 Alex Unigovsky
#
# This file is part of NetProfile.
# NetProfile is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later
# version.
#
# NetProfile is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General
# Public License along with NetProfile. If not, see
# <http://www.gnu.org/licenses/>.

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

import ldap3
import ssl
from sqlalchemy import event
from sqlalchemy.orm import object_mapper
from pyramid.settings import aslist
from pyramid.threadlocal import get_current_request

from netprofile.common.hooks import (
    IHookManager,
    register_hook
)
from netprofile.common.util import make_config_dict

LDAPConn = None

_LDAP_ORM_CFG = 'netprofile.ldap.orm.%s.%s'


def _get_base(em, settings):
    sname = _LDAP_ORM_CFG % (em.name, 'base')
    if sname in settings:
        return settings.get(sname)
    return settings.get(_LDAP_ORM_CFG % ('default', 'base'))


def _get_scope(em, settings):
    sname = _LDAP_ORM_CFG % (em.name, 'scope')
    if sname not in settings:
        sname = _LDAP_ORM_CFG % ('default', 'scope')
    val = settings.get(sname)
    if val == 'one':
        return ldap3.LEVEL
    elif val == 'sub':
        return ldap3.SUBTREE
    return ldap3.BASE


def _gen_attrlist(cols, settings, info):
    object_classes = info.get('ldap_classes')

    def _attrlist(tgt):
        attrs = {'objectClass': list(object_classes)}
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
                val = getattr(tgt, prop.key)
            if not isinstance(val, (list, tuple)):
                if val == '':
                    val = None
                if val is not None:
                    val = [val]
            if isinstance(ldap_attr, (list, tuple)):
                for la in ldap_attr:
                    attrs[la] = val
            else:
                attrs[ldap_attr] = val
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


def _gen_ldap_object_load(em, info, settings, hm):
    base = _get_base(em, settings)
    scope = _get_scope(em, settings)
    rdn_attr = info.get('ldap_rdn')
    object_classes = info.get('ldap_classes')
    object_classes = ('(objectClass='
                      + ')(objectClass='.join(object_classes)
                      + ')')
    get_rdn = _gen_ldap_object_rdn(em, rdn_attr)

    def _ldap_object_load(tgt, ctx):
        if getattr(tgt, '__req__', None) is None:
            tgt.__req__ = get_current_request()
        rdn = get_rdn(tgt)
        flt = '(&(%s)%s)' % (rdn, object_classes)
        with LDAPConn as lc:
            tgt._ldap_data = lc.search(base, flt, search_scope=scope,
                                       attributes=ldap3.ALL_ATTRIBUTES)

    return _ldap_object_load


def _gen_ldap_object_store(em, info, settings, hm):
    cols = em.get_read_columns()
    base = _get_base(em, settings)
    rdn_attr = info.get('ldap_rdn')
    get_attrlist = _gen_attrlist(cols, settings, info)
    hook_name = 'ldap.attrs.%s.%s' % (em.model.__moddef__, em.name)
    get_rdn = _gen_ldap_object_rdn(em, rdn_attr)

    def _ldap_object_store(mapper, conn, tgt):
        attrs = get_attrlist(tgt)
        rdn = get_rdn(tgt)
        dn = '%s,%s' % (rdn, base)
        hm.run_hook(hook_name, tgt, dn, attrs)
        ldap_data = getattr(tgt, '_ldap_data', None)
        with LDAPConn as lc:
            if isinstance(ldap_data, int):
                # FIXME: check for errors
                ret, status = lc.get_response(ldap_data)
                if len(ret):
                    tgt._ldap_data = ldap_data = ret[0]
                else:
                    tgt._ldap_data = ldap_data = None
            if ldap_data:
                if dn != ldap_data['dn']:
                    # TODO: add code to handle moving objects to different
                    #       bases (new_superior=).
                    ret = lc.modify_dn(ldap_data['dn'], rdn,
                                       delete_old_dn=True)
                    # FIXME: check for errors
                    ret, status = lc.get_response(ret)
                    ldap_data['dn'] = dn
                xattrs = {}
                del_attrs = []
                for attr in attrs:
                    old_val = ldap_data['attributes'].get(attr)
                    new_val = attrs[attr]
                    if new_val is None:
                        if old_val:
                            xattrs[attr] = (ldap3.MODIFY_DELETE, ())
                        del_attrs.append(attr)
                    else:
                        xattrs[attr] = (ldap3.MODIFY_REPLACE, new_val)
                for attr in ldap_data['attributes']:
                    if attr not in attrs:
                        xattrs[attr] = (ldap3.MODIFY_DELETE, ())
                for attr in del_attrs:
                    del attrs[attr]
                ret = lc.modify(dn, xattrs)
                # FIXME: check for errors
                ret, status = lc.get_response(ret)
                tgt._ldap_data['attributes'] = attrs
            else:
                xattrs = {}
                for attr in attrs:
                    new_val = attrs[attr]
                    if new_val is not None:
                        xattrs[attr] = new_val
                ret = lc.add(dn, attributes=xattrs)
                # FIXME: check for errors
                ret, status = lc.get_response(ret)
                tgt._ldap_data = {'dn': dn, 'attributes': attrs}

    return _ldap_object_store


def _gen_ldap_object_delete(em, info, settings, hm):
    base = _get_base(em, settings)
    rdn_attr = info.get('ldap_rdn')
    get_rdn = _gen_ldap_object_rdn(em, rdn_attr)

    def _ldap_object_delete(mapper, conn, tgt):
        dn = '%s,%s' % (get_rdn(tgt), base)
        with LDAPConn as lc:
            ret = lc.delete(dn)
            # FIXME: check for errors
            ret, status = lc.get_response(ret)

    return _ldap_object_delete


@register_hook('np.model.load')
def _proc_model_ldap(mmgr, model):
    if not LDAPConn:
        return
    cls = model.model
    info = cls.__table__.info
    if 'ldap_classes' not in info or 'ldap_rdn' not in info:
        return

    registry = mmgr.cfg.registry
    settings = registry.settings
    hm = registry.getUtility(IHookManager)

    cls._ldap_load = _gen_ldap_object_load(model, info, settings, hm)
    cls._ldap_store = _gen_ldap_object_store(model, info, settings, hm)
    cls._ldap_delete = _gen_ldap_object_delete(model, info, settings, hm)

    event.listen(model.model, 'load', cls._ldap_load)
    event.listen(model.model, 'after_insert', cls._ldap_store)
    event.listen(model.model, 'after_update', cls._ldap_store)
    event.listen(model.model, 'after_delete', cls._ldap_delete)


def store(obj):
    if not LDAPConn:
        return
    cls = obj.__class__
    callback = getattr(cls, '_ldap_store', None)
    if callable(callback):
        return callback(object_mapper(obj), None, obj)


def includeme(config):
    global _ldap_active, LDAPConn

    settings = config.registry.settings
    conn_cfg = make_config_dict(settings, 'netprofile.ldap.connection.')
    ssl_cfg = make_config_dict(conn_cfg, 'ssl.')
    auth_cfg = make_config_dict(conn_cfg, 'auth.')
    pool_cfg = make_config_dict(conn_cfg, 'pool.')

    ldap_host = None
    server_opts = {}
    tls_opts = {}
    conn_opts = {'lazy': True}

    if 'uri' in conn_cfg:
        ldap_host = conn_cfg['uri']
    elif 'host' in conn_cfg:
        ldap_host = conn_cfg['host']

    if 'port' in conn_cfg:
        server_opts['port'] = conn_cfg['port']
    if 'protocol' in conn_cfg:
        conn_opts['version'] = conn_cfg['protocol']
    if 'type' in auth_cfg:
        value = auth_cfg['type']
        proc = None
        if value in {'anon', 'anonymous'}:
            proc = ldap3.ANONYMOUS
        elif value == 'simple':
            proc = ldap3.SIMPLE
        elif value == 'sasl':
            proc = ldap3.SASL
        elif value == 'ntlm':
            proc = ldap3.NTLM
        if proc:
            conn_opts['authentication'] = proc
    if 'user' in auth_cfg and 'password' in auth_cfg:
        conn_opts['user'] = auth_cfg['user']
        conn_opts['password'] = auth_cfg['password']
        if 'authentication' not in conn_opts:
            conn_opts['authentication'] = ldap3.SIMPLE
        bind = None
        bind_cfg = auth_cfg.get('bind', 'none')
        if bind_cfg == 'none':
            bind = ldap3.AUTO_BIND_NONE
        elif bind_cfg == 'no-tls':
            bind = ldap3.AUTO_BIND_NO_TLS
        elif bind_cfg == 'tls-before-bind':
            bind = ldap3.AUTO_BIND_TLS_BEFORE_BIND
        elif bind_cfg == 'tls-after-bind':
            bind = ldap3.AUTO_BIND_TLS_AFTER_BIND
        if bind:
            conn_opts['auto_bind'] = bind

    if 'key.file' in ssl_cfg and 'cert.file' in ssl_cfg:
        tls_opts['local_private_key_file'] = ssl_cfg['key.file']
        tls_opts['local_certificate_file'] = ssl_cfg['cert.file']
        if 'validate' not in ssl_cfg:
            tls_opts['validate'] = ssl.CERT_REQUIRED
    value = ssl_cfg.get('version', 'tls1.2')
    if hasattr(ssl, 'PROTOCOL_TLSv1') and value == 'tls1':
        value = ssl.PROTOCOL_TLSv1
    elif hasattr(ssl, 'PROTOCOL_TLSv1_1') and value == 'tls1.1':
        value = ssl.PROTOCOL_TLSv1_1
    elif hasattr(ssl, 'PROTOCOL_TLSv1_2'):
        value = ssl.PROTOCOL_TLSv1_2
    else:
        value = None
    if value is not None:
        tls_opts['version'] = value
    if 'validate' in ssl_cfg:
        value = ssl_cfg['validate']
        if value == 'none':
            tls_opts['validate'] = ssl.CERT_NONE
        elif value == 'optional':
            tls_opts['validate'] = ssl.CERT_OPTIONAL
        elif value == 'required':
            tls_opts['validate'] = ssl.CERT_REQUIRED
    if 'ca.file' in ssl_cfg:
        tls_opts['ca_certs_file'] = ssl_cfg['ca.file']
    if 'altnames' in ssl_cfg:
        tls_opts['valid_names'] = aslist(ssl_cfg['altnames'])
    if 'ca.path' in ssl_cfg:
        tls_opts['ca_certs_path'] = ssl_cfg['ca.path']
    if 'ca.data' in ssl_cfg:
        tls_opts['ca_certs_data'] = ssl_cfg['ca.data']
    if 'key.password' in ssl_cfg:
        tls_opts['local_private_key_password'] = ssl_cfg['key.password']

    tls = None
    if tls_opts:
        tls = ldap3.Tls(**tls_opts)
        server_opts['use_ssl'] = True

    if 'name' in pool_cfg:
        conn_opts['pool_name'] = pool_cfg['name']
    if 'size' in pool_cfg:
        conn_opts['pool_size'] = int(pool_cfg['size'])
    else:
        conn_opts['pool_size'] = 4
    if 'lifetime' in pool_cfg:
        conn_opts['pool_lifetime'] = int(pool_cfg['lifetime'])
    else:
        conn_opts['pool_lifetime'] = 300

    server = ldap3.Server(ldap_host, tls=tls, **server_opts)
    LDAPConn = ldap3.Connection(server, client_strategy=ldap3.REUSABLE,
                                **conn_opts)
    LDAPConn.open()

    def get_system_ldap(request):
        return LDAPConn

    config.add_request_method(get_system_ldap, str('ldap'), reify=True)

    config.scan()
