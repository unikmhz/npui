#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV request objects
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
	'DAVRequest',
	'DAVPropFindRequest',
	'DAVPropPatchRequest',
	'DAVMkColRequest',
	'DAVLockRequest',
	'DAVReportRequest'
]

import uuid
import datetime as dt
from lxml import etree

from . import props as dprops
from .errors import (
	DAVBadRequestError,
	DAVConflictError,
	DAVUnsupportedMediaTypeError
)
from .responses import (
	DAVCreateResponse,
	DAVMultiStatusResponse
)
from .elements import DAVResponseElement
from .values import DAVResourceTypeValue

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

	def is_allprop_request(self):
		if (len(self.xml) >= 1) and (self.xml[0].tag == dprops.ALL_PROPS):
			return True
		return False

	def is_propname_request(self):
		if (len(self.xml) >= 1) and (self.xml[0].tag == dprops.PROPNAME):
			return True
		return False

	def get_props(self):
		return self.req.dav.parse_propnames(self.req, self.xml)

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
		req = self.req
		ret = {}
		for el in self.xml:
			props = None
			if el.tag == dprops.SET:
				props = req.dav.parse_props(req, el)
			elif el.tag == dprops.REMOVE:
				props = dict.fromkeys(req.dav.parse_propnames(req, el), None)
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
			ret.update(self.req.dav.parse_props(self.req, el))
		return ret

	def process(self):
		props = self.get_props()
		try:
			rtype = props.pop(dprops.RESOURCE_TYPE)
		except KeyError:
			raise DAVBadRequestError('MKCOL method body must contain resource type property.')
		req = self.req
		ret = req.dav.make_collection(req, self.ctx, self.new_name, rtype, props)
		if ret is None:
			return DAVCreateResponse(request=req)
		resp = DAVMultiStatusResponse(request=req)
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

class DAVReportRequest(DAVRequest):
	def __init__(self, req):
		super(DAVReportRequest, self).__init__(req)
		try:
			self.xml = etree.XML(req.body)
		except etree.XMLSyntaxError:
			raise DAVBadRequestError('Invalid or not well-formed XML supplied in a request.')

	def get_name(self):
		try:
			return self.xml.tag
		except AttributeError:
			return None

