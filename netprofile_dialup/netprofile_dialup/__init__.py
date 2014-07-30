#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Dial-Up module
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

_ = TranslationStringFactory('netprofile_dialup')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_dialup:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_models(cls):
		from netprofile_dialup import models
		return (
			models.IPPool,
			models.NAS,
			models.NASPool
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
				code='NAS_LIST',
				name='NASes: List'
			),
			Privilege(
				code='NAS_CREATE',
				name='NASes: Create'
			),
			Privilege(
				code='NAS_EDIT',
				name='NASes: Edit'
			),
			Privilege(
				code='NAS_DELETE',
				name='NASes: Delete'
			),
			Privilege(
				code='IPPOOLS_LIST',
				name='IP Pools: List'
			),
			Privilege(
				code='IPPOOLS_CREATE',
				name='IP Pools: Create'
			),
			Privilege(
				code='IPPOOLS_EDIT',
				name='IP Pools: Edit'
			),
			Privilege(
				code='IPPOOLS_DELETE',
				name='IP Pools: Delete'
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
			'netprofile_dialup:static/css/main.css',
		)

	@property
	def name(self):
		return _('Dial-Up')

