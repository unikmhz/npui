#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Cache setup
# © Copyright 2016 Alex 'Unik' Unigovsky
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
	'Setting',
	'SettingSection'
]

from sqlalchemy.orm.exc import NoResultFound
from netprofile.common.cache import cache
from netprofile.db.connection import DBSession

class SettingSection(object):
	def __init__(self, name, *settings, vhost='MAIN', scope='global', title=None, read_cap=None, help_text=None):
		self.name = name
		self.settings = dict((setting.name, setting) for setting in settings)
		self.vhost = vhost
		self.scope = scope
		self.title = title
		self.read_cap = read_cap
		self.help_text = help_text

	def __iter__(self):
		return iter(self.settings)

	def __getitem__(self, name):
		return self.settings[name]

	def get_tree_cfg(self, req, moddef):
		if self.read_cap and not req.has_permission(self.read_cap):
			return None
		loc = req.localizer
		ret = {
			'id'      : '.'.join((moddef, self.name)),
			'text'    : loc.translate(self.title) if self.title else self.name,
			'leaf'    : True,
			'iconCls' : 'ico-cog'
		}
		return ret

	def get_form_cfg(self, req, moddef):
		if self.read_cap and not req.has_permission(self.read_cap):
			return None
		fields = []
		for setting in settings:
			fld = setting.get_form_cfg(req, moddef, self)
			if fld:
				fields.append(fld)
		return {
			'success' : True,
			'fields'  : fields,
			'section' : {
				'id'    : '.'.join((moddef, self.name)),
				'name'  : loc.translate(self.title) if self.title else self.name,
				'descr' : loc.translate(self.help_text) if self.help_text else None
			}
		}

class Setting(object):
	def __init__(self, name, title=None, type='string', pass_to_client=True,
			read_cap=None, write_cap=None, default=None, help_text=None,
			field_cfg=None, field_extra=None, nullable=False):
		self.name = name
		self.title = title
		self.type = type
		self.client_ok = pass_to_client
		self.read_cap = read_cap
		self.write_cap = write_cap
		self.default = default
		self.help_text = help_text
		self.nullable = nullable

		if field_cfg is None:
			if self.type == 'bool':
				field_cfg = self.field_bool
			else:
				raise ValueError('Unrecognized setting type: \'%s\'.' % (self.type,))

		self.field_cfg = field_cfg
		self.field_extra = field_extra

	def field_bool(self, req, moddef, section):
		return {
			'xtype'          : 'checkbox',
			'inputValue'     : 'true',
			'uncheckedValue' : 'false'
		}

	def field_int(self, req, moddef, section):
		return {
			'xtype'         : 'numberfield',
			'allowDecimals' : False
		}

	def get_form_cfg(self, req, moddef, section):
		if self.read_cap and not req.has_permission(self.read_cap):
			return None
		field_name = '.'.join((moddef, section.name, self.name))
		loc = req.localizer
		if callable(self.field_cfg):
			cfg = self.field_cfg(req, moddef, section)
		else:
			cfg = self.field_cfg.copy()
		cfg.update({
			'name'        : field_name,
			'fieldLabel'  : loc.translate(self.title) if self.title else self.name,
			'description' : loc.translate(self.help_text) if self.help_text else None
		})
		extra = self.field_extra
		if extra:
			if callable(extra):
				extra = extra(req, moddef, section)
			cfg.update(extra)
		return cfg

