#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
else:
	from urlparse import urlparse

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

class DAVTraverser(ResourceTreeTraverser):
	VIEW_SELECTOR = None

@implementer(IDAVCollection)
class DAVRoot(object):
	"""
	DAV root context.
	"""
	__parent__ = None
	__name__ = 'dav'

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
		if dprops.RESOURCE_TYPE in pset:
			ret[dprops.RESOURCE_TYPE] = DAVResourceTypeValue(dprops.COLLECTION)
		if dprops.DISPLAY_NAME in pset:
			ret[dprops.DISPLAY_NAME] = 'dav'
		return ret

	def dav_create(self, req, name, rtype=None, props=None, data=None):
		raise DAVForbiddenError('Unable to create child node.')

	def resolve_uri(self, uri, exact=False):
		url = urlparse(uri)
		if url.netloc != self.req.host:
			raise ValueError('Alien URL supplied.')
		tr = traverse(self, url.path.strip('/').split('/')[1:])
		if exact and (tr.view_name or (len(tr.subpath) > 0)):
			raise ValueError('Object not found.')
		return tr

	@property
	def dav_children(self):
		for name, plug in self.plugs.items():
			pl = plug(self.req)
			pl.__name__ = name
			pl.__parent__ = self
			yield pl

class DAVPlugin(object):
	def __init__(self, req):
		self.req = req

	def get_uri(self):
		uri = self.__parent__.get_uri()
		uri.append(self.__name__)
		return uri

	def dav_props(self, pset):
		ret = {}
		if dprops.RESOURCE_TYPE in pset:
			ret[dprops.RESOURCE_TYPE] = DAVResourceTypeValue(dprops.COLLECTION)
		if dprops.DISPLAY_NAME in pset:
			ret[dprops.DISPLAY_NAME] = self.__name__
		return ret

	def dav_clone(self, req):
		raise DAVForbiddenError('Can\'t copy plug-in root folder.')

	@property
	def __acl__(self):
		return (
			(Allow, Authenticated, 'access'),
			(Allow, Authenticated, 'read'),
			DENY_ALL
		)

