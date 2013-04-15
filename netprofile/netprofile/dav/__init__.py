#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import urllib
import datetime as dt
from lxml import etree

from zope.interface import (
	Interface,
	implementer,
)
from zope.interface.verify import verifyObject
from zope.interface.exceptions import DoesNotImplement
from webob.util import status_reasons

from pyramid.response import Response
from netprofile.common.modules import IModuleManager
from netprofile.dav import props as dprops

class IDAVNode(Interface):
	"""
	Generic DAV node interface.
	"""
	pass

class IDAVCollection(IDAVNode):
	"""
	DAV collection interface.
	"""
	pass

class IDAVFile(IDAVNode):
	"""
	DAV file object interface.
	"""
	pass

class IDAVPrincipal(IDAVNode):
	"""
	DAV principal object interface.
	"""
	pass

@implementer(IDAVCollection)
class DAVRoot(object):
	"""
	DAV root context.
	"""
	__parent__ = None
	__name__ = None

	@property
	def name(self):
		return 'ROOT'

	@property
	def __acl__(self):
		return getattr(self.req, 'acls', ())

	def __getitem__(self, name):
		return self.plugs[name]

	def __iter__(self):
		return iter(self.plugs)

	def __init__(self, request):
		self.req = request
		self.mmgr = request.registry.getUtility(IModuleManager)
		self.plugs = self.mmgr.get_dav_plugins(request)
		for name, plug in self.plugs.items():
			plug.__name__ = name
			plug.__parent__ = self

	def get_uri(self):
		return [ self.req.host, 'dav' ]

	def dav_props(self, pset):
		ret = {}
		if dprops.RESOURCE_TYPE in pset:
			ret[dprops.RESOURCE_TYPE] = DAVResourceTypeValue(dprops.COLLECTION)
		if dprops.DISPLAY_NAME in pset:
			ret[dprops.DISPLAY_NAME] = 'dav'
		return ret

class DAVPlugin(object):
	def __init__(self, req):
		self.req = req

DEPTH_INFINITY = -1

def get_http_depth(req, dd=DEPTH_INFINITY):
	d = req.headers.get('Depth')
	if d is None:
		return dd
	if d == 'infinity':
		return DEPTH_INFINITY
	try:
		return int(d)
	except ValueError:
		pass
	return dd

def get_http_status(code, http_ver='1.1'):
	return 'HTTP/%s %d %s' % (
		http_ver,
		code,
		status_reasons[code]
	)

def parse_props(pnode, mapdict=None):
	ret = {}
	if pnode is None:
		return ret
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

def parse_propnames(pnode):
	ret = set()
	if pnode is None:
		return ret
	for prop in pnode.iter(dprops.PROP):
		for data in prop:
			ret.add(data.tag)
	return ret

def get_node_props(ctx, pset=None):
	# TODO: add exceptions for ACL access controls etc.
	all_props = False
	if (pset is None) or (len(pset) == 0):
		all_props = True
		pset = set(
			dprops.CONTENT_LENGTH,
			dprops.CONTENT_TYPE,
			dprops.ETAG,
			dprops.LAST_MODIFIED,
			dprops.QUOTA_AVAIL_BYTES,
			dprops.QUOTA_USED_BYTES,
			dprops.RESOURCE_TYPE
		)
	# TODO: handle add/remove from pset from hooks
	ret = {
		200 : {},
		404 : {}
	}
	found = {}
	not_found = {}
	if len(pset) > 0:
		props = ctx.dav_props(pset)
		for pn in pset:
			if pn in props:
				ret[200][pn] = props[pn]
			elif not all_props:
				ret[404][pn] = None
		del props
	return ret

def get_path_props(ctx, pset, depth):
	ret = {}
	ret[ctx] = get_node_props(ctx, pset) # catch exceptions
	if depth:
		child_iter = None
		if hasattr(ctx, 'dav_children'):
			for ch in ctx.dav_children:
				ret[ch] = get_node_props(ch, pset) # catch exceptions
		else:
			for chname in ctx:
				ch = ctx[chname]
				ret[ch] = get_node_props(ch, pset) # catch exceptions
	return ret

class DAVError(RuntimeError):
	def __init__(self, *args, status=500):
		super(DAVError, self).__init__(*args)
		self.status = status

class DAVNotFoundError(DAVError):
	def __init__(self, *args):
		super(DAVNotFoundError, self).__init__(*args, status=404)

