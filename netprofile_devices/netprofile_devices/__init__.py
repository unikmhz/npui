#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Devices module
# © Copyright 2013-2014 Alex 'Unik' Unigovsky
# © Copyright 2014 Sergey Dikunov
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


_ = TranslationStringFactory('netprofile_devices')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_devices:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('entities', 'hosts')

	@classmethod
	def get_models(cls):
		from netprofile_devices import models
		return (
			models.DeviceTypeCategory,
			models.DeviceTypeManufacturer,

			models.DeviceTypeFlagType,
			models.DeviceTypeFlag,

			models.DeviceFlagType,
			models.DeviceFlag,

			models.DeviceTypeFile,

			models.DeviceType,
			models.SimpleDeviceType,
			models.NetworkDeviceType,

			models.Device,
			models.SimpleDevice,
			models.NetworkDevice
		)

	@classmethod
	def get_sql_data(cls, modobj, sess):
		from netprofile_devices import models
		from netprofile_core.models import (
			Group,
			GroupCapability,
			LogType,
			Privilege
		)

		sess.add(LogType(
			id=9,
			name='Devices'
		))
		sess.flush()

		privs = (
			Privilege(
				code='BASE_DEVICES',
				name='Access: Devices'
			),
			Privilege(
				code='DEVICES_LIST',
				name='Devices: List'
			),
			Privilege(
				code='DEVICES_CREATE',
				name='Devices: Create'
			),
			Privilege(
				code='DEVICES_EDIT',
				name='Devices: Edit'
			),
			Privilege(
				code='DEVICES_DELETE',
				name='Devices: Delete'
			),
			Privilege(
				code='DEVICES_PASSWORDS',
				name='Devices: Access to passwords'
			),
			Privilege(
				code='FILES_ATTACH_2DEVICETYPES',
				name='Files: Attach to devices'
			),
			Privilege(
				code='DEVICES_FLAGTYPES_CREATE',
				name='Devices: Create flags'
			),
			Privilege(
				code='DEVICES_FLAGTYPES_EDIT',
				name='Devices: Edit flags'
			),
			Privilege(
				code='DEVICES_FLAGTYPES_DELETE',
				name='Devices: Delete flags'
			),

			Privilege(
				code='DEVICETYPES_FLAGTYPES_CREATE',
				name='Devices: Create device type flags'
			),
			Privilege(
				code='DEVICETYPES_FLAGTYPES_EDIT',
				name='Devices: Edit device type flags'
			),
			Privilege(
				code='DEVICETYPES_FLAGTYPES_DELETE',
				name='Devices: Delete device type flags'
			),

			Privilege(
				code='DEVICETYPES_MANUFACTURERS_CREATE',
				name='Devices: Create manufacturers'
			),
			Privilege(
				code='DEVICETYPES_MANUFACTURERS_EDIT',
				name='Devices: Edit manufacturers'
			),
			Privilege(
				code='DEVICETYPES_MANUFACTURERS_DELETE',
				name='Devices: Delete manufacturers'
			),

			Privilege(
				code='DEVICETYPES_LIST',
				name='Devices: List types'
			),
			Privilege(
				code='DEVICETYPES_CREATE',
				name='Devices: Create types'
			),
			Privilege(
				code='DEVICETYPES_EDIT',
				name='Devices: Edit types'
			),
			Privilege(
				code='DEVICETYPES_DELETE',
				name='Devices: Delete types'
			),

			Privilege(
				code='DEVICETYPES_CATEGORIES_CREATE',
				name='Devices: Create categories'
			),
			Privilege(
				code='DEVICETYPES_CATEGORIES_EDIT',
				name='Devices: Edit categories'
			),
			Privilege(
				code='DEVICETYPES_CATEGORIES_DELETE',
				name='Devices: Delete categories'
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

		#TODO sess.add(models.EntityState(
		# 	name='Default',
		# 	description='Default entity state. You can safely rename and/or delete it if you wish.'
		# ))

	#TODO def get_local_js(self, request, lang):
	# 	return (
	# 		'netprofile_devices:static/webshell/locale/webshell-lang-' + lang + '.js',
	# 	)

	def get_css(self, request):
		return (
			'netprofile_devices:static/css/main.css',
		)

	@property
	def name(self):
		return _('Devices')

