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

_ = TranslationStringFactory('netprofile_tickets')

class Module(ModuleBase):
	def __init__(self, mmgr):
		self.mmgr = mmgr
		mmgr.cfg.add_translation_dirs('netprofile_tickets:locale/')
		mmgr.cfg.scan()

	@classmethod
	def get_deps(cls):
		return ('entities',)

	def get_models(self):
		return (
			Ticket,
			TicketChange,
			TicketChangeBit,
			TicketChangeField,
			TicketChangeFlagMod,
			TicketDependency,
			TicketFile,
			TicketFlag,
			TicketFlagType,
			TicketOrigin,
			TicketState,
			TicketStateTransition
		)

	def get_css(self, request):
		return (
			'netprofile_tickets:static/css/main.css',
		)

	@property
	def name(self):
		return _('Tickets')

