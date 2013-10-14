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

_ = TranslationStringFactory('netprofile_medical')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_medical:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_deps(self):
		return ('tickets',)

	def get_models(self):
		return (
			ICDBlock,
			ICDClass,
			ICDEntry,
			ICDHistory,
			ICDMapping,
			MedicalTestType,
			MedicalTest
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

