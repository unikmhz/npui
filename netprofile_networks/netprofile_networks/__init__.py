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

_ = TranslationStringFactory('netprofile_networks')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_networks:locale/')
		mmgr.cfg.scan()
		

	def get_models(self):
		return (
			Network,
			NetworkGroup,
			NetworkHostLinkage,
			NetworkHost
			)
	
	def get_css(self, request):
		return (
			'netprofile_networks:static/css/main.css',
		)

	@property
	def name(self):
		return _('Networks')

