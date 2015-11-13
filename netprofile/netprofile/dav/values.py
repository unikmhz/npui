#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV value objects
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
	'DAVValue',
	'DAVResourceTypeValue',
	'DAVSupportedLockValue',
	'DAVLockDiscoveryValue',
	'DAVSupportedReportSetValue',
	'DAVSupportedPrivilegeSetValue',
	'DAVTagValue',
	'DAVBinaryValue',
	'DAVHrefValue',
	'DAVHrefListValue',
	'DAVSupportedAddressDataValue',
	'CalDAVSupportedCollationSetValue',
	'CardDAVSupportedCollationSetValue',

	'_parse_resource_type',
	'_parse_tag',
	'_parse_href',
	'_parse_hreflist',
	'_parse_supported_addressdata',
	'_parse_caldav_supported_collation_set',
	'_parse_carddav_supported_collation_set'
]

import datetime as dt
from lxml import etree

from . import props as dprops

class DAVValue(object):
	def render(self, req, parent):
		raise NotImplementedError('No render method defined for DAV value')

class DAVResourceTypeValue(DAVValue):
	def __init__(self, *types):
		self.types = types

	def render(self, req, parent):
		for t in self.types:
			etree.SubElement(parent, t)

def _parse_resource_type(el):
	ret = [item.tag for item in el]
	return DAVResourceTypeValue(*ret)

class DAVSupportedLockValue(DAVValue):
	def __init__(self, allow_locks=True):
		self.allow_locks = allow_locks

	def render(self, req, parent):
		if not self.allow_locks:
			return

		l_ex = etree.SubElement(parent, dprops.LOCK_ENTRY)
		l_sh = etree.SubElement(parent, dprops.LOCK_ENTRY)

		ls_ex = etree.SubElement(l_ex, dprops.LOCK_SCOPE)
		lt_ex = etree.SubElement(l_ex, dprops.LOCK_TYPE)

		ls_sh = etree.SubElement(l_sh, dprops.LOCK_SCOPE)
		lt_sh = etree.SubElement(l_sh, dprops.LOCK_TYPE)

		etree.SubElement(ls_ex, dprops.EXCLUSIVE)
		etree.SubElement(ls_sh, dprops.SHARED)
		etree.SubElement(lt_ex, dprops.WRITE)
		etree.SubElement(lt_sh, dprops.WRITE)

class DAVLockDiscoveryValue(DAVValue):
	def __init__(self, locks, show_token=False):
		self.locks = locks
		self.show_token = show_token

	def render(self, req, parent):
		for lock in self.locks:
			active = etree.SubElement(parent, dprops.ACTIVE_LOCK)
			el = etree.SubElement(active, dprops.LOCK_SCOPE)
			etree.SubElement(el, lock.get_dav_scope())
			el = etree.SubElement(active, dprops.LOCK_TYPE)
			etree.SubElement(el, dprops.WRITE)

			lockroot = etree.SubElement(active, dprops.LOCK_ROOT)
			el = etree.SubElement(lockroot, dprops.HREF)
			el.text = req.dav.uri(req, '/' + lock.uri)

			el = etree.SubElement(active, dprops.DEPTH)
			if lock.depth == dprops.DEPTH_INFINITY:
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

class DAVSupportedReportSetValue(DAVValue):
	def __init__(self, reports):
		self.reports = reports

	def render(self, req, parent):
		for rep in self.reports:
			suprep = etree.SubElement(parent, dprops.SUPPORTED_REPORT)
			el = etree.SubElement(suprep, dprops.REPORT)
			etree.SubElement(el, rep)

class DAVSupportedPrivilegeSetValue(DAVValue):
	def __init__(self, privileges):
		self.priv = privileges

	def render(self, req, parent):
		for p in self.priv:
			p.render(req, parent)

class DAVTagValue(DAVValue):
	def __init__(self, tag, value=None):
		self.tag = tag
		self.value = value

	def render(self, req, parent):
		node = etree.SubElement(parent, self.tag)
		if self.value is not None:
			node.text = self.value

def _parse_tag(el):
	try:
		el = el[0]
	except IndexError:
		return None
	val = None
	if el.text:
		val = el.text
	return DAVTagValue(el.tag, val)

class DAVBinaryValue(DAVValue):
	def __init__(self, buf):
		self.buf = buf

	def render(self, req, parent):
		buf = self.buf
		if isinstance(buf, (bytes, bytearray)):
			buf = buf.decode()
		parent.text = etree.CDATA(buf)

