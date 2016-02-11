#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Devices module
# © Copyright 2013-2016 Alex 'Unik' Unigovsky
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

import os
import pkg_resources
import snimpy.mib

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
			models.NetworkDevice,

			models.NetworkDeviceMediaType
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

		medias = (
			# Name,                        ifT, ifTA, Physical, Speed,       Description
			(_('Other'),                   1,   None, False,    None,        'None of the following'),
			(_('BBN 1822 Regular'),        2,   None, True,     None,        'BBN Report 1822 regular connection'),
			(_('BBN 1822 HDH'),            3,   None, True,     None,        'BBN Report 1822 HDH sync serial'),
			('DDN X.25',                   4,   None, True,     None,        'Defence Data Network X.25'),
			('RFC877 X.25',                5,   None, True,     None,        'RFC877 IP over X.25'),
			('IEEE 802.3a 10Base2',        6,   7,    True,     10000000,    '10Base2 Ethernet over 50-ohm thin coax'),
			('IEEE 802.3b 10Broad36',      6,   7,    True,     10000000,    '10Broad36 Ethernet over 75-ohm CATV coax'),
			('IEEE 802.3e 10Base5',        6,   7,    True,     10000000,    '10Base5 Ethernet over 50-ohm thick coax'),
			('IEEE 802.3i 10BaseT',        6,   7,    True,     10000000,    '10BaseT Ethernet over cat3 2-twisted-pair cable'),
			('IEEE 802.3j 10BaseFL',       6,   7,    True,     10000000,    '10BaseFL Ethernet over multi-mode fiber pair'),
			('IEEE 802.3u 100Base-TX',     6,   62,   True,     100000000,   '100Base-TX Ethernet over cat5 2-twisted-pair cable'),
			('IEEE 802.3u 100Base-T4',     6,   62,   True,     100000000,   '100Base-T4 Ethernet over cat3 4-twisted-pair cable'),
			('IEEE 802.3u 100Base-FX',     6,   69,   True,     100000000,   '100Base-FX Ethernet over single-/multi-mode fiber pair'),
			('IEEE 802.3y 100Base-T2',     6,   62,   True,     100000000,   '100Base-T2 Ethernet over cat3 2-twisted-pair cable'),
			('Ethernet 100Base-SX',        6,   69,   True,     100000000,   '100Base-SX Ethernet over multi-mode fiber pair'),
			('Ethernet 100Base-BX',        6,   69,   True,     100000000,   '100Base-BX Ethernet over one single-mode fiber'),
			('IEEE 802.3ah 100Base-LX10',  6,   69,   True,     100000000,   '100Base-LX Ethernet over single-mode fiber pair'),
			('IEEE 802.3z 1000Base-LX',    6,   117,  True,     1000000000,  '1000Base-X Ethernet over single-/multi-mode fiber pair'),
			('IEEE 802.3ah 1000Base-LX10', 6,   117,  True,     1000000000,  '1000Base-X Ethernet over single-mode fiber pair (1000Base-LH)'),
			('IEEE 802.3z 1000Base-SX',    6,   117,  True,     1000000000,  '1000Base-X Ethernet over multi-mode fiber pair'),
			('IEEE 802.3z 1000Base-CX',    6,   117,  True,     1000000000,  '1000Base-X Ethernet over 150-ohm balanced STP cable'),
			('IEEE 802.3ab 1000Base-T',    6,   117,  True,     1000000000,  '1000Base-T Ethernet over cat5/5e 4-twisted-pair cable'),
		)
		for mdata in medias:
			media = models.NetworkDeviceMediaType(
				name=mdata[0],
				iftype=mdata[1],
				iftype_alternate=mdata[2],
				is_physical=mdata[3],
				speed=mdata[4],
				description=mdata[5]
			)
			sess.add(media)

	def get_css(self, request):
		return (
			'netprofile_devices:static/css/main.css',
		)

	@property
	def name(self):
		return _('Devices')

def includeme(config):
	"""
	For inclusion by Pyramid.
	"""
	dist = pkg_resources.get_distribution('netprofile_devices')
	if dist:
		new_path = os.path.join(dist.location, 'netprofile_devices', 'mibs')
		if os.path.isdir(new_path):
			cur_path = snimpy.mib.path()
			snimpy.mib.path(new_path + ':' + cur_path)

