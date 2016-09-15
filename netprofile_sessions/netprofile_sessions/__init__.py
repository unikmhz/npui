#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Sessions module
# © Copyright 2013-2016 Alex 'Unik' Unigovsky
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
from netprofile.common.settings import (
	Setting,
	SettingSection
)
from netprofile.tpl import TemplateObject

from sqlalchemy.orm.exc import NoResultFound
from pyramid.i18n import TranslationStringFactory

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

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
	def get_sql_data(cls, modobj, vpair, sess):
		from netprofile_core.models import (
			GlobalSetting,
			Group,
			GroupCapability,
			Privilege
		)

		if not vpair.is_install:
			return

		privs = (
			Privilege(
				code='BASE_SESSIONS',
				name=_('Menu: Sessions')
			),
			Privilege(
				code='SESSIONS_LIST',
				name=_('Sessions: List')
			),
			Privilege(
				code='SESSIONS_LIST_ARCHIVED',
				name=_('Sessions: List archived')
			),
			Privilege(
				code='SESSIONS_DISCONNECT',
				name=_('Sessions: Disconnect')
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

		global_settings = (
			GlobalSetting(name='sessions.acct.interval', value='60'),
			GlobalSetting(name='sessions.acct.stale_cutoff', value='130')
		)
		for gs in global_settings:
			sess.add(gs)

	def get_css(self, request):
		return (
			'netprofile_sessions:static/css/main.css',
		)

	def get_settings(self, vhost='MAIN', scope='global'):
		if vhost == 'MAIN' and scope == 'global':
			return (
				SettingSection(
					'acct',
					Setting(
						'interval',
						title=_('Default accounting interval'),
						help_text=_('Interval (in seconds) between session accounting reports.'),
						type='int',
						default=60,
						write_cap='ADMIN_DB',
						field_extra={ 'minValue' : 20 }
					),
					Setting(
						'stale_cutoff',
						title=_('Inactivity before close'),
						help_text=_('Maximum session inactivity time (in seconds) before it is considered stale and closed down.'),
						type='int',
						default=130,
						write_cap='ADMIN_DB',
						field_extra={ 'minValue' : 45 }
					),
					title=_('Accounting'),
					help_text=_('Client accounting settings.'),
					read_cap='BASE_ADMIN'
				),
			)
		return ()

	@property
	def name(self):
		return _('Sessions')

