#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV response objects
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

__all__ = [
	'DAVUnlockResponse',
	'DAVOverwriteResponse',
	'DAVDeleteResponse',
	'DAVETagResponse',
	'DAVCreateResponse',
	'DAVXMLResponse',
	'DAVMountResponse',
	'DAVErrorResponse',
	'DAVMultiStatusResponse',
	'DAVSyncCollectionResponse',
	'DAVLockResponse',
	'DAVPrincipalSearchPropertySetResponse'
]

from lxml import etree
from pyramid.response import Response
from pyramid.i18n import (
	TranslationString,
	get_localizer
)

from . import props as dprops
from .errors import DAVError
from .values import DAVLockDiscoveryValue

class DAVResponse(Response):
	def __init__(self, *args, request=None, **kwargs):
		super(DAVResponse, self).__init__(*args, **kwargs)
		self.req = request

class DAVUnlockResponse(DAVResponse):
	def __init__(self, *args, **kwargs):
		super(DAVUnlockResponse, self).__init__(*args, **kwargs)
		self.status = 204

class DAVOverwriteResponse(DAVResponse):
	def __init__(self, *args, **kwargs):
		super(DAVOverwriteResponse, self).__init__(*args, **kwargs)
		self.status = 204

class DAVDeleteResponse(DAVResponse):
	def __init__(self, *args, **kwargs):
		super(DAVDeleteResponse, self).__init__(*args, **kwargs)
		self.status = 204

class DAVETagResponse(DAVResponse):
	def __init__(self, *args, etag=None, **kwargs):
		super(DAVETagResponse, self).__init__(*args, **kwargs)
		self.etag = etag
		self.status = 204

class DAVCreateResponse(DAVETagResponse):
	def __init__(self, *args, etag=None, **kwargs):
		super(DAVCreateResponse, self).__init__(*args, etag=etag, **kwargs)
		self.status = 201

class DAVXMLResponse(DAVResponse):
	def __init__(self, *args, nsmap=None, **kwargs):
		super(DAVXMLResponse, self).__init__(*args, **kwargs)
		self.content_type = 'application/xml'
		self.charset = 'utf-8'
		self.xml_root = None
		self.nsmap = nsmap

	def make_body(self):
		#etree.cleanup_namespaces(self.xml_root)
		self.body = etree.tostring(
			self.xml_root,
			encoding='utf-8',
			xml_declaration=True,
			pretty_print=self.req.debug_enabled,
			with_tail=False
		)

	def append(self, el):
		self.xml_root.append(el)

class DAVMountResponse(DAVXMLResponse):
	def __init__(self, *args, path=None, username=None, **kwargs):
		super(DAVMountResponse, self).__init__(*args, **kwargs)
		self.content_type = 'application/davmount+xml'
		ns_map = dprops.NS_MAP.copy()
		if self.nsmap:
			ns_map.update(self.nsmap)
		self.xml_root = etree.Element(dprops.MOUNT, nsmap={
			'dm' : dprops.NS_DAVMOUNT
		})
		el = etree.SubElement(self.xml_root, dprops.MOUNT_URL)
		el.text = self.req.dav.uri(self.req, '/')
		if path is not None:
			el = etree.SubElement(self.xml_root, dprops.MOUNT_OPEN)
			el.text = path
		if username is not None:
			el = etree.SubElement(self.xml_root, dprops.MOUNT_USERNAME)
			el.text = username

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
		self.err.render(self.req, self.xml_root)

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

class DAVSyncCollectionResponse(DAVMultiStatusResponse):
	def __init__(self, *args, sync_token=None, **kwargs):
		super(DAVSyncCollectionResponse, self).__init__(*args, **kwargs)
		if sync_token is not None:
			tok = etree.SubElement(self.xml_root, dprops.SYNC_TOKEN)
			tok.text  = '%s%s' % (
				dprops.NS_SYNC,
				str(sync_token)
			)

class DAVLockResponse(DAVXMLResponse):
	def __init__(self, *args, lock=None, new_file=False, **kwargs):
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
			val = DAVLockDiscoveryValue((lock,), show_token=True)
			val.render(self.req, ld)

class DAVPrincipalSearchPropertySetResponse(DAVXMLResponse):
	def __init__(self, req, propdef, *args, **kwargs):
		super(DAVPrincipalSearchPropertySetResponse, self).__init__(*args, request=req, **kwargs)
		loc = get_localizer(req)
		ns_map = dprops.NS_MAP.copy()
		self.xml_root = etree.Element(dprops.PRINC_SEARCH_PROP_SET, nsmap=ns_map)
		for prop, descr in propdef.items():
			srcprop = etree.SubElement(self.xml_root, dprops.PRINC_SEARCH_PROP)
			el = etree.SubElement(srcprop, dprops.PROP)
			etree.SubElement(el, prop)
			if descr:
				el = etree.SubElement(srcprop, dprops.DESCRIPTION)
				if isinstance(descr, TranslationString):
					el.set('{http://www.w3.org/XML/1998/namespace}lang', req.locale_name)
					el.text = loc.translate(descr)
				else:
					el.set('{http://www.w3.org/XML/1998/namespace}lang', 'en')
					el.text = descr

