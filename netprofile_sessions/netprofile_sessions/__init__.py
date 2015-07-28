#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Access module
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
from netprofile.tpl import TemplateObject

from sqlalchemy.orm.exc import NoResultFound
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_sessions')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_sessions:locale/')
		mmgr.cfg.register_block('stashes.cl.block.entity_menu', TemplateObject('netprofile_sessions:templates/client_block_sessions.mak'))
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('access',)

	@classmethod
	def get_models(cls):
		from netprofile_sessions import models
		return (
			models.AccessSession,
			models.AccessSessionHistory
		)

	@classmethod
	def get_sql_functions(cls):
		from netprofile_sessions import models
		return (
			models.AcctAddSessionProcedure,
			models.AcctAllocIPProcedure,
			models.AcctAllocIPv6Procedure,
			models.AcctAuthzSessionProcedure,
			models.AcctCloseSessionProcedure,
			models.AcctOpenSessionProcedure
		)

	@classmethod
	def get_sql_events(cls):
		from netprofile_sessions import models
		return (
			models.IPAddrClearStaleEvent,
			models.SessionsClearStaleEvent
		)

	@classmethod
	def get_sql_data(cls, modobj, sess):
		from netprofile_core.models import (
			GlobalSetting,
			GlobalSettingSection,
			Group,
			GroupCapability,
			Privilege
		)

		privs = (
			Privilege(
				code='BASE_SESSIONS',
				name='Access: Sessions'
			),
			Privilege(
				code='SESSIONS_LIST',
				name='Sessions: List'
			),
			Privilege(
				code='SESSIONS_LIST_ARCHIVED',
				name='Sessions: List archived'
			),
			Privilege(
				code='SESSIONS_DISCONNECT',
				name='Sessions: Disconnect'
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

		gss_acct = GlobalSettingSection( # no old id
			module=modobj,
			name='Accounting',
			description='Client accounting settings.'
		)

		sess.add(gss_acct)

		sess.add(GlobalSetting(
			section=gss_acct,
			module=modobj,
			name='acct_interval',
			title='Default accounting interval',
			type='text',
			value='60',
			default='60',
			constraints={
				'cast'   : 'int',
				'nullok' : False,
				'minval' : 20
			},
			description='Interval (in seconds) between session accounting reports.'
		))
		sess.add(GlobalSetting(
			section=gss_acct,
			module=modobj,
			name='acct_stale_cutoff',
			title='Inactivity before close',
			type='text',
			value='130',
			default='130',
			constraints={
				'cast'   : 'int',
				'nullok' : False,
				'minval' : 45
			},
			description='Maximum session inactivity time (in seconds) before it is considered stale and closed down.'
		))

	def get_css(self, request):
		return (
			'netprofile_sessions:static/css/main.css',
		)

	@property
	def name(self):
		return _('Sessions')

