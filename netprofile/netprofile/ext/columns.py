#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

class PseudoColumn(object):
	def __init__(self, **kwargs):
		kwargs['nullable'] = bool(kwargs.get('nullable', True))
		kwargs['sortable'] = bool(kwargs.get('sortable', False))
		if 'editor_xtype' not in kwargs:
			kwargs['editor_xtype'] = 'textfield'
		if 'js_type' not in kwargs:
			kwargs['js_type'] = 'auto'
		if 'header_string' not in kwargs:
			kwargs['header_string'] = self.name
		if 'column_name' not in kwargs:
			kwargs['column_name'] = kwargs['header_string']
		kwargs['column_resizable'] = bool(kwargs.get('column_resizable', True))
		if 'filter_type' not in kwargs:
			kwargs['filter_type'] = 'none'
		kwargs['pass_request'] = bool(kwargs.get('pass_request', False))
		kwargs['secret_value'] = bool(kwargs.get('secret_value', False))
		kwargs['read_only'] = bool(kwargs.get('read_only', False))

		self.info = kwargs

	def __getattr__(self, attr):
		return self.info.get(attr)

class HybridColumn(PseudoColumn):
	def __init__(self, pname, **kwargs):
		self.name = pname
		super(HybridColumn, self).__init__(**kwargs)

class MarkupColumn(PseudoColumn):
	def __init__(self, **kwargs):
		self.name = kwargs.get('name')
		super(MarkupColumn, self).__init__(**kwargs)

