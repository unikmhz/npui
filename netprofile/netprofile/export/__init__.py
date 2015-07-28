#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Data export support
# © Copyright 2015 Alex 'Unik' Unigovsky
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

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile')

class ExportFormat(object):
	"""
	Base class for export formats.
	"""
	@property
	def name(self):
		pass

	@property
	def icon(self):
		pass

	def enabled(self, req):
		return True

	def options(self, req, name):
		return ()

	def export(self, extm, params, req):
		pass

	def export_panel(self, req, name):
		loc = get_localizer(req)
		opt = self.options(req, name)
		return {
			'title'         : loc.translate(self.name),
			'iconCls'       : self.icon,
			'xtype'         : 'form',
			'itemId'        : name,
			'bodyPadding'   : 5,
			'border'        : 0,
			'layout'        : 'anchor',
			'defaults'      : {
				'anchor' : '100%'
			},
			'fieldDefaults' : {
				'labelAlign' : 'left',
				'msgTarget'  : 'side'
			},
			'items'         : opt,
			'buttons'       : ({
				'cls'     : 'np-data-export',
				'iconCls' : 'ico-save',
				'xtype'   : 'button',
				'text'    : loc.translate(_('Export'))
			},)
		}

