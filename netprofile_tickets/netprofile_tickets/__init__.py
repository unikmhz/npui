#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Tickets module
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

_ = TranslationStringFactory('netprofile_tickets')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_route(
			'tickets.cl.issues',
			'/issues/*traverse',
			factory='netprofile_tickets.views.ClientRootFactory',
			vhost='client'
		)
		mmgr.cfg.add_translation_dirs('netprofile_tickets:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('entities',)

	@classmethod
	def get_models(cls):
		from netprofile_tickets import models
		return (
			models.Ticket,
			models.TicketChange,
			models.TicketChangeBit,
			models.TicketChangeField,
			models.TicketChangeFlagMod,
			models.TicketDependency,
			models.TicketFile,
			models.TicketFlag,
			models.TicketFlagType,
			models.TicketOrigin,
			models.TicketState,
			models.TicketStateTransition,
			models.TicketTemplate,
			models.TicketScheduler,
			models.TicketSchedulerUserAssignment,
			models.TicketSchedulerGroupAssignment
		)

	@classmethod
	def get_sql_data(cls, modobj, sess):
		from netprofile_tickets.models import (
			TicketChangeField,
			TicketOrigin
		)
		from netprofile_core.models import (
			Group,
			GroupCapability,
			LogType,
			Privilege
		)

		sess.add(LogType(
			id=3,
			name='Tickets'
		))

		privs = (
			Privilege(
				code='BASE_TICKETS',
				name='Access: Tickets'
			),
			Privilege(
				code='TICKETS_LIST',
				name='Tickets: List'
			),
			Privilege(
				code='TICKETS_LIST_ARCHIVED',
				name='Tickets: List archived'
			),
			Privilege(
				code='TICKETS_CREATE',
				name='Tickets: Create'
			),
			Privilege(
				code='TICKETS_UPDATE',
				name='Tickets: Update'
			),
			Privilege(
				code='TICKETS_COMMENT',
				name='Tickets: Comment'
			),
			Privilege(
				code='TICKETS_ARCHIVAL',
				name='Tickets: Archival'
			),
			Privilege(
				code='TICKETS_DIRECT',
				name='Tickets: Direct access',
				can_be_set=False
			),
			Privilege(
				code='TICKETS_OWN_LIST',
				name='Tickets: List assigned to user'
			),
			Privilege(
				code='TICKETS_OWNGROUP_LIST',
				name='Tickets: List assigned to group'
			),
			Privilege(
				code='TICKETS_CHANGE_DATE',
				name='Tickets: Change date'
			),
			Privilege(
				code='TICKETS_CHANGE_UID',
				name='Tickets: Change assigned user'
			),
			Privilege(
				code='TICKETS_CHANGE_GID',
				name='Tickets: Change assigned group'
			),
			Privilege(
				code='TICKETS_CHANGE_STATE',
				name='Tickets: Change state'
			),
			Privilege(
				code='TICKETS_CHANGE_FLAGS',
				name='Tickets: Change flags'
			),
			Privilege(
				code='TICKETS_CHANGE_ENTITY',
				name='Tickets: Change entity'
			),
			Privilege(
				code='TICKETS_DEPENDENCIES',
				name='Tickets: Edit dependencies'
			),
			Privilege(
				code='FILES_ATTACH_2TICKETS',
				name='Files: Attach to tickets'
			),
			Privilege(
				code='TICKETS_STATES_CREATE',
				name='Tickets: Create states'
			),
			Privilege(
				code='TICKETS_STATES_EDIT',
				name='Tickets: Edit states'
			),
			Privilege(
				code='TICKETS_STATES_DELETE',
				name='Tickets: Delete states'
			),
			Privilege(
				code='TICKETS_FLAGTYPES_CREATE',
				name='Tickets: Create flag types'
			),
			Privilege(
				code='TICKETS_FLAGTYPES_EDIT',
				name='Tickets: Edit flag types'
			),
			Privilege(
				code='TICKETS_FLAGTYPES_DELETE',
				name='Tickets: Delete flag types'
			),
			Privilege(
				code='TICKETS_ORIGINS_CREATE',
				name='Tickets: Create origins'
			),
			Privilege(
				code='TICKETS_ORIGINS_EDIT',
				name='Tickets: Edit origins'
			),
			Privilege(
				code='TICKETS_ORIGINS_DELETE',
				name='Tickets: Delete origins'
			),
			Privilege(
				code='TICKETS_TRANSITIONS_CREATE',
				name='Tickets: Create transitions'
			),
			Privilege(
				code='TICKETS_TRANSITIONS_EDIT',
				name='Tickets: Edit transitions'
			),
			Privilege(
				code='TICKETS_TRANSITIONS_DELETE',
				name='Tickets: Delete transitions'
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

		origins = (
			TicketOrigin(
				id=1,
				name='Operator',
				description='Added manually via an administrative UI.'
			),
			TicketOrigin(
				id=2,
				name='Via site',
				description='Added via client portal.'
			),
			TicketOrigin(
				id=3,
				name='Via e-mail',
				description='Added via incoming e-mail message.'
			),
			TicketOrigin(
				id=4,
				name='Via voicemail',
				description='Added via incoming voicemail message.'
			)
		)

		for obj in origins:
			sess.add(obj)

		chfields = (
			TicketChangeField(
				id=1,
				name='User'
			),
			TicketChangeField(
				id=2,
				name='Group'
			),
			TicketChangeField(
				id=3,
				name='Time'
			),
			TicketChangeField(
				id=4,
				name='Archived'
			),
			TicketChangeField(
				id=5,
				name='Entity'
			)
		)

		for obj in chfields:
			sess.add(obj)

	def get_css(self, request):
		return (
			'netprofile_tickets:static/css/main.css',
		)

	def get_local_js(self, request, lang):
		return (
			'netprofile_tickets:static/webshell/locale/webshell-lang-' + lang + '.js',
		)

	def get_autoload_js(self, request):
		return (
			'NetProfile.form.field.WeekDayField',
		)

	def get_controllers(self, request):
		return (
			'NetProfile.tickets.controller.TicketGrid',
		)

	@property
	def name(self):
		return _('Tickets')

