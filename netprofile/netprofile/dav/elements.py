#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
	'DAVElement',
	'DAVNodeElement',
	'DAVResponseElement'
]

import datetime as dt
from lxml import etree
from zope.interface.verify import verifyObject
from zope.interface.exceptions import DoesNotImplement

from . import props as dprops
from .interfaces import (
	IDAVCollection,
	IDAVPrincipal
)
from .values import DAVValue

class DAVElement(object):
	pass

class DAVNodeElement(DAVElement):
	def __init__(self, req, ctx):
		self.req = req
		self.ctx = ctx

	def get_uri(self):
		uri = self.ctx.get_uri()
		try:
			if verifyObject(IDAVCollection, self.ctx):
				uri.append('')
		except DoesNotImplement:
			try:
				if verifyObject(IDAVPrincipal, self.ctx):
					uri.append('')
			except DoesNotImplement:
				pass
		return self.req.route_url('core.dav', traverse=uri)

class DAVResponseElement(DAVNodeElement):
	def __init__(self, req, ctx, props=None, status=None):
		super(DAVResponseElement, self).__init__(req, ctx)
		self.props = props
		self.status = status

	def to_xml(self):
		el = etree.Element(dprops.RESPONSE)
		uri = self.get_uri()
		href = etree.SubElement(el, dprops.HREF)
		href.text = uri
		if self.status:
			status = etree.SubElement(el, dprops.STATUS)
			status.text = self.req.dav.get_http_status(self.status)
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
				status.text = self.req.dav.get_http_status(st)
		return el

