#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV value objects
# © Copyright 2013 Alex 'Unik' Unigovsky
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
	'DAVTagValue',
	'DAVResourceTypeValue',
	'DAVSupportedLockValue',
	'DAVLockDiscoveryValue',
	'DAVSupportedReportSetValue',
	'DAVSupportedPrivilegeSetValue',
	'DAVHrefValue',
	'DAVHrefListValue',

	'_parse_resource_type',
	'_parse_href',
	'_parse_hreflist'
]

from lxml import etree

from . import props as dprops

class DAVValue(object):
	def render(self, req, parent):
		raise NotImplementedError('No render method defined for DAV value')

class DAVTagValue(DAVValue):
	def __init__(self, tag, value=None):
		self.tag = tag
		self.value = value

	def render(self, req, parent):
		node = etree.SubElement(parent, self.tag)
		if self.value is not None:
			node.text = self.value

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

class DAVHrefValue(DAVValue):
	def __init__(self, value, prefix=False):
		self.value = value
		self.prefix = prefix

	def render(self, req, parent):
		href = etree.SubElement(parent, dprops.HREF)
		val = self.value
		if not issubclass(val.__class__, str):
			href.text = req.dav.node_uri(req, val)
		elif self.prefix:
			href.text = req.dav.uri(req) + val
		else:
			href.text = val

def _parse_href(el):
	try:
		el = el[0]
	except IndexError:
		return None
	if el.tag != dprops.HREF:
		return None
	return DAVHrefValue(el.text.strip())

class DAVHrefListValue(DAVValue):
	def __init__(self, values, prefix=False):
		self.values = values
		self.prefix = prefix

	def render(self, req, parent):
		pfx = req.dav.uri(req)
		for val in self.values:
			el = etree.SubElement(parent, dprops.HREF)
			if not isinstance(val, str):
				el.text = req.dav.node_uri(req, val)
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

