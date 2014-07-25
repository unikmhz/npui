#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Entities module
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

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_entities')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_entities:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('geo',)

	@classmethod
	def get_models(cls):
		from netprofile_entities import models
		return (
			models.Address,
			models.Phone,
			models.Entity,
			models.EntityComment,
			models.EntityFile,
			models.EntityFlag,
			models.EntityFlagType,
			models.EntityState,
			models.PhysicalEntity,
			models.LegalEntity,
			models.StructuralEntity,
			models.ExternalEntity
		)

	@classmethod
	def get_sql_views(cls):
		from netprofile_entities import models
		return (
			models.EntitiesBaseView,
		)

	def get_local_js(self, request, lang):
		return (
			'netprofile_entities:static/webshell/locale/webshell-lang-' + lang + '.js',
		)

	def get_autoload_js(self, request):
		return (
			'NetProfile.entities.view.HistoryGrid',
		)

	def get_css(self, request):
		return (
			'netprofile_entities:static/css/main.css',
		)

	@property
	def name(self):
		return _('Entities')

