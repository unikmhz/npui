#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV XML bits
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
	'DAVElement',
	'DAVNodeElement',
	'DAVResponseElement'
]

import datetime as dt
from lxml import etree

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

class DAVResponseElement(DAVNodeElement):
	def __init__(self, req, ctx, props=None, status=None, names_only=False):
		super(DAVResponseElement, self).__init__(req, ctx)
		self.props = props
		self.status = status
		self.names_only = names_only

	def to_xml(self):
		req = self.req
		el = etree.Element(dprops.RESPONSE)
		if isinstance(self.ctx, str):
			uri = self.ctx
		else:
			uri = req.dav.node_uri(req, self.ctx)
		href = etree.SubElement(el, dprops.HREF)
		href.text = uri
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
		return el

