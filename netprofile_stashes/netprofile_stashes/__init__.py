#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Stashes module
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

_ = TranslationStringFactory('netprofile_stashes')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_route(
			'stashes.cl.accounts',
			'/accounts/*traverse',
			factory='netprofile_stashes.views.ClientRootFactory',
			vhost='client'
		)
		mmgr.cfg.add_translation_dirs('netprofile_stashes:locale/')
		mmgr.cfg.scan()
		

	@classmethod
	def get_deps(cls):
		return ('entities',)

	@classmethod
	def get_models(cls):
		from netprofile_stashes import models
		return (
			models.FuturePayment,
			models.Stash,
			models.StashIO,
			models.StashIOType,
			models.StashOperation
		)

	@classmethod
	def get_sql_functions(cls):
		from netprofile_stashes import models
		return (
			models.FuturesPollProcedure,
		)

	@classmethod
	def get_sql_events(cls):
		from netprofile_stashes import models
		return (
			models.FuturesPollEvent,
		)

	@classmethod
	def get_sql_data(cls, modobj, sess):
		from netprofile_stashes.models import (
			IOOperationType,
			OperationClass,
			StashIOType
		)
		from netprofile_core.models import (
			Group,
			GroupCapability,
			LogType,
			Privilege
		)

		sess.add(LogType(
			id=12,
			name='Stashes'
		))
		sess.add(LogType(
			id=16,
			name='Promised Payments'
		))

		privs = (
			Privilege(
				code='BASE_STASHES',
				name='Access: Stashes'
			),
			Privilege(
				code='STASHES_LIST',
				name='Stashes: List'
			),
			Privilege(
				code='STASHES_CREATE',
				name='Stashes: Create'
			),
			Privilege(
				code='STASHES_EDIT',
				name='Stashes: Edit'
			),
			Privilege(
				code='STASHES_DELETE',
				name='Stashes: Delete'
			),
			Privilege(
				code='STASHES_IO',
				name='Stashes: Operations'
			),
			Privilege(
				code='STASHES_IOTYPES_CREATE',
				name='Stashes: Create op. types'
			),
			Privilege(
				code='STASHES_IOTYPES_EDIT',
				name='Stashes: Edit op. types'
			),
			Privilege(
				code='STASHES_IOTYPES_DELETE',
				name='Stashes: Delete op. types'
			),
			Privilege(
				code='BASE_FUTURES',
				name='Access: Promised payments'
			),
			Privilege(
				code='FUTURES_LIST',
				name='Promised payments: List'
			),
			Privilege(
				code='FUTURES_CREATE',
				name='Promised payments: Create'
			),
			Privilege(
				code='FUTURES_EDIT',
				name='Promised payments: Edit'
			),
			Privilege(
				code='FUTURES_APPROVE',
				name='Promised payments: Approve'
			),
			Privilege(
				code='FUTURES_CANCEL',
				name='Promised payments: Cancel'
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

		siotypes = (
			StashIOType(
				id=1,
				name='Subscription fee',
				io_class=OperationClass.system,
				type=IOOperationType.outgoing,
				oper_visible=False,
				user_visible=True,
				description='Periodic withdrawal of funds for an active service.'
			),
			StashIOType(
				id=2,
				name='Postpaid service fee',
				io_class=OperationClass.system,
				type=IOOperationType.outgoing,
				oper_visible=False,
				user_visible=True,
				description='Withdrawal of funds for used service.'
			),
			StashIOType(
				id=3,
				name='Reimbursement for unused subscription fee.',
				io_class=OperationClass.system,
				type=IOOperationType.incoming,
				oper_visible=False,
				user_visible=True,
				description='Addition of funds that is a result of tariff recalculation or operator action.'
			),
			StashIOType(
				id=4,
				name='Confirmation of promised payment',
				io_class=OperationClass.system,
				type=IOOperationType.bidirectional,
				oper_visible=False,
				user_visible=True,
				description='This operation is a result of a payment promise being fulfilled.'
			),
			StashIOType(
				id=5,
				name='Transfer from another stash',
				io_class=OperationClass.system,
				type=IOOperationType.incoming,
				oper_visible=False,
				user_visible=True,
				description='Addition of funds that were transferred from another stash.'
			),
			StashIOType(
				id=6,
				name='Transfer to another stash',
				io_class=OperationClass.system,
				type=IOOperationType.outgoing,
				oper_visible=False,
				user_visible=True,
				description='Withdrawal of funds that were transferred to another stash.'
			),
			StashIOType(
				id=7,
				name='Payment for service activation',
				io_class=OperationClass.system,
				type=IOOperationType.outgoing,
				oper_visible=False,
				user_visible=True,
				description='Initial payment for activation of an auxiliary service.',
			),
			StashIOType(
				id=8,
				name='Payment for maintaining service',
				io_class=OperationClass.system,
				type=IOOperationType.outgoing,
				oper_visible=False,
				user_visible=True,
				description='Periodic payment for maintaining an auxiliary service.'
			)
		)

	def get_css(self, request):
		return (
			'netprofile_stashes:static/css/main.css',
		)

	@property
	def name(self):
		return _('Stashes')

