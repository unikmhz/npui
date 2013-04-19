#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import urllib
import itertools
import datetime as dt
from dateutil.parser import parse as dparse
from lxml import etree

from zope.interface import (
	Interface,
	implementer,
)
from zope.interface.verify import verifyObject
from zope.interface.exceptions import DoesNotImplement
from webob.util import status_reasons

from pyramid.response import Response
from netprofile.db.connection import DBSession
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
		return ()

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

	def dav_create(self, req, name, rtype=None, props=None, data=None):
		raise DAVForbiddenError('Unable to create child node.')

	@property
	def dav_children(self):
		for plug in self.plugs.values():
			yield plug

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

def _parse_datetime(self, el):
	return dparse(el.text)

def _parse_resource_type(self, el):
	ret = [item.tag for item in el]
	return DAVResourceTypeValue(*ret)

VALUE_PARSERS = {
	dprops.RESOURCE_TYPE : _parse_resource_type,
	dprops.CREATION_DATE : _parse_datetime,
	dprops.LAST_MODIFIED : _parse_datetime
}

def parse_props(pnode, mapdict=VALUE_PARSERS):
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
		pset = dprops.DEFAULT_PROPS
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

def set_node_props(ctx, pdict):
	is_ok = True
	ret = {
		200 : {},
		403 : {},
		424 : {}
	}
	ro_props = dprops.RO_PROPS.intersect(pdict)
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
					ret[200][prop] = None
			else:
				for prop in pdict:
					ret[403][prop] = None
		pdict = {}
	
	for prop in pdict:
		ret[424][prop] = None
	return ret

def make_collection(req, parent, name, rtype, props):
	sess = DBSession()
	creator = getattr(parent, 'dav_create', None)
	if (creator is None) or (not callable(creator)):
		raise DAVNotImplementedError('Unable to create child node.')
	obj = creator(req, name, rtype.types, props)
	if len(props) == 0:
		pset = set(dprops.DEFAULT_PROPS)
		pset.update(props.keys())
	else:
		pset = set(props.keys())
	sess.flush()
	obj.__parent__ = parent
	return (obj, get_node_props(obj, pset))

def dav_children(parent):
	if hasattr(parent, 'dav_children'):
		for ch in parent.dav_children:
			yield ch
	else:
		try:
			for chname in parent:
				yield parent[chname]
		except TypeError:
			pass

def dav_delete(ctx):
	sess = DBSession()
	sess.delete(ctx)
	sess.flush()

def get_path_props(ctx, pset, depth):
	ret = {}
	ret[ctx] = get_node_props(ctx, pset) # catch exceptions
	if depth:
		for ch in dav_children(ctx):
			ret[ch] = get_node_props(ch, pset) # catch exceptions
	return ret

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

class DAVError(RuntimeError, DAVValue):
	def __init__(self, *args, status=500):
		super(DAVError, self).__init__(*args)
		self.status = status

	def render(self, parent):
		pass

	def response(self, resp):
		pass

class DAVBadRequestError(DAVError):
	def __init__(self, *args):
		super(DAVNotFoundError, self).__init__(*args, status=400)

class DAVNotAuthenticatedError(DAVError):
	def __init__(self, *args):
		super(DAVNotAuthenticatedError, self).__init__(*args, status=401)

class DAVForbiddenError(DAVError):
	def __init__(self, *args):
		super(DAVNotAuthenticatedError, self).__init__(*args, status=403)

class DAVNotFoundError(DAVError):
	def __init__(self, *args):
		super(DAVNotFoundError, self).__init__(*args, status=404)

class DAVInvalidResourceTypeError(DAVForbiddenError):
	def render(self, parent):
		etree.SubElement(parent, dprops.VALID_RESOURCETYPE)
		super(DAVInvalidResourceTypeError, self).render(parent)

class DAVReportNotSupportedError(DAVForbiddenError):
	def render(self, parent):
		etree.SubElement(parent, dprops.SUPPORTED_REPORT)
		super(DAVReportNotSupportedError, self).render(parent)

class DAVMethodNotAllowedError(DAVError):
	def __init__(self, *args):
		super(DAVMethodNotAllowedError, self).__init__(*args, status=405)

class DAVConflictError(DAVError):
	def __init__(self, *args):
		super(DAVConflictError, self).__init__(*args, status=409)

