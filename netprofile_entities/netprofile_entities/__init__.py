#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from netprofile.common.modules import ModuleBase
from .models import *

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

	def get_models(self):
		return (
			Address,
			Phone,
			Entity,
			EntityComment,
			EntityFile,
			EntityFlag,
			EntityFlagType,
			EntityState,

			PhysicalEntity,
			LegalEntity,
			StructuralEntity,
			ExternalEntity,
			AccessEntity
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