class DAVNotAuthenticatedError(DAVError):
	def __init__(self, *args):
		super(DAVNotAuthenticatedError, self).__init__(*args, status=401)

class DAVValue(object):
	def render(self, parent):
		raise NotImplementedError('No render method defined for DAV value')

class DAVTagValue(DAVValue):
	def __init__(self, tag, value=None):
		self.tag = tag
		self.value = value

	def render(self, parent):
		node = etree.SubElement(parent, self.tag)
		if self.value is not None:
			node.text = self.value

class DAVResourceTypeValue(DAVValue):
	def __init__(self, *types):
		self.types = types

	def render(self, parent):
		for t in self.types:
			etree.SubElement(parent, t)

class DAVRequest(object):
	def __init__(self, req):
		self.req = req
		self.ctx = req.context
		if req.body:
			self.xml = etree.XML(req.body)
			if self.xml.tag != dprops.PROPFIND:
				self.xml = self.xml.find('.//%s' % dprops.PROPFIND)
		else:
			self.xml = None

class DAVPropFindRequest(DAVRequest):
	def get_props(self):
		return parse_propnames(self.xml)

class DAVElement(object):
	pass

class DAVNodeElement(DAVElement):
	def __init__(self, ctx):
		self.ctx = ctx

	def get_uri(self):
		uri = ['http:/']
		uri.extend(self.ctx.get_uri())
		try:
			if verifyObject(IDAVCollection, self.ctx):
				uri.append('')
			elif verifyObject(IDAVPrincipal, self.ctx):
				uri.append('')
		except DoesNotImplement:
			pass
		uri[2:] = [urllib.parse.quote(el) for el in uri[2:]]
		return '/'.join(uri)

class DAVResponseElement(DAVNodeElement):
	def __init__(self, ctx, props=None, status=None):
		super(DAVResponseElement, self).__init__(ctx)
		self.props = props
		self.status = status

	def to_xml(self):
		el = etree.Element(dprops.RESPONSE)
		uri = self.get_uri()
		href = etree.SubElement(el, dprops.HREF)
		href.text = uri
		if self.status:
			status = etree.SubElement(el, dprops.STATUS)
			status.text = get_http_status(self.status)
		if self.props:
			for st, props in self.props.items():
				if not len(props):
					continue
				propstat = etree.SubElement(el, dprops.PROPSTAT)
				prop = etree.SubElement(propstat, dprops.PROP)
				for k, v in props.items():
					curprop = etree.SubElement(prop, k)
					if v is None:
						pass
					elif isinstance(v, dt.datetime):
						curprop.text = v.isoformat()
					elif isinstance(v, DAVValue):
						v.render(curprop)
					else:
						curprop.text = str(v)
				status = etree.SubElement(propstat, dprops.STATUS)
				status.text = get_http_status(st)
		return el

class DAVXMLResponse(Response):
	def __init__(self, *args, nsmap=None, **kwargs):
		super(DAVXMLResponse, self).__init__(*args, **kwargs)
		self.content_type = 'application/xml'
		self.charset = 'utf-8'
		self.xml_root = None
		self.nsmap = nsmap

	def make_body(self):
		# TODO: pretty-print only when debugging
		self.body = etree.tostring(self.xml_root, encoding='utf-8', xml_declaration=True, pretty_print=True, with_tail=False)

	def append(self, el):
		self.xml_root.append(el)

class DAVErrorResponse(DAVXMLResponse):
	def __init__(self, *args, error=None, **kwargs):
		super(DAVErrorResponse, self).__init__(*args, **kwargs)
		if error:
			self.err = error
		else:
			self.err = DAVError()
		self.status = self.err.status
		self.xml_root = etree.Element(dprops.ERROR, nsmap=dprops.NS_MAP)

class DAVMultiStatusResponse(DAVXMLResponse):
	def __init__(self, *args, strip_notfound=False, **kwargs):
		super(DAVMultiStatusResponse, self).__init__(*args, **kwargs)
		self.strip_notfound = strip_notfound
		self.status = 207
		ns_map = dprops.NS_MAP.copy()
		if self.nsmap:
			ns_map.update(self.nsmap)
		self.xml_root = etree.Element(dprops.MULTISTATUS, nsmap=ns_map)

	def add_element(self, resp_el):
		self.xml_root.append(resp_el.to_xml())

