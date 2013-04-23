#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
	'DAVSupportedPrivilegeSetValue'
]

from lxml import etree

from . import props as dprops

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

class DAVSupportedLockValue(DAVValue):
	def __init__(self, allow_locks=True):
		self.allow_locks = allow_locks

	def render(self, parent):
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
	def __init__(self, req, locks, show_token=False):
		self.req = req
		self.locks = locks
		self.show_token = show_token

	def render(self, parent):
		for lock in self.locks:
			active = etree.SubElement(parent, dprops.ACTIVE_LOCK)
			el = etree.SubElement(active, dprops.LOCK_SCOPE)
			etree.SubElement(el, lock.get_dav_scope())
			el = etree.SubElement(active, dprops.LOCK_TYPE)
			etree.SubElement(el, dprops.WRITE)

			lockroot = etree.SubElement(active, dprops.LOCK_ROOT)
			el = etree.SubElement(lockroot, dprops.HREF)
			#el.text = '/'.join((self.base_uri, lock.uri))
			el.text = self.req.route_url('core.dav', traverse=('/' + lock.uri))

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

	def render(self, parent):
		for rep in self.reports:
			suprep = etree.SubElement(parent, dprops.SUPPORTED_REPORT)
			el = etree.SubElement(suprep, dprops.REPORT)
			etree.SubElement(el, rep)

class DAVSupportedPrivilegeSetValue(DAVValue):
	def __init__(self, privileges):
		self.priv = privileges

