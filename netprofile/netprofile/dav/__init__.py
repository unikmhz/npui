#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from netprofile import PY3
if PY3:
	from urllib.parse import (
		urlparse,
		quote
	)
else:
	from urllib import quote
	from urlparse import urlparse

import uuid
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

from sqlalchemy.exc import IntegrityError
from pyramid.response import Response
from pyramid.traversal import traverse
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
		for plug in self.plugs.values():
			yield plug

class DAVPlugin(object):
	def __init__(self, req):
		self.req = req

DEPTH_INFINITY = -1

def get_path(uri):
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

def get_ctx_path(ctx):
	return [quote(el) for el in ctx.get_uri()[2:]]

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

def get_http_timeout(req):
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

def dav_delete(ctx, recurse=True, _flush=True):
	sess = DBSession()
	if recurse:
		for ch in dav_children(ctx):
			dav_delete(ch, recurse, False)
	sess.delete(ctx)
	if _flush:
		sess.flush()

def dav_clone(req, ctx, recurse=True, _flush=True):
	sess = DBSession()
	obj = ctx.dav_clone(req)
	sess.add(obj)
	if recurse:
		for ch in dav_children(ctx):
			newch = dav_clone(req, ch, recurse, False)
			obj.dav_append(req, newch, ch.__name__)
	return obj

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

class DAVLockDiscoveryValue(DAVValue):
	def __init__(self, baseuri, locks, show_token=False):
		self.base_uri = baseuri
		self.locks = locks
		self.show_token = show_token

	def render(self, parent):
		for lock in self.locks:
			active = etree.SubElement(parent, props.ACTIVE_LOCK)
			el = etree.SubElement(active, props.LOCK_SCOPE)
			etree.SubElement(el, lock.get_dav_scope())
			el = etree.SubElement(active, dprops.LOCK_TYPE)
			etree.SubElement(el, dprops.WRITE)

			lockroot = etree.SubElement(active, dprops.LOCK_ROOT)
			el = etree.SubElement(lockroot, dprops.HREF)
			el.text = '/'.join((self.base_uri, lock.uri))

			el = etree.SubElement(active, dprops.DEPTH)
			if lock.depth == DEPTH_INFINITY:
				el.text = 'infinity'
			else:
				el.text = str(lock.depth)

			if lock.creation_time and lock.timeout:
				delta = lock.timeout - lock.creation_time
				el = etree.SubElement(active, dprops.TIMEOUT)
				el.text = 'Second-%d' % delta.seconds

			if self.show_token:
				tok = etree.SubElement(active, dprops.LOCK_TOKEN)
				el = etree.SubElement(tok, dprops.HREF)
				el.text = 'opaquelocktoken:%s' % lock.token

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
		super(DAVBadRequestError, self).__init__(*args, status=400)

class DAVNotAuthenticatedError(DAVError):
	def __init__(self, *args):
		super(DAVNotAuthenticatedError, self).__init__(*args, status=401)

class DAVForbiddenError(DAVError):
	def __init__(self, *args):
		super(DAVForbiddenError, self).__init__(*args, status=403)

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

class DAVLockTokenMatchError(DAVConflictError):
	def render(self, parent):
		etree.SubElement(parent, dprops.LOCK_TOKEN_REQUEST_URI)
		super(DAVLockTokenMatchError, self).render(parent)

class DAVPreconditionError(DAVError):
	def __init__(self, *args, header=None):
		super(DAVPreconditionError, self).__init__(*args, status=412)
		self.header = header

class DAVUnsupportedMediaTypeError(DAVError):
	def __init__(self, *args):
		super(DAVUnsupportedMediaTypeError, self).__init__(*args, status=415)

class DAVLockedError(DAVError):
	def __init__(self, *args, lock=None):
		super(DAVLockedError, self).__init__(*args, status=423)
		self.lock = lock

	def render(self, parent):
		err = etree.SubElement(parent, dprops.LOCK_TOKEN_SUBMITTED)
		if self.lock:
			href = etree.SubElement(err, dprops.HREF)
			href.text = self.lock.uri

