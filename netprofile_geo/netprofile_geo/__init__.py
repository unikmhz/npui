#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Geo module
# © Copyright 2013 Nikita Andriyanov
# © Copyright 2013-2014 Alex 'Unik' Unigovsky
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

from netprofile.common.modules import ModuleBase

from sqlalchemy.orm.exc import NoResultFound
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_geo')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_geo:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_models(cls):
		from netprofile_geo import models
		return (
			models.City,
			models.District,
			models.Street,
			models.House,
			models.Place,
			models.HouseGroup,
			models.HouseGroupMapping
		)

	@classmethod
	def get_sql_functions(cls):
		from netprofile_geo import models
		return (
			models.AddrFormatCompactFunction,
			models.AddrFormatFunction,
			models.AddrGetFullFunction,
			models.AddrListDistrictProcedure,
			models.AddrListEntrProcedure,
			models.AddrListStreetProcedure
		)

	@classmethod
	def get_sql_views(cls):
		from netprofile_geo import models
		return (
			models.AddrCompactView,
			models.AddrExtraView,
			models.AddrFullView,
			models.AddrStreetNamesView
		)

	@classmethod
	def get_sql_data(cls, modobj, sess):
		from netprofile_core.models import (
			Group,
			GroupCapability,
			Privilege
		)

		privs = (
			Privilege(
				code='BASE_GEO',
				name='Access: Addresses'
			),
			Privilege(
				code='GEO_LIST',
				name='Addresses: List'
			),
			Privilege(
				code='GEO_CREATE',
				name='Addresses: Create'
			),
			Privilege(
				code='GEO_EDIT',
				name='Addresses: Edit'
			),
			Privilege(
				code='GEO_DELETE',
				name='Addresses: Delete'
			)
		)
		for priv in privs:
			priv.module = modobj
			sess.add(priv)
		try:
			grp_admins = sess.query(Group).filter(Group.name == 'Administrators').one()
			for priv in privs:
				cap = GroupCapability()
				cap.group = grp_admins
				cap.privilege = priv
		except NoResultFound:
			pass

	def get_local_js(self, request, lang):
		return (
			'netprofile_geo:static/webshell/locale/webshell-lang-' + lang + '.js',
		)

	def get_autoload_js(self, request):
		return (
			'NetProfile.geo.form.field.Address',
		)

	def get_css(self, request):
		return (
			'netprofile_geo:static/css/main.css',
		)

	@property
	def name(self):
		return _('Geography')

