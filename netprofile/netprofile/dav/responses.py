#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
	'DAVUnlockResponse',
	'DAVOverwriteResponse',
	'DAVDeleteResponse',
	'DAVETagResponse',
	'DAVCreateResponse',
	'DAVXMLResponse',
	'DAVErrorResponse',
	'DAVMultiStatusResponse',
	'DAVLockResponse'
]

from lxml import etree
from pyramid.response import Response

from . import props as dprops
from .errors import DAVError
from .values import DAVLockDiscoveryValue

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
	def __init__(self, *args, lock=None, request=None, new_file=False, **kwargs):
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
			val = DAVLockDiscoveryValue(request, (lock,), show_token=True)
			val.render(ld)

