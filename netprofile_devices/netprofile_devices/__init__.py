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
from pyramid.config import aslist
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_devices')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_devices:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('entities', 'hosts', 'rates')

	@classmethod
	def get_models(cls):
		from netprofile_devices import models
		return (
			models.DeviceClass,

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

			models.NetworkDeviceMediaType,
			models.NetworkDeviceInterface,
			models.NetworkDeviceBinding
		)

	@classmethod
	def get_sql_data(cls, modobj, vpair, sess):
		from netprofile_devices import models
		from netprofile_core.models import (
			Group,
			GroupCapability,
			LogType,
			Privilege
		)

		if not vpair.is_install:
			return

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
			),
			Privilege(
				code='HOSTS_PROBE',
				name='Devices: Probe hosts'
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

		classes = (
			models.DeviceClass(
				id=1,
				name=_('Simple'),
				model='SimpleDevice',
				long_name=_('Simple Device'),
				plural=_('Simple Devices'),
				description=_('Non-networking equipment.')
			),
			models.DeviceClass(
				id=2,
				name=_('Network'),
				model='NetworkDevice',
				long_name=_('Network Device'),
				plural=_('Network Devices'),
				description=_('Networking equipment.')
			)
		)
		for dcls in classes:
			dcls.module = modobj
			sess.add(dcls)

		medias = (
			# Name,                             ifT, ifTA, Physical, Speed,       Description
			(_('Other'),                        1,   None, False,    None,        'Other'),
			('BBN 1822 Regular',                2,   None, True,     None,        'BBN Report 1822 regular connection'),
			('BBN 1822 HDH',                    3,   None, True,     None,        'BBN Report 1822 HDH sync serial'),
			('DDN X.25',                        4,   None, True,     None,        'Defence Data Network X.25'),
			('RFC877 X.25',                     5,   None, True,     None,        'RFC877 IP over X.25'),
			('IEEE 802.3a 10Base2',             6,   7,    True,     10000000,    '10Base2 Ethernet over 50-ohm thin coax'),
			('IEEE 802.3b 10Broad36',           6,   7,    True,     10000000,    '10Broad36 Ethernet over 75-ohm CATV coax'),
			('IEEE 802.3e 10Base5',             6,   7,    True,     10000000,    '10Base5 Ethernet over 50-ohm thick coax'),
			('IEEE 802.3i 10BaseT',             6,   7,    True,     10000000,    '10BaseT Ethernet over cat3 2-twisted-pair cable'),
			('IEEE 802.3j 10BaseFL',            6,   7,    True,     10000000,    '10BaseFL Ethernet over multi-mode fiber pair'),
			('IEEE 802.3u 100Base-TX',          6,   62,   True,     100000000,   '100Base-TX Ethernet over cat5 2-twisted-pair cable'),
			('IEEE 802.3u 100Base-T4',          6,   62,   True,     100000000,   '100Base-T4 Ethernet over cat3 4-twisted-pair cable'),
			('IEEE 802.3u 100Base-FX',          6,   69,   True,     100000000,   '100Base-FX Ethernet over single-/multi-mode fiber pair'),
			('IEEE 802.3y 100Base-T2',          6,   62,   True,     100000000,   '100Base-T2 Ethernet over cat3 2-twisted-pair cable'),
			('Ethernet 100Base-SX',             6,   69,   True,     100000000,   '100Base-SX Ethernet over multi-mode fiber pair'),
			('Ethernet 100Base-BX',             6,   69,   True,     100000000,   '100Base-BX Ethernet over one single-mode fiber'),
			('IEEE 802.3ah 100Base-LX10',       6,   69,   True,     100000000,   '100Base-LX Ethernet over single-mode fiber pair'),
			('IEEE 802.3z 1000Base-LX',         6,   117,  True,     1000000000,  '1000Base-X Ethernet over single-/multi-mode fiber pair'),
			('IEEE 802.3ah 1000Base-LX10',      6,   117,  True,     1000000000,  '1000Base-X Ethernet over single-mode fiber pair (1000Base-LH)'),
			('IEEE 802.3ah 1000Base-BX10',      6,   117,  True,     1000000000,  '1000Base-X Ethernet over one single-mode fiber'),
			('IEEE 802.3z 1000Base-SX',         6,   117,  True,     1000000000,  '1000Base-X Ethernet over multi-mode fiber pair'),
			('IEEE 802.3z 1000Base-CX',         6,   117,  True,     1000000000,  '1000Base-X Ethernet over 150-ohm balanced STP cable'),
			('IEEE 802.3ab 1000Base-T',         6,   117,  True,     1000000000,  '1000Base-T Ethernet over cat5/5e 4-twisted-pair cable'),
			('Ethernet 1000Base-EX',            6,   117,  True,     1000000000,  '1000Base-X Ethernet over single-mode fiber pair (1000Base-LH)'),
			('Ethernet 1000Base-ZX',            6,   117,  True,     1000000000,  '1000Base-X Ethernet over single-mode fiber pair (1000Base-LH)'),
			('IEEE 802.3ae 10GBase-SR',         6,   None, True,     10000000000, '10GBase-SR Ethernet over multi-mode fiber pair (LAN PHY)'),
			('IEEE 802.3ae 10GBase-LR',         6,   None, True,     10000000000, '10GBase-LR Ethernet over single-mode fiber pair (LAN PHY)'),
			('IEEE 802.3ae 10GBase-ER',         6,   None, True,     10000000000, '10GBase-ER Ethernet over single-mode fiber pair (LAN PHY)'),
			('IEEE 802.3ae 10GBase-SW',         6,   None, True,     10000000000, '10GBase-SW Ethernet over multi-mode fiber pair (WAN PHY)'),
			('IEEE 802.3ae 10GBase-LW',         6,   None, True,     10000000000, '10GBase-LW Ethernet over single-mode fiber pair (WAN PHY)'),
			('IEEE 802.3ae 10GBase-EW',         6,   None, True,     10000000000, '10GBase-EW Ethernet over single-mode fiber pair (WAN PHY)'),
			('Ethernet 10GBase-ZR',             6,   None, True,     10000000000, '10GBase-ZR Ethernet over single-mode fiber pair (LAN PHY)'),
			('Ethernet 10GBase-ZW',             6,   None, True,     10000000000, '10GBase-ZW Ethernet over single-mode fiber pair (WAN PHY)'),
			('IEEE 802.3ak 10GBase-CX4',        6,   None, True,     10000000000, '10GBase-CX4 Ethernet over twinaxial 8-pair cable'),
			('IEEE 802.3an 10GBase-T',          6,   None, True,     10000000000, '10GBase-T Ethernet over cat6/6a 4-twisted-pair cable'),
			('IEEE 802.3aq 10GBase-LRM',        6,   None, True,     10000000000, '10GBase-LR Ethernet over multi-mode fiber pair'),
			('IEEE 802.4 Token Bus',            8,   None, True,     20000000,    'Token Bus over OnB'),
			('IEEE 802.5 Token Ring',           9,   None, True,     16000000,    'Token Ring'),
			('IEEE 802.6 MAN DQDB',             10,  None, True,     150000000,   'Metropolitan Area Network over DQDB'),
			# 11-14
			('FDDI',                            15,  None, True,     100000000,   'Fiber Distributed Data Interface'),
			('LAPB',                            16,  None, True,     None,        'Link Access Procedure, Balanced (ITU-T X.25, ISO/IEC 7776)'),
			('SDLC',                            17,  None, False,    None,        'Synchronous Data Link Control (IBM SNA)'),
			('ITU-T G.703 DS1',                 18,  19,   True,     1544000,     'DS1 carrier (ITU-T G.703)'),
			('ITU-T G.703 J1',                  18,  19,   True,     1544000,     'J1 carrier (ITU-T G.703)'),
			('ITU-T G.703 E1',                  18,  19,   True,     2048000,     'E1 carrier (ITU-T G.703)'),
			('ITU-T G.703 DS2',                 18,  19,   True,     6312000,     'DS2 carrier (ITU-T G.703)'),
			('ITU-T G.703 E2',                  18,  19,   True,     8448000,     'E2 carrier (ITU-T G.703)'),
			('I.430 ISDN BRI',                  20,  None, True,     16000,       'I.430 ISDN Basic Rate Interface'),
			('I.431 ISDN PRI',                  21,  None, True,     64000,       'I.431 ISDN Primary Rate Interface'),
			(_('P2P Serial'),                   22,  None, True,     None,        'Proprietary peer-to-peer serial'),
			('PPP',                             23,  None, False,    None,        'Point-to-Point Protocol (RFC 1661)'),
			(_('Loopback'),                     24,  None, False,    None,        'Software loopback'),
			# 25-27
			('SLIP',                            28,  None, False,    None,        'Serial Line Internet Protocol'),
			# 29
			('ITU-T G.751 DS3',                 30,  None, True,     44736000,    'DS3 carrier (ITU-T G.751)'),
			('ITU-T G.751 E3',                  30,  None, True,     34368000,    'E3 carrier (ITU-T G.751)'),
			# 31
			('Frame Relay DTE',                 32,  None, True,     None,        'Frame Relay DTE'),
			('RS-232',                          33,  None, True,     None,        'RS-232 serial interface'),
			('IEEE 1284 ParPort',               34,  None, True,     None,        'IEEE 1284 parallel port interface (LPT)'),
			('ARCnet',                          35,  None, True,     2500000,     'Attached Resource Computer NETwork'),
			('ARCnet Plus',                     36,  None, True,     20000000,    'Attached Resource Computer NETwork Plus'),
			# 37-38
			('SONET/SDH OC-3/STM-1',            39,  None, True,     155520000,   'Synchronous Optical Networking / Synchronous Digital Hierarchy optical carrier 3'),
			('SONET/SDH OC-12/STM-4',           39,  None, True,     622080000,   'Synchronous Optical Networking / Synchronous Digital Hierarchy optical carrier 12'),
			('SONET/SDH OC-24/STM-8',           39,  None, True,     1244160000,  'Synchronous Optical Networking / Synchronous Digital Hierarchy optical carrier 24'),
			('SONET/SDH OC-48/STM-16',          39,  None, True,     2488320000,  'Synchronous Optical Networking / Synchronous Digital Hierarchy optical carrier 48'),
			('SONET/SDH OC-96/STM-32',          39,  None, True,     4976640000,  'Synchronous Optical Networking / Synchronous Digital Hierarchy optical carrier 96'),
			('SONET/SDH OC-192/STM-64',         39,  None, True,     9953280000,  'Synchronous Optical Networking / Synchronous Digital Hierarchy optical carrier 192'),
			('SONET/SDH OC-768/STM-256',        39,  None, True,     39813120000, 'Synchronous Optical Networking / Synchronous Digital Hierarchy optical carrier 768'),
			('SONET/SDH OC-1536/STM-512',       39,  None, True,     79626240000, 'Synchronous Optical Networking / Synchronous Digital Hierarchy optical carrier 1536'),
			('X.25 PLE',                        40,  None, False,    None,        'X.25 Packet Level Entity'),
			('IEEE 802.2 LLC',                  41,  None, False,    None,        'IEEE 802.2 Logical Link Control'),
			# 42-44
			('V.35',                            45,  None, True,     None,        'ITU-T V.35 wideband'),
			('HSSI',                            46,  None, True,     None,        'High-Speed Serial Interface (EIA-612, EIA-613)'),
			('HIPPI-800',                       47,  None, True,     800000000,   'High-Performance Parallel Interface 800Mbps'),
			('HIPPI-1600',                      47,  None, True,     1600000000,  'High-Performance Parallel Interface 1600Mbps'),
			('HIPPI-6400',                      47,  145,  True,     6400000000,  'High-Performance Parallel Interface 6400Mbps (GSN)'),
			(_('Generic modem'),                48,  None, True,     None,        'Generic modem interface'),
			# 49-52
			(_('Proprietary virtual/internal'), 53,  None, False,    None,        'Non-standard proprietary virtual/internal interface'),
			(_('Proprietary multiplexing'),     54,  None, False,    None,        'Non-standard proprietary multiplexing interface'),
			('IEEE 802.12 100BaseVG',           55,  None, True,     100000000,   '100BaseVG Ethernet over cat3 4-twisted-pair cable (voice grade)'),
			('Fibre Channel',                   56,  None, True,     None,        'Fibre Channel'),
			# 57 - hippi again?
			# 58-72
			('IBM ESCON',                       73,  None, True,     None,        'IBM Enterprise Systems Connection'),
			# 74-93
			('ADSL',                            94,  None, True,     None,        'Asymmetric Digital Subscriber Line (ITU-T G.992)'),
			('RADSL',                           95,  None, True,     None,        'Rate-Adaptive Digital Subscriber Line (ANSI T1.TR.59)'),
			('SDSL',                            96,  None, True,     None,        'Symmetric Digital Subscriber Line'),
			('VDSL',                            97,  None, True,     None,        'Very-high-data-rate Digital Subscriber Line (ITU-T G.993.1)'),
			# 98
			('Myrinet',                         99,  None, True,     None,        'Myricom Myrinet (ANSI/VITA 26-1998)'),
			# 100-117
			('HDLC',                            118, None, False,    None,        'High-Level Data Link Control (ISO/IEC 13239)'),
			# 119-130
			(_('Tunnel'),                       131, None, False,    None,        'Encapsulation interface'),
			# 132-133
			(_('ATM Sub Interface'),            134, None, False,    None,        'ATM sub interface'),
			('L2 802.1Q VLAN',                  135, None, False,    None,        'Layer 2 Virtual LAN using IEEE 802.1Q'),
			('L3 IP VLAN',                      136, None, False,    None,        'Layer 3 Virtual LAN using IP'),
			('L3 IPX VLAN',                     137, None, False,    None,        'Layer 3 Virtual LAN using IPX'),
			(_('IP over Power Line'),           138, None, True,     None,        'IP over power lines'),
			# 139-141
			(_('IP Forward'),                   142, None, False,    None,        'IP forwarding interface'),
			# 143
			('IEEE 1394 Firewire',              144, None, True,     None,        'IEEE 1394 High Performance Serial Bus (Firewire / i.LINK / Lynx)'),
			# 146-148
			(_('ATM Virtual'),                  149, None, False,    None,        'ATM virtual interface'),
			(_('MPLS Tunnel'),                  150, None, False,    None,        'MPLS tunnel virtual interface'),
			# 151
			('VoATM',                           152, None, False,    None,        'Voice over ATM'),
			('VoFR',                            153, None, False,    None,        'Voice over Frame Relay'),
			('IDSL',                            154, None, False,    None,        'Digital Subscriber Line over ISDN (ANSI T1.418)'),
			# 155
			(_('SS7 Signaling'),                156, None, False,    None,        'SS7 signaling link'),
			(_('Proprietary P2P wireless'),     157, None, True,     None,        'Non-standard proprietary peer-to-peer wireless interface'),
			# 158-159
			('USB',                             160, None, True,     None,        'Universal Serial Bus interface'),
			('IEEE 802.3ad LAG',                161, None, False,    None,        'IEEE 802.3ad Link Aggregation Group'),
			# 162-165
			('MPLS',                            166, None, False,    None,        'Multiprotocol Label Switching'),
			# 167
			('HDSL2 (T1)',                      168, None, True,     1552000,     'High bit rate Digital Subscriber Line 2 over T1 (ANSI T1.418)'),
			('HDSL2 (E1)',                      168, None, True,     2048000,     'High bit rate Digital Subscriber Line 2 over E1 (ANSI T1.418)'),
			('SHDSL',                           169, None, True,     None,        'Single-pair High-speed Digital Subscriber Line (ITU-T G.991.2)'),
			# 170
			('POS',                             171, None, False,    None,        'Packet over SONET/SDH'),
			# 172-173
			('PowerLine',                       174, None, True,     None,        'Power Line Communications'),
			# 175-198
			('InfiniBand',                      199, None, True,     None,        'InfiniBand'),
			# 200-205
			('Acorn Econet',                    206, None, True,     None,        'Acorn Econet'),
			# 207-208
			(_('Bridge'),                       209, None, False,    None,        'Transparent bridge interface'),
			# 210-219
			('HomePNA',                         220, None, True,     None,        'HomePNA (ITU-T G.9951 through G.9954)'),
			# 221
			('L2 ISL VLAN',                     222, None, False,    None,        'Layer 2 Virtual LAN using Cisco ISL'),
			# 223-229
			('ADSL2',                           230, None, True,     None,        'Asymmetric Digital Subscriber Line 2 (ITU-T G.992.3)'),
			# 231-237
			('ADSL2+',                          238, None, True,     None,        'Asymmetric Digital Subscriber Line 2+ (ITU-T G.992.5)'),
			# 239-249
			('G-PON',                           250, None, True,     None,        'Gigabit-capable Passive Optical Network (ITU-T G.984.1)'),
			('VDSL2',                           251, None, True,     None,        'Very-high-data-rate Digital Subscriber Line 2 (ITU-T G.993.2)'),
			# 252-278
			('G.fast',                          279, None, True,     None,        'G.fast Digital Subscriber Line (ITU-T G.9700, ITU-T G.9701)')
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

		mibs = ('IF-MIB', 'BRIDGE-MIB', 'P-BRIDGE-MIB', 'Q-BRIDGE-MIB', 'IP-MIB', 'LLDP-MIB')

		for mib in mibs:
			sess.add(models.DeviceTypeFlagType(
				name='SNMP: %s' % (mib,),
				description='Support for %s SNMP values and tables' % (mib,)
			))

	def get_local_js(self, request, lang):
		return (
			'netprofile_devices:static/webshell/locale/webshell-lang-' + lang + '.js',
		)

	def get_css(self, request):
		return (
			'netprofile_devices:static/css/main.css',
		)

	def get_task_imports(self):
		return (
			'netprofile_devices.tasks',
		)

	def get_controllers(self, request):
		return (
			'NetProfile.devices.controller.HostProbe',
		)

	@property
	def name(self):
		return _('Devices')

def includeme(config):
	"""
	For inclusion by Pyramid.
	"""
	mib_paths = []
	cfg = config.registry.settings

	# Add user-configured MIB paths
	if 'netprofile.devices.mib_paths' in cfg:
		for path in aslist(cfg['netprofile.devices.mib_paths']):
			if os.path.isdir(path):
				mib_paths.append(path)

	# Add path to bundles MIBs
	dist = pkg_resources.get_distribution('netprofile_devices')
	if dist:
		new_path = os.path.join(dist.location, 'netprofile_devices', 'mibs')
		if os.path.isdir(new_path):
			mib_paths.append(new_path)

	if len(mib_paths) > 0:
		cur_path = snimpy.mib.path()
		snimpy.mib.path(':'.join(mib_paths) + ':' + cur_path)

