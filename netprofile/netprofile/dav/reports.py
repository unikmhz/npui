#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV report objects
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
	'DAVReport',
	'DAVExpandPropertyReport'
]

from . import props as dprops
from .errors import (
	DAVBadRequestError,
	DAVNotImplementedError
)
from .values import (
	DAVHrefValue,
	DAVResponseValue
)
from .responses import DAVMultiStatusResponse
from .elements import DAVResponseElement

class DAVReport(object):
	def __init__(self, rname, rreq):
		self.name = rname
		self.rreq = rreq

	def __call__(self, req):
		raise DAVNotImplementedError('Report %s not implemented.' % self.name)

class DAVExpandPropertyReport(DAVReport):
	def __call__(self, req):
		node = self.rreq.ctx
		root = self.rreq.xml

		props = self.get_props(node, root, req)
		# TODO: handle 'minimal' flags
		resp = DAVMultiStatusResponse(request=req)

		el = DAVResponseElement(req, node, props)
		resp.add_element(el)
		resp.make_body()
		req.dav.set_features(resp, node)
		resp.vary = ('Brief', 'Prefer')
		return resp

	def get_props(self, node, prop_root, req):
		req.dav.user_acl(req, node, dprops.ACL_READ) # FIXME: parent
		pdict = dict()
		for prop in prop_root:
			if prop.tag != dprops.PROPERTY:
				continue
			prop_name = prop.get('name')
			if not prop_name:
				continue
			prop_ns = prop.get('namespace', dprops.NS_DAV)
			prop_id = '{%s}%s' % (prop_ns, prop_name)
			pdict[prop_id] = prop

		props = req.dav.get_node_props(req, node, set(pdict))
		if 200 not in props:
			return props
		found_props = props[200]
		if len(found_props) == 0:
			return props
		for fprop in list(found_props):
			fvalue = found_props[fprop]
			if fprop not in pdict:
				continue
			qprop = pdict[fprop]
			if len(qprop) == 0:
				continue
			if not isinstance(fvalue, DAVHrefValue):
				continue
			fnode = fvalue.get_node(req)
			if fnode:
				found_props[fprop] = DAVResponseValue(
					fnode,
					self.get_props(fnode, qprop, req)
				)
		return props