class DAVHrefValue(DAVValue):
	def __init__(self, value, prefix=False, path_only=False):
		self.value = value
		self.prefix = prefix
		self.path_only = path_only

	def render(self, req, parent):
		href = etree.SubElement(parent, dprops.HREF)
		val = self.value
		if not issubclass(val.__class__, str):
			href.text = req.dav.node_uri(req, val, path_only=self.path_only)
		elif self.prefix:
			href.text = req.dav.uri(req, path_only=self.path_only) + val
		else:
			href.text = val

	def get_uri(self, req):
		val = self.value
		if not issubclass(val.__class__, str):
			return req.dav.node_uri(req, val, path_only=self.path_only)
		elif self.prefix:
			return req.dav.uri(req, path_only=self.path_only) + val
		else:
			return val

	def get_node(self, req):
		val = self.value
		if not issubclass(val.__class__, str):
			return val
		elif self.prefix:
			return req.dav.node(req, req.dav.uri(req, path_only=self.path_only) + val)
		else:
			return req.dav.node(req, val)

def _parse_href(el):
	try:
		el = el[0]
	except IndexError:
		return None
	if el.tag != dprops.HREF:
		return None
	return DAVHrefValue(el.text.strip())

class DAVHrefListValue(DAVValue):
	def __init__(self, values, prefix=False, path_only=False):
		self.values = values
		self.prefix = prefix
		self.path_only = path_only

	def render(self, req, parent):
		pfx = req.dav.uri(req, path_only=self.path_only)
		for val in self.values:
			el = etree.SubElement(parent, dprops.HREF)
			if not isinstance(val, str):
				el.text = req.dav.node_uri(req, val, path_only=self.path_only)
			elif self.prefix:
				el.text = pfx + val
			else:
				el.text = val

def _parse_hreflist(el):
	ret = []
	for href in el:
		if href.tag == dprops.HREF:
			ret.append(href.text.strip())
	return DAVHrefListValue(ret)

class DAVSupportedAddressDataValue(DAVValue):
	def __init__(self, *tup):
		self.tuples = tup

	def render(self, req, parent):
		for tup in self.tuples:
			tl = len(tup)
			el = etree.SubElement(parent, dprops.ADDRESS_DATA_TYPE)
			if (tl > 0) and tup[0]:
				el.set('content-type', tup[0])
			if tl > 1:
				el.set('version', tup[1])

def _parse_supported_addressdata(el):
	ret = []
	for adt in el:
		if adt.tag == dprops.ADDRESS_DATA_TYPE:
			ctype = adt.get('content-type')
			ver = adt.get('version')
			if ctype:
				if ver:
					ret.append((ctype, ver))
				else:
					ret.append((ctype,))
			elif ver:
				ret.append((None, ver))
	return DAVSupportedAddressDataValue(*ret)

class CalDAVSupportedCollationSetValue(DAVValue):
	def __init__(self, *colls):
		self.colls = colls

	def render(self, req, parent):
		for coll in self.colls:
			el = etree.SubElement(parent, dprops.SUPPORTED_COLL_CAL)
			el.text = coll

def _parse_caldav_supported_collation_set(el):
	ret = []
	for coll in el:
		if coll.tag == dprops.SUPPORTED_COLL_CAL:
			ret.append(coll.text)
	return CalDAVSupportedCollationSetValue(*ret)

class CardDAVSupportedCollationSetValue(DAVValue):
	def __init__(self, *colls):
		self.colls = colls

	def render(self, req, parent):
		for coll in self.colls:
			el = etree.SubElement(parent, dprops.SUPPORTED_COLL_CARD)
			el.text = coll

def _parse_carddav_supported_collation_set(el):
	ret = []
	for coll in el:
		if coll.tag == dprops.SUPPORTED_COLL_CARD:
			ret.append(coll.text)
	return CardDAVSupportedCollationSetValue(*ret)

class DAVResponseValue(DAVValue):
	def __init__(self, node=None, props=None, status=None, names_only=False):
		self.node = node
		self.props = props
		self.status = status
		self.names_only = names_only

	def render(self, req, parent):
		el = etree.SubElement(parent, dprops.RESPONSE)
		if self.node:
			href = etree.SubElement(el, dprops.HREF)
			href.text = req.dav.node_uri(req, self.node)
		if self.status:
			status = etree.SubElement(el, dprops.STATUS)
			status.text = req.dav.get_http_status(self.status)
		if self.props:
			for st, props in self.props.items():
				if not len(props):
					continue
				propstat = etree.SubElement(el, dprops.PROPSTAT)
				prop = etree.SubElement(propstat, dprops.PROP)
				for k, v in props.items():
					curprop = etree.SubElement(prop, k)
					if (v is None) or self.names_only:
						pass
					elif isinstance(v, dt.datetime):
						curprop.text = v.strftime('%a, %d %b %Y %H:%M:%S')
					elif isinstance(v, DAVValue):
						v.render(req, curprop)
					else:
						curprop.text = str(v)
				status = etree.SubElement(propstat, dprops.STATUS)
				status.text = req.dav.get_http_status(st)

