#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Custom ExtJS columns
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

