#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from netprofile.common.modules import ModuleBase

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_medical')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_medical:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('tickets',)

        @classmethod
	def get_models(cls):
                from netprofile_medical import models
		return (
			models.ICDBlock,
			models.ICDClass,
			models.ICDEntry,
			models.ICDHistory,
			models.ICDMapping,
			models.MedicalTestType,
			models.MedicalTest
		)

	def get_css(self, request):
		return (
			'netprofile_medical:static/css/main.css',
		)

	def get_controllers(self, request):
		return (
			'NetProfile.medical.controller.TicketGrid',
		)

	@property
	def name(self):
		return _('Medical')

