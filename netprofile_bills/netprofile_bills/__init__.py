#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Bills module
# © Copyright 2017 Alex 'Unik' Unigovsky
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

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

_ = TranslationStringFactory('netprofile_bills')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_bills:locale/')

	@classmethod
	def get_deps(cls):
		return ('stashes', 'documents')

	@classmethod
	def get_models(cls):
		from netprofile_bills import models
		return (
			models.Bill,
			models.BillType,
			models.BillSerial
		)

	@classmethod
	def get_sql_data(cls, modobj, vpair, sess):
		from netprofile_core.models import (
			Group,
			GroupCapability,
			LogType,
			Privilege
		)

		if not vpair.is_install:
			return

		sess.add(LogType(
			id=15,
			name='Bills'
		))
		sess.flush()

		privs = (
			Privilege(
				code='BASE_BILLS',
				name=_('Menu: Bills')
			),
			Privilege(
				code='BILLS_LIST',
				name=_('Bills: List')
			),
			Privilege(
				code='BILLS_CREATE',
				name=_('Bills: Create')
			),
			Privilege(
				code='BILLS_EDIT',
				name=_('Bills: Edit')
			),
			Privilege(
				code='BILLS_DELETE',
				name=_('Bills: Delete')
			),
			Privilege(
				code='BILLS_OPS',
				name=_('Bills: Operations')
			),
			Privilege(
				code='BILLS_TYPES_CREATE',
				name=_('Bills: Create types')
			),
			Privilege(
				code='BILLS_TYPES_EDIT',
				name=_('Bills: Edit types')
			),
			Privilege(
				code='BILLS_TYPES_DELETE',
				name=_('Bills: Delete types')
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
			'netprofile_bills:static/css/main.css',
		)

	@property
	def name(self):
		return _('Bills')

