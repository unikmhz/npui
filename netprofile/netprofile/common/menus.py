#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: UI menu setup and handling
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

from pyramid.threadlocal import get_current_request
from pyramid.i18n import get_localizer

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
		self.extra_fields = kwargs.get('extra_fields', ())
		self.custom_root = kwargs.get('custom_root')

	def get_data(self):
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
		if self.perm is not None:
			ret['perm'] = self.perm
		return ret

	def __json__(self, req=None):
		return self.get_data()

