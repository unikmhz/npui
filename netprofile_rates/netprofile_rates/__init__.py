#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Rates module
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

_ = TranslationStringFactory('netprofile_rates')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_rates:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('dialup',)

	@classmethod
	def get_models(cls):
		from netprofile_rates import models
		return (
			models.BillingPeriod,
			models.Destination,
			models.DestinationSet,
			models.EntityTypeRateClass,
			models.Filter,
			models.FilterSet,
			models.GlobalRateModifier,
			models.Rate,
			models.RateClass,
			models.RateModifierType
		)

	@classmethod
	def get_sql_functions(cls):
		from netprofile_rates import models
		return (
			models.AcctRateDestProcedure,
			models.AcctRateFilterProcedure,
			models.AcctRatePercentRemainingFunction,
			models.AcctRatePercentSpentFunction,
			models.AcctRateQPCountFunction,
			models.AcctRateQPLengthFunction,
			models.AcctRateQPNewFunction,
			models.AcctRateQPSpentFunction
		)

	@classmethod
	def get_sql_data(cls, modobj, sess):
		from netprofile_rates.models import (
			DestinationSet,
			FilterSet,
			RateClass
		)
		from netprofile_core.models import (
			Group,
			GroupCapability,
			LogType,
			Privilege
		)

		sess.add(LogType(
			id=13,
			name='Rates'
		))

		privs = (
			Privilege(
				code='BASE_RATES',
				name='Access: Rates'
			),
			Privilege(
				code='RATES_LIST',
				name='Rates: List'
			),
			Privilege(
				code='RATES_CREATE',
				name='Rates: Create'
			),
			Privilege(
				code='RATES_EDIT',
				name='Rates: Edit'
			),
			Privilege(
				code='RATES_DELETE',
				name='Rates: Delete'
			),
			Privilege(
				code='RATES_CLASSES_CREATE',
				name='Rates: Create classes'
			),
			Privilege(
				code='RATES_CLASSES_EDIT',
				name='Rates: Edit classes'
			),
			Privilege(
				code='RATES_CLASSES_DELETE',
				name='Rates: Delete classes'
			),
			Privilege(
				code='RATES_DS_CREATE',
				name='Rates: Create destinations'
			),
			Privilege(
				code='RATES_DS_EDIT',
				name='Rates: Edit destinations'
			),
			Privilege(
				code='RATES_DS_DELETE',
				name='Rates: Delete destinations'
			),
			Privilege(
				code='RATES_FS_CREATE',
				name='Rates: Create filters'
			),
			Privilege(
				code='RATES_FS_EDIT',
				name='Rates: Edit filters'
			),
			Privilege(
				code='RATES_FS_DELETE',
				name='Rates: Delete filters'
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

		sess.add(RateClass(
			name='Default Class',
			description='This is a class added during module installation. You can safely remove it, provided you haven\'t specified any rates in this class yet.'
		))

		sess.add(DestinationSet(name='Default Set'))
		sess.add(FilterSet(name='Default Set'))

	def get_css(self, request):
		return (
			'netprofile_rates:static/css/main.css',
		)

	@property
	def name(self):
		return _('Rates')

