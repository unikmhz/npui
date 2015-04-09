#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV low-level library
# © Copyright 2013-2014 Alex 'Unik' Unigovsky
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

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from netprofile import PY3
if PY3:
	from urllib.parse import urlparse
	from urllib.request import quote
else:
	from urlparse import urlparse
	from urllib import quote

from dateutil.parser import parse as _dparse
from zope.interface import implementer
from zope.interface.verify import verifyObject
from zope.interface.exceptions import DoesNotImplement
from webob.util import status_reasons

from netprofile.db.connection import DBSession

from . import props as dprops
from .interfaces import *
from .values import *
from .errors import *
from .nodes import *
from .requests import *
from .elements import *
from .responses import *
from .reports import *
from .acls import *

def _parse_datetime(el):
	return _dparse(el.text)

class DAVAllPropsSet(object):
	def __contains__(self, el):
		return True

	def __len__(self):
		return 1

@implementer(IDAVManager)
class DAVManager(object):
	def __init__(self, config):
		self.cfg = config
		self.lock_cls = None
		self.features = ['1', '2', '3', 'extended-mkcol', 'access-control', 'sabredav-partialupdate']
		self.methods = [
			'OPTIONS', 'GET', 'HEAD', 'DELETE', 'PROPFIND',
			'PUT', 'PROPPATCH', 'COPY', 'MOVE', 'REPORT',
			'PATCH', 'LOCK', 'UNLOCK', 'ACL'
		]
		self.parsers = {
			dprops.RESOURCE_TYPE    : _parse_resource_type,
			dprops.CREATION_DATE    : _parse_datetime,
			dprops.LAST_MODIFIED    : _parse_datetime,
			dprops.GROUP_MEMBER_SET : _parse_hreflist,
			dprops.ACE              : _parse_ace,
			dprops.ACL              : _parse_acl
		}
		self.default_priv_set = (
			DAVPrivilegeValue(
				dprops.ACL_ALL,
				abstract=True,
				aggregates=(
					DAVPrivilegeValue(
						dprops.ACL_READ,
						aggregates=(
							DAVPrivilegeValue(dprops.ACL_READ_ACL),
							DAVPrivilegeValue(dprops.ACL_READ_CUR_USER_PSET)
						)
					),
					DAVPrivilegeValue(
						dprops.ACL_WRITE,
						aggregates=(
							DAVPrivilegeValue(dprops.ACL_WRITE_ACL),
							DAVPrivilegeValue(dprops.ACL_WRITE_PROPERTIES),
							DAVPrivilegeValue(dprops.ACL_WRITE_CONTENT),
							DAVPrivilegeValue(dprops.ACL_BIND),
							DAVPrivilegeValue(dprops.ACL_UNBIND),
							DAVPrivilegeValue(dprops.ACL_UNLOCK)
						)
					),
				)
			),
		)
		self.reports = {
			dprops.EXPAND_PROPERTY       : DAVExpandPropertyReport,
			dprops.PRINC_PROP_SEARCH     : DAVReport,
			dprops.PRINC_SEARCH_PROP_SET : DAVReport
		}

	def principal_collections(self, req):
		dr = DAVRoot(req)
		hlist = [ dr['users'], dr['groups'] ]
		# TODO: add hooks for other modules here
		return hlist

	def set_locks_backend(self, cls):
		self.lock_cls = cls

	def get_locks(self, path, children=False):
		if self.lock_cls is None:
			return []
		return self.lock_cls.find(path, children=children)

	def add_report(self, name, cls):
		self.reports[name] = cls

	def add_method(self, meth):
		self.methods.add(meth)

	def add_feature(self, feat):
		self.features.add(feat)

	def supported_report_set(self, node):
		rset = set()
		for rname, cls in self.reports.items():
			if hasattr(cls, 'supports') and callable(cls.supports) and (not cls.supports(node)):
				continue
			rset.add(rname)
		return rset

	def report(self, name, rreq):
		if name not in self.reports:
			raise DAVReportNotSupportedError('Requested report type is not supported.')
		return self.reports[name](name, rreq)

	def set_headers(self, resp):
		resp.status = 200
		resp.content_type = None
		resp.headers.add('DAV', ', '.join(self.features))
		resp.headers.add('MS-Author-Via', 'DAV')
		resp.accept_ranges = 'bytes'

	def set_features(self, resp):
		resp.headers.add('DAV', ', '.join(self.features))

	def set_patch_formats(self, resp):
		resp.headers.add('Accept-Patch', 'application/x-sabredav-partialupdate')

	def set_allow(self, resp, more=None):
		result = list(self.methods)
		if more:
			result.extend(more)
		return result

	def uri(self, req, tr=None):
		if tr is None:
			tr = '/'
		return req.route_url('core.dav', traverse=tr)

	def node_uri(self, req, node):
		uri = node.get_uri()
		try:
			if verifyObject(IDAVCollection, node):
				uri.append('')
		except DoesNotImplement:
			try:
				if verifyObject(IDAVPrincipal, node):
					uri.append('')
			except DoesNotImplement:
				pass
		return req.route_url('core.dav', traverse=uri)

	def node(self, req, uri):
		if not isinstance(uri, str):
			return uri
		dr = DAVRoot(req)
		tr = dr.resolve_uri(uri, True)
		return tr['context']

	def acl(self, req, princ, node, acl):
		acl_ok = None
		if not isinstance(acl, (list, set, tuple)):
			acl = (acl,)
		davacl = None
		if hasattr(node, 'dav_acl'):
			davacl = node.dav_acl(req)
		elif hasattr(node, '__plugin__'):
			plug = node.__plugin__
			if hasattr(plug, 'dav_acl'):
				davacl = plug.dav_acl(req)

		if davacl:
			acl_ok = davacl.check(req, princ, acl, node)
		if not acl_ok:
			raise DAVNeedPrivilegesError(node, acl)

	def user_acl(self, req, node, acl):
		return self.acl(req, req.user, node, acl)

	def has_acl(self, req, princ, node, acl):
		try:
			self.acl(req, princ, node, acl)
		except DAVNeedPrivilegesError:
			return False
		return True

	def has_user_acl(self, req, node, acl):
		try:
			self.acl(req, req.user, node, acl)
		except DAVNeedPrivilegesError:
			return False
		return True

	def path(self, uri):
		if not uri:
			return None
		uri = urlparse(uri)
		if not uri.path:
			return None
		path = uri.path
		if path[0] != '/':
			return None
		path = path.strip('/').split('/')
		if len(path) == 0:
			return None
		if uri.scheme or uri.hostname:
			path.pop(0)
		return path

	def ctx_path(self, ctx):
		return [quote(el) for el in ctx.get_uri()[1:]]

	def parse_props(self, req, pnode, mapdict=None):
		ret = {}
		if pnode is None:
			return ret
		if not mapdict:
			mapdict = self.parsers
		else:
			tmp = mapdict
			mapdict = self.parsers
			mapdict.update(tmp)
			del tmp
		for prop in pnode.iter(dprops.PROP):
			for data in prop:
				val = None
				if mapdict and (data.tag in mapdict):
					typemap = mapdict[data.tag]
					if callable(typemap):
						val = typemap(data)
					else:
						val = typemap
				else:
					val = data.text
				ret[data.tag] = val
		return ret

	def parse_propnames(self, req, pnode):
		ret = set()
		if pnode is None:
			return ret
		for prop in pnode.iter(dprops.PROP):
			for data in prop:
				ret.add(data.tag)
		return ret

	def get_http_depth(self, req, dd=dprops.DEPTH_INFINITY):
		d = req.headers.get('Depth')
		if d is None:
			return dd
		if d == 'infinity':
			return dprops.DEPTH_INFINITY
		try:
			return int(d)
		except (TypeError, ValueError):
			pass
		return dd

	def get_http_timeout(self, req):
		t = req.headers.get('Timeout')
		if not t:
			return 0
		ret = None
		t = t.lower().split(' ')
		for el in t:
			if el[:7] == 'second-':
				ret = int(el[7:])
			elif el == 'infinite':
				ret = None
			else:
				raise DAVBadRequestError('Invalid HTTP Timeout: header.')
		return ret

	def get_http_status(self, code, http_ver='1.1'):
		return 'HTTP/%s %d %s' % (
			http_ver,
			code,
			status_reasons[code]
		)

	def children(self, parent):
		if hasattr(parent, 'dav_children'):
			for ch in parent.dav_children:
				yield ch
		else:
			try:
				for chname in parent:
					yield parent[chname]
			except TypeError:
				pass

	def delete(self, req, ctx, recurse=True, _flush=True):
		sess = DBSession()
		if recurse:
			for ch in self.children(ctx):
				self.delete(req, ch, recurse, False)
		sess.delete(ctx)
		if _flush:
			sess.flush()

	def clone(self, req, ctx, recurse=True, _flush=True):
		sess = DBSession()
		obj = ctx.dav_clone(req)
		sess.add(obj)
		if recurse:
			for ch in self.children(ctx):
				newch = self.clone(req, ch, recurse, False)
				obj.dav_append(req, newch, ch.__name__)
		return obj

	def get_path_props(self, req, ctx, pset, depth, get_404=True):
		ret = {}
		ret[ctx] = self.get_node_props(req, ctx, pset, get_404=get_404) # catch exceptions
		if depth:
			for ch in self.children(ctx):
				ret[ch] = self.get_node_props(req, ch, pset, get_404=get_404) # catch exceptions
		return ret

	def props(self, req, node, pset, set403=None):
		# TODO: split this and clean up
		# First, get properties from an object
		props = node.dav_props(pset)
		# Now, append lock-related stuff
		if (dprops.SUPPORTED_LOCK in pset) and (dprops.SUPPORTED_LOCK not in props):
			props[dprops.SUPPORTED_LOCK] = DAVSupportedLockValue()
		if (dprops.LOCK_DISCOVERY in pset) and (dprops.LOCK_DISCOVERY not in props):
			locks = self.get_locks(self.ctx_path(node))
			props[dprops.LOCK_DISCOVERY] = DAVLockDiscoveryValue(locks, show_token=False)
		# Now, append report-related properties
		if (dprops.SUPPORTED_REPORT_SET in pset) and (dprops.SUPPORTED_REPORT_SET not in props):
			props[dprops.SUPPORTED_REPORT_SET] = DAVSupportedReportSetValue(self.supported_report_set(node))
		# Principal properties
		try:
			if verifyObject(IDAVPrincipal, node):
				if (dprops.ALTERNATE_URI_SET in pset) and (dprops.ALTERNATE_URI_SET not in props) and hasattr(node, 'dav_alt_uri'):
					props[dprops.ALTERNATE_URI_SET] = DAVHrefListValue(node.dav_alt_uri(req))
				if(dprops.PRINCIPAL_URL in pset) and (dprops.PRINCIPAL_URL not in props):
					props[dprops.PRINCIPAL_URL] = DAVHrefValue(node)
				if(dprops.GROUP_MEMBER_SET in pset) and (dprops.GROUP_MEMBER_SET not in props) and hasattr(node, 'dav_group_members'):
					props[dprops.GROUP_MEMBER_SET] = DAVHrefListValue(node.dav_group_members(req))
				if(dprops.GROUP_MEMBERSHIP in pset) and (dprops.GROUP_MEMBERSHIP not in props) and hasattr(node, 'dav_memberships'):
					props[dprops.GROUP_MEMBERSHIP] = DAVHrefListValue(node.dav_memberships(req))
		except DoesNotImplement:
			pass
		# ACL properties
		if (dprops.PRINCIPAL_COLL_SET in pset) and (dprops.PRINCIPAL_COLL_SET not in props):
			props[dprops.PRINCIPAL_COLL_SET] = DAVHrefListValue(req.dav.principal_collections(req))
		if (dprops.CUR_USER_PRINCIPAL in pset) and (dprops.CUR_USER_PRINCIPAL not in props):
			props[dprops.CUR_USER_PRINCIPAL] = DAVHrefValue(req.user)
		# TODO: check {DAV:}read-current-user-privilege-set
		if (dprops.CUR_USER_PRIVILEGE_SET in pset) and (dprops.CUR_USER_PRIVILEGE_SET not in props):
			if hasattr(node, 'dav_acl'):
				acl = node.dav_acl(req)
				if acl:
					props[dprops.CUR_USER_PRIVILEGE_SET] = DAVPrivilegeList(acl.all_privs(req, req.user, node))
			else:
				props[dprops.CUR_USER_PRIVILEGE_SET] = None
		if (dprops.SUPPORTED_PRIVILEGE_SET in pset) and (dprops.SUPPORTED_PRIVILEGE_SET not in props):
			cls = node.__class__
			if hasattr(cls, 'dav_privilege_set'):
				privset = cls.dav_privilege_set
			else:
				privset = self.default_priv_set
			props[dprops.SUPPORTED_PRIVILEGE_SET] = DAVPrivilegeSetValue(privset)
		if (dprops.ACL in pset) and (dprops.ACL not in props):
			# TODO: check ACL: {DAV:}read-acl
			if hasattr(node, 'dav_acl'):
				props[dprops.ACL] = node.dav_acl(req)
			else:
				props[dprops.ACL] = None
		if (dprops.ACL_RESTRICTIONS in pset) and (dprops.ACL_RESTRICTIONS not in props):
			plug = getattr(node, '__plugin__', None)
			if plug is None:
				props[dprops.ACL_RESTRICTIONS] = None
			else:
				if hasattr(plug, 'acl_restrictions'):
					props[dprops.ACL_RESTRICTIONS] = plug.acl_restrictions()
				else:
					props[dprops.ACL_RESTRICTIONS] = None
		if (dprops.OWNER in pset) and (dprops.OWNER not in props) and hasattr(node, 'dav_owner'):
			owner = node.dav_owner
			if owner:
				props[dprops.OWNER] = DAVHrefValue(owner)
		if (dprops.GROUP in pset) and (dprops.GROUP not in props) and hasattr(node, 'dav_group'):
			group = node.dav_group
			if group:
				props[dprops.GROUP] = DAVHrefValue(group)
		return props

	def get_node_props(self, req, ctx, pset=None, get_404=True):
		# TODO: add exceptions for ACL access controls etc.
		all_props = False
		if (pset is None) or (isinstance(pset, set) and (len(pset) == 0)):
			all_props = True
			pset = dprops.DEFAULT_PROPS
		if isinstance(pset, DAVAllPropsSet):
			all_props = True
			get_404 = False
		# TODO: handle add/remove from pset from hooks
		ret = {
			200 : {},
			403 : {},
			404 : {}
		}
		if len(pset) > 0:
			forbidden = set()
			props = self.props(req, ctx, pset, set403=forbidden)
			if isinstance(pset, DAVAllPropsSet):
				for pn in props:
					ret[200][pn] = props[pn]
			else:
				for pn in pset:
					if pn in props:
						ret[200][pn] = props[pn]
					elif (not all_props) and get_404:
						ret[404][pn] = None
			del props
		return ret

	def set_node_props(self, req, ctx, pdict):
		is_ok = True
		ret = {
			200 : {},
			403 : {},
			424 : {}
		}
		# TODO: handle ACLs
		ro_props = dprops.RO_PROPS.intersection(pdict)
		if len(ro_props) > 0:
			is_ok = False
			ret[403] = dict.fromkeys(ro_props, None)
			for prop in ro_props:
				del pdict[prop]
		if is_ok and (len(pdict) > 0):
			setter = getattr(ctx, 'dav_props_set', None)
			if (not setter) or not callable(setter):
				for prop in pdict:
					ret[403][prop] = None
			else:
				result = setter(pdict)
				# TODO: handle composite results
				if result:
					for prop in pdict:
						if pdict[prop] is not None:
							ret[200][prop] = None
				else:
					for prop in pdict:
						ret[403][prop] = None
			pdict = {}

		for prop in pdict:
			ret[424][prop] = None
		return ret

	def make_collection(self, req, parent, name, rtype, props):
		sess = DBSession()
		creator = getattr(parent, 'dav_create', None)
		if (creator is None) or (not callable(creator)):
			raise DAVNotImplementedError('Unable to create child node.')
		obj = creator(req, name, rtype.types, props)
		if len(props) == 0:
			pset = set(dprops.DEFAULT_PROPS)
		else:
			pset = set(props.keys())
		sess.flush()
		obj.__parent__ = parent
		return (obj, self.get_node_props(req, obj, pset))

def _get_davm(request):
	return request.registry.getUtility(IDAVManager)

def includeme(config):
	davm = DAVManager(config)
	config.registry.registerUtility(davm, IDAVManager)
	config.add_request_method(_get_davm, str('dav'), reify=True)

