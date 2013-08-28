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
			TicketStateTransition,
			TicketTemplate,
			TicketScheduler,
			TicketSchedulerUserAssignment,
			TicketSchedulerGroupAssignment
		)

	def get_css(self, request):
		return (
			'netprofile_tickets:static/css/main.css',
		)

	def get_local_js(self, request, lang):
		return (
			'netprofile_tickets:static/webshell/locale/webshell-lang-' + lang + '.js',
		)

	def get_controllers(self, request):
		return (
			'NetProfile.tickets.controller.TicketGrid',
		)

	@property
	def name(self):
		return _('Tickets')

