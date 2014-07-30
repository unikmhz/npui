#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Documents module
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

_ = TranslationStringFactory('netprofile_documents')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_documents:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_models(cls):
		from netprofile_documents import models
		return (
			models.Document,
			models.DocumentBundle,
			models.DocumentBundleMapping
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
				code='DOCUMENTS_LIST',
				name='Documents: List'
			),
			Privilege(
				code='DOCUMENTS_CREATE',
				name='Documents: Create'
			),
			Privilege(
				code='DOCUMENTS_EDIT',
				name='Documents: Edit'
			),
			Privilege(
				code='DOCUMENTS_DELETE',
				name='Documents: Delete'
			),
			Privilege(
				code='DOCUMENTS_GENERATE',
				name='Documents: Generate'
			),
			Privilege(
				code='DOCUMENTS_BUNDLES_CREATE',
				name='Documents: Create Bundles'
			),
			Privilege(
				code='DOCUMENTS_BUNDLES_EDIT',
				name='Documents: Edit Bundles'
			),
			Privilege(
				code='DOCUMENTS_BUNDLES_DELETE',
				name='Documents: Delete Bundles'
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

	def get_autoload_js(self, request):
		return (
			'NetProfile.documents.button.DocumentButton',
		)

	def get_css(self, request):
		return (
			'netprofile_documents:static/css/main.css',
		)

	@property
	def name(self):
		return _('Documents')

