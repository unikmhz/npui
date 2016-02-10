#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV-related nodes for Pyramid traversal
# © Copyright 2013-2015 Alex 'Unik' Unigovsky
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

__all__ = [
	'DAVTraverser',
	'DAVRoot',
	'DAVPlugin'
]

from netprofile import PY3
if PY3:
	from urllib.parse import urlparse
	from urllib.request import unquote
else:
	from urlparse import urlparse
	from urllib import unquote

from pyramid.traversal import (
	traverse,
	ResourceTreeTraverser
)
from pyramid.security import (
	Allow,
	Authenticated,
	DENY_ALL
)
from zope.interface import implementer

from netprofile.common.modules import IModuleManager

from . import props as dprops
from .interfaces import IDAVCollection
from .values import DAVResourceTypeValue
from .acls import (
	DAVACLRestrictions,
	DAVACEValue,
	DAVACLValue,
	DAVPrincipalValue
)

class DAVTraverser(ResourceTreeTraverser):
	VIEW_SELECTOR = None

@implementer(IDAVCollection)
class DAVRoot(object):
	"""
	DAV root context.
	"""
	__parent__ = None
	__name__ = 'dav'
	__dav_collid__ = 'ROOT'

	@property
	def name(self):
		return 'dav'

	@property
	def __acl__(self):
		return (
			(Allow, Authenticated, 'access'),
			(Allow, Authenticated, 'read'),
			DENY_ALL
		)

	def dav_acl(self, req):
		return DAVACLValue((
			DAVACEValue(
				DAVPrincipalValue(DAVPrincipalValue.AUTHENTICATED),
				grant=(dprops.ACL_READ, dprops.ACL_READ_ACL),
				protected=True
			),
		))

	def __getitem__(self, name):
		plug = self.plugs[name](self.req)
		plug.__name__ = name
		plug.__parent__ = self
		return plug

	def __iter__(self):
		return iter(self.plugs)

	def __init__(self, request):
		self.req = request
		self.mmgr = request.registry.getUtility(IModuleManager)
		self.plugs = self.mmgr.get_dav_plugins(request)

	def get_uri(self):
		return [ '' ]

	def dav_props(self, pset):
		ret = {}
		if dprops.DISPLAY_NAME in pset:
			ret[dprops.DISPLAY_NAME] = 'dav'
		if dprops.IS_COLLECTION in pset:
			ret[dprops.IS_COLLECTION] = '1'
		if dprops.IS_FOLDER in pset:
			ret[dprops.IS_FOLDER] = 't'
		if dprops.IS_HIDDEN in pset:
			ret[dprops.IS_HIDDEN] = '0'
		return ret

	def dav_create(self, req, name, rtype=None, props=None, data=None):
		raise DAVForbiddenError('Unable to create child node.')

	def resolve_uri(self, uri, exact=False, accept_path=True):
		url = urlparse(uri)
		url_loc = url.netloc
		if accept_path and (uri[0] == '/') and (url_loc == ''):
			url_loc = self.req.host
		elif not url.port:
			url_loc += ':80'
		if url_loc != self.req.host:
			raise ValueError('Alien URL supplied.')
		path = url.path.strip('/').split('/')[1:]
		path = [unquote(n) for n in path]
		tr = traverse(self, path)
		if exact and (tr['view_name'] or (len(tr['subpath']) > 0)):
			raise ValueError('Object not found.')
		return tr

	@property
	def dav_children(self):
		for name, plug in self.plugs.items():
			pl = plug(self.req)
			pl.__name__ = name
			pl.__parent__ = self
			yield pl

	@property
	def dav_collections(self):
		return self.dav_children

	@property
	def dav_collection_id(self):
		return 'ROOT'

	@property
	def dav_sync_token(self):
		get_st = self.req.dav.get_synctoken
		if callable(get_st):
			return get_st(self)

	def dav_changes(self, since_token):
		pass

@implementer(IDAVCollection)
class DAVPlugin(object):
	def __init__(self, req):
		self.req = req

	def get_uri(self):
		uri = self.__parent__.get_uri()
		uri.append(self.__name__)
		return uri

	def dav_props(self, pset):
		ret = {}
		if dprops.DISPLAY_NAME in pset:
			ret[dprops.DISPLAY_NAME] = self.__name__
		if dprops.IS_COLLECTION in pset:
			ret[dprops.IS_COLLECTION] = '1'
		if dprops.IS_FOLDER in pset:
			ret[dprops.IS_FOLDER] = 't'
		if dprops.IS_HIDDEN in pset:
			ret[dprops.IS_HIDDEN] = '0'
		return ret

	def dav_clone(self, req):
		raise DAVForbiddenError('Can\'t copy plug-in root folder.')

	@property
	def __plugin__(self):
		return self

	@property
	def __acl__(self):
		return (
			(Allow, Authenticated, 'access'),
			(Allow, Authenticated, 'read'),
			DENY_ALL
		)

	def dav_acl(self, req):
		return DAVACLValue((
			DAVACEValue(
				DAVPrincipalValue(DAVPrincipalValue.AUTHENTICATED),
				grant=(dprops.ACL_READ, dprops.ACL_READ_ACL),
				protected=True
			),
		))

	def acl_restrictions(self):
		return DAVACLRestrictions(
			DAVACLRestrictions.GRANT_ONLY |
			DAVACLRestrictions.NO_INVERT
		)

	@property
	def dav_collection_id(self):
		return self.__dav_collid__

	@property
	def dav_sync_token(self):
		get_st = self.req.dav.get_synctoken
		if callable(get_st):
			return get_st(self)

