#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Networks module
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

_ = TranslationStringFactory('netprofile_networks')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_networks:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('hosts',)

	@classmethod
	def get_models(cls):
		from netprofile_networks import models
		return (
			models.Network,
			models.NetworkGroup,
			models.NetworkService,
			models.NetworkServiceType,
			models.RoutingTable,
			models.RoutingTableEntry
		)

	@classmethod
	def get_sql_data(cls, modobj, sess):
		from netprofile_networks.models import NetworkServiceType
		from netprofile_core.models import (
			Group,
			GroupCapability,
			LogType,
			Privilege
		)

		sess.add(LogType(
			id=6,
			name='Networks'
		))

		privs = (
			Privilege(
				code='BASE_NETS',
				name='Access: Networks'
			),
			Privilege(
				code='NETS_LIST',
				name='Networks: List'
			),
			Privilege(
				code='NETS_CREATE',
				name='Networks: Create'
			),
			Privilege(
				code='NETS_EDIT',
				name='Networks: Edit'
			),
			Privilege(
				code='NETS_DELETE',
				name='Networks: Delete'
			),
			Privilege(
				code='NETGROUPS_CREATE',
				name='Networks: Create groups'
			),
			Privilege(
				code='NETGROUPS_EDIT',
				name='Networks: Edit groups'
			),
			Privilege(
				code='NETGROUPS_DELETE',
				name='Networks: Delete groups'
			),
			Privilege(
				code='NETS_SERVICETYPES_CREATE',
				name='Networks: Create service types'
			),
			Privilege(
				code='NETS_SERVICETYPES_EDIT',
				name='Networks: Edit service types'
			),
			Privilege(
				code='NETS_SERVICETYPES_DELETE',
				name='Networks: Delete service types'
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

		nstypes = (
			models.NetworkServiceType(
				id=1,
				name='Name Server'
			),
			models.NetworkServiceType(
				id=2,
				name='WINS Server'
			),
			models.NetworkServiceType(
				id=3,
				name='NTP Server'
			),
			models.NetworkServiceType(
				id=4,
				name='Gateway'
			),
			models.NetworkServiceType(
				id=5,
				name='SLP DA Server'
			),
			models.NetworkServiceType(
				id=6,
				name='DNSv6 Server'
			)
		)

		for nst in nstypes:
			sess.add(nst)
	
	def get_css(self, request):
		return (
			'netprofile_networks:static/css/main.css',
		)

	@property
	def name(self):
		return _('Networks')