class DAVConflictingLockError(DAVLockedError):
	def render(self, parent):
		err = etree.SubElement(parent, dprops.NO_CONFLICTING_LOCK)
		if self.lock:
			href = etree.SubElement(err, dprops.HREF)
			href.text = self.lock.uri

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
			try:
				self.xml = etree.XML(req.body)
			except etree.XMLSyntaxError:
				raise DAVBadRequestError('Invalid or not well-formed XML supplied in a request.')
			if self.xml.tag != dprops.PROPFIND:
				self.xml = self.xml.find('.//%s' % dprops.PROPFIND)
		else:
			self.xml = None

	def get_props(self):
		return parse_propnames(self.xml)

class DAVPropPatchRequest(DAVRequest):
	def __init__(self, req):
		super(DAVPropPatchRequest, self).__init__(req)
		if not req.body:
			raise DAVUnsupportedMediaTypeError('PROPPATCH method must be supplied with an XML request body.')
		try:
			self.xml = etree.XML(req.body)
		except etree.XMLSyntaxError:
			raise DAVBadRequestError('Invalid or not well-formed XML supplied in a request.')
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
			if props:
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
			try:
				self.xml = etree.XML(req.body)
			except etree.XMLSyntaxError:
				raise DAVBadRequestError('Invalid or not well-formed XML supplied in a request.')
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
#		resp.add_element(DAVResponseElement(*ret))
		resp.make_body()
		return resp

class DAVLockRequest(DAVRequest):
	def __init__(self, req):
		super(DAVLockRequest, self).__init__(req)
		try:
			self.xml = etree.XML(req.body)
		except etree.XMLSyntaxError:
			raise DAVBadRequestError('Invalid or not well-formed XML supplied in a request.')

	def _content(self, node):
		return (node.text or '') + ''.join(etree.tostring(el, encoding='unicode') for el in node)

	def get_lock(self, cls):
		lock = cls(user_id = self.req.user.id)
		el = self.xml.find(dprops.OWNER)
		if el:
			lock.owner = self._content(el)
		lock.token = str(uuid.uuid4())
		if len(self.xml.xpath('d:lockscope/d:exclusive', namespaces=dprops.NS_MAP)) > 0:
			lock.scope = cls.SCOPE_EXCLUSIVE
		else:
			lock.scope = cls.SCOPE_SHARED
		lock.creation_time = dt.datetime.now()
		return lock

class DAVElement(object):
	pass

class DAVNodeElement(DAVElement):
	def __init__(self, ctx):
		self.ctx = ctx

	def get_uri(self):
		# FIXME: get scheme from config
		uri = ['http:/']
		uri.extend(self.ctx.get_uri())
		try:
			if verifyObject(IDAVCollection, self.ctx):
				uri.append('')
			elif verifyObject(IDAVPrincipal, self.ctx):
				uri.append('')
		except DoesNotImplement:
			pass
		uri[2:] = [quote(el) for el in uri[2:]]
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

class DAVUnlockResponse(Response):
	def __init__(self, *args, **kwargs):
		super(DAVUnlockResponse, self).__init__(*args, **kwargs)
		self.status = 204

class DAVOverwriteResponse(Response):
	def __init__(self, *args, **kwargs):
		super(DAVOverwriteResponse, self).__init__(*args, **kwargs)
		self.status = 204

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
		self.body = etree.tostring(
			self.xml_root,
			encoding='utf-8',
			xml_declaration=True,
			pretty_print=True,
			with_tail=False
		)

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
		self.xml_root = etree.Element(dprops.MULTI_STATUS, nsmap=ns_map)

	def add_element(self, resp_el):
		self.xml_root.append(resp_el.to_xml())

class DAVLockResponse(DAVXMLResponse):
	def __init__(self, *args, lock=None, base_url=None, new_file=False, **kwargs):
		super(DAVLockResponse, self).__init__(*args, **kwargs)
		if new_file:
			self.status = 201
		else:
			self.status = 200
		self.lock = lock
		ns_map = dprops.NS_MAP.copy()
		if self.nsmap:
			ns_map.update(self.nsmap)
		self.xml_root = etree.Element(dprops.PROP, nsmap=ns_map)
		if lock:
			self.headers.add('Lock-Token', '<opaquelocktoken:%s>' % (lock.token,))
			ld = etree.SubElement(self.xml_root, dprops.LOCK_DISCOVERY)
			val = DAVLockDiscoveryValue(base_url, (lock,), show_token=True)
			val.render(ld)

