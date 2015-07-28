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
from netprofile.db.ddl import AlterTableAlterColumn

from sqlalchemy.orm.exc import NoResultFound
from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_access')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_access:locale/')
		mmgr.cfg.add_route('access.cl.home', '/', vhost='client')
		mmgr.cfg.add_route('access.cl.login', '/login', vhost='client')
		mmgr.cfg.add_route('access.cl.logout', '/logout', vhost='client')
		mmgr.cfg.add_route('access.cl.upload', '/upload', vhost='client')
		mmgr.cfg.add_route('access.cl.download', '/download/{mode}/{id:\d+}', vhost='client')
		mmgr.cfg.add_route('access.cl.register', '/register', vhost='client')
		mmgr.cfg.add_route('access.cl.regsent', '/regsent', vhost='client')
		mmgr.cfg.add_route('access.cl.activate', '/activate', vhost='client')
		mmgr.cfg.add_route('access.cl.restorepass', '/restorepass', vhost='client')
		mmgr.cfg.add_route('access.cl.restoresent', '/restoresent', vhost='client')
		mmgr.cfg.add_route('access.cl.chpass', '/chpass', vhost='client')
		mmgr.cfg.add_route('access.cl.check.nick', '/check/nick', vhost='client')
		mmgr.cfg.add_route('access.cl.robots', '/robots.txt', vhost='client')
		mmgr.cfg.add_route('access.cl.favicon', '/favicon.ico', vhost='client')
		mmgr.cfg.register_block('stashes.cl.block.info', TemplateObject('netprofile_access:templates/client_block_chrate.mak'))
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('stashes', 'rates', 'ipaddresses')

	@classmethod
	def prepare(cls):
		from netprofile_access import models

	@classmethod
	def get_models(cls):
		from netprofile_access import models
		return (
			models.AccessBlock,
			models.AccessEntity,
			models.AccessEntityLink,
			models.AccessEntityLinkType,
			models.PerUserRateModifier
		)

	@classmethod
	def get_sql_functions(cls):
		from netprofile_access import models
		return (
			models.AcctAddProcedure,
			models.AcctAuthzProcedure,
			models.AcctPollProcedure,
			models.AcctRateModsProcedure,
			models.AcctRollbackProcedure,
			models.CheckAuthFunction
		)

	@classmethod
	def get_sql_events(cls):
		from netprofile_access import models
		return (
			models.AccessblockExpireEvent,
			models.AcctPollEvent
		)

	@classmethod
	def get_sql_data(cls, modobj, sess):
		from netprofile_entities.models import Entity
		from netprofile_access import models
		from netprofile_core.models import (
			Group,
			GroupCapability,
			Privilege
		)

		etab = Entity.__table__
		sess.execute(AlterTableAlterColumn(etab, etab.c['etype']))

		privs = (
			Privilege(
				code='ENTITIES_ACCOUNTSTATE_EDIT',
				name='Entities: Edit Account State'
			),
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
			'netprofile_access:static/css/main.css',
		)

	@property
	def name(self):
		return _('Access')