class DAVPreconditionError(DAVError):
	def __init__(self, *args, header=None):
		super(DAVConflictError, self).__init__(*args, status=412)
		self.header = header

class DAVUnsupportedMediaTypeError(DAVError):
	def __init__(self, *args):
		super(DAVUnsupportedMediaTypeError, self).__init__(*args, status=415)

class DAVNotImplementedError(DAVError):
	def __init__(self, *args):
		super(DAVNotImplementedError, self).__init__(*args, status=501)

	def response(self, resp):
		resp.allow = self.args

class DAVRequest(object):
	def __init__(self, req):
		self.req = req
		self.ctx = req.context

class DAVPropFindRequest(DAVRequest):
	def __init__(self, req):
		super(DAVPropFindRequest, self).__init__(req)
		if req.body:
			self.xml = etree.XML(req.body)
			if self.xml.tag != dprops.PROPFIND:
				self.xml = self.xml.find('.//%s' % dprops.PROPFIND)
		else:
			self.xml = None

	def get_props(self):
		return parse_propnames(self.xml)

class DAVPropPatchRequest(DAVRequest):
	def __init__(self, req):
		super(DAVPropFindRequest, self).__init__(req)
		if not req.body:
			raise DAVUnsupportedMediaTypeError('PROPPATCH method must be supplied with an XML request body.')
		self.xml = etree.XML(req.body)
		if not self.xml or (self.xml.tag != dprops.PROPERTY_UPDATE):
			raise DAVUnsupportedMediaTypeError('PROPPATCH method must be supplied with an XML request body.')

	def get_props(self):
		ret = {}
		for el in self.xml:
			props = None
			if el.tag == dprops.SET:
				props = parse_props(el)
			elif el.tag == dprops.REMOVE:
				props = dict.fromkeys(parse_propnames(el), None)
			ret.update(props)
		return ret

class DAVMkColRequest(DAVRequest):
	def __init__(self, req):
		super(DAVMkColRequest, self).__init__(req)
		self.new_name = req.view_name
		if len(req.subpath) > 0:
			raise DAVConflictError('Parent node does not exist.')
		# TODO: check if parent is a collection, if needed
		if req.body:
			if req.content_type not in {'application/xml', 'text/xml'}:
				raise DAVUnsupportedMediaTypeError('MKCOL method must be supplied with an XML request body.')
			self.xml = etree.XML(req.body)
			if not self.xml or (self.xml.tag != dprops.MKCOL):
				raise DAVUnsupportedMediaTypeError('MKCOL method body must contain mkcol root XML tag.')
		else:
			self.xml = None

	def get_props(self):
		if self.xml is None:
			return {
				dprops.RESOURCE_TYPE: DAVResourceTypeValue(dprops.COLLECTION)
			}
		ret = {}
		for el in self.xml:
			if el.tag != dprops.SET:
				continue
			ret.update(parse_props(el))
		return ret

	def process(self):
		props = self.get_props()
		try:
			rtype = props.pop(dprops.RESOURCE_TYPE)
		except KeyError:
			raise DAVBadRequestError('MKCOL method body must contain resource type property.')
		ret = make_collection(self.req, self.ctx, self.new_name, rtype, props)
		if ret is None:
			return DAVCreateResponse()
		resp = DAVMultiStatusResponse()
		resp.add_element(DAVResponseElement(*ret))
		resp.make_body()
		return resp

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

class DAVDeleteResponse(Response):
	def __init__(self, *args, **kwargs):
		super(DAVDeleteResponse, self).__init__(*args, **kwargs)
		self.status = 204

class DAVETagResponse(Response):
	def __init__(self, *args, etag=None, **kwargs):
		super(DAVETagResponse, self).__init__(*args, **kwargs)
		self.etag = etag
		self.status = 204

class DAVCreateResponse(DAVETagResponse):
	def __init__(self, *args, etag=None, **kwargs):
		super(DAVCreateResponse, self).__init__(*args, etag=etag, **kwargs)
		self.status = 201

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
		ns_map = dprops.NS_MAP.copy()
		if self.nsmap:
			ns_map.update(self.nsmap)
		self.xml_root = etree.Element(dprops.ERROR, nsmap=ns_map)
		self.err.render(self.xml_root)

	def make_body(self):
		self.err.response(self)
		super(DAVErrorResponse, self).make_body()

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

