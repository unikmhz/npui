#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: IP addresses module
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

from netprofile.common.modules import ModuleBase

from sqlalchemy.orm.exc import NoResultFound
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_ipaddresses')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_ipaddresses:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('networks', 'dialup')

	@classmethod
	def get_models(cls):
		from netprofile_ipaddresses import models
		return (
			models.IPv4Address,
			models.IPv6Address,
			models.IPv4ReverseZoneSerial,
			models.IPv6ReverseZoneSerial
		)

	@classmethod
	def get_sql_functions(cls):
		from netprofile_ipaddresses import models
		return (
			models.IPAddrGetDotStrFunction,
			models.IPAddrGetOffsetGenFunction,
			models.IPAddrGetOffsetHGFunction,
			models.IP6AddrGetOffsetGenFunction,
			models.IP6AddrGetOffsetHGFunction
		)

	@classmethod
	def get_sql_data(cls, modobj, sess):
		from netprofile_core.models import (
			Group,
			GroupCapability,
			LogType,
			Privilege
		)

		sess.add(LogType(
			id=8,
			name='IPv4 Addresses'
		))
		sess.add(LogType(
			id=19,
			name='IPv6 Addresses'
		))

		privs = (
			Privilege(
				code='BASE_IPADDR',
				name='Access: IP Addresses'
			),
			Privilege(
				code='IPADDR_LIST',
				name='IP Addresses: List'
			),
			Privilege(
				code='IPADDR_CREATE',
				name='IP Addresses: Create'
			),
			Privilege(
				code='IPADDR_EDIT',
				name='IP Addresses: Edit'
			),
			Privilege(
				code='IPADDR_DELETE',
				name='IP Addresses: Delete'
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

	def get_css(self, request):
		return (
			'netprofile_ipaddresses:static/css/main.css',
		)

	@property
	def name(self):
		return _('IP Addresses')

