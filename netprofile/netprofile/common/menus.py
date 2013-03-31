#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from pyramid.threadlocal import get_current_request
from pyramid.i18n import (
	TranslationString,
	get_localizer
)

def _trans_deep(loc, node):
	for k, v in node.items():
		if isinstance(v, TranslationString):
			node[k] = loc.translate(v)
		if isinstance(v, dict):
			_trans_deep(loc, v)

class Menu(object):
	"""
	Defines a single menu pane on the left side of the UI.
	"""
	def __init__(self, name, **kwargs):
		self.name = name
		self.title = kwargs.get('title', name)
		self.order = kwargs.get('order', 10)
		self.perm = kwargs.get('permission')
		self.direct = kwargs.get('direct')
		self.url = kwargs.get('url')
		self.options = kwargs.get('options')

	def get_data(self, req):
		ttl = self.title
		opt = self.options
		ret = {
			'name'    : self.name,
			'title'   : ttl,
			'order'   : self.order,
			'direct'  : self.direct,
			'url'     : self.url,
			'options' : opt
		}
		if req is not None:
			loc = get_localizer(req)
			_trans_deep(loc, ret)
		if self.perm is not None:
			ret['perm'] = self.perm
		return ret

	def json_repr(self):
		return self.get_data(get_current_request())

