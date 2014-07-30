#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Domains module
# © Copyright 2013 Nikita Andriyanov
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

_ = TranslationStringFactory('netprofile_domains')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_domains:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_models(cls):
		from netprofile_domains import models
		return (
			models.Domain,
			models.DomainAlias,
			models.DomainTXTRecord,
			models.DomainServiceType
		)

	@classmethod
	def get_sql_functions(cls):
		from netprofile_domains import models
		return (
			models.DomainGetFullFunction,
		)

	@classmethod
	def get_sql_views(cls):
		from netprofile_domains import models
		return (
			models.DomainsBaseView,
			models.DomainsEnabledView,
			models.DomainsPublicView,
			models.DomainsSignedView
		)

	@classmethod
	def get_sql_data(cls, modobj, sess):
		from netprofile_domains import models
		from netprofile_core.models import (
			Group,
			GroupCapability,
			LogType,
			Privilege
		)

		sess.add(LogType(
			id=5,
			name='Domains'
		))
		sess.flush()

		privs = (
			Privilege(
				code='BASE_DOMAINS',
				name='Access: Domains'
			),
			Privilege(
				code='DOMAINS_LIST',
				name='Domains: List'
			),
			Privilege(
				code='DOMAINS_CREATE',
				name='Domains: Create'
			),
			Privilege(
				code='DOMAINS_EDIT',
				name='Domains: Edit'
			),
			Privilege(
				code='DOMAINS_DELETE',
				name='Domains: Delete'
			),
			Privilege(
				code='DOMAINS_SERVICETYPES_CREATE',
				name='Domains: Create service types'
			),
			Privilege(
				code='DOMAINS_SERVICETYPES_EDIT',
				name='Domains: Edit service types'
			),
			Privilege(
				code='DOMAINS_SERVICETYPES_DELETE',
				name='Domains: Delete service types'
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

		dstypes = (
			models.DomainServiceType(
				id=1,
				name='Primary Name Server',
				unique=True
			),
			models.DomainServiceType(
				id=2,
				name='Secondary Name Server',
				unique=False
			),
			models.DomainServiceType(
				id=3,
				name='Primary Mail Server',
				unique=True
			),
			models.DomainServiceType(
				id=4,
				name='Secondary Mail Server',
				unique=False
			),
			models.DomainServiceType(
				id=5,
				name='Default Host',
				unique=False
			)
		)

		for dst in dstypes:
			sess.add(dst)

	def get_css(self, request):
		return (
			'netprofile_domains:static/css/main.css',
		)

	@property
	def name(self):
		return _('Domains')

