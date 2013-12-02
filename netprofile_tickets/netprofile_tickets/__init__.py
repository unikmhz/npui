#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Tickets module
# © Copyright 2013 Alex 'Unik' Unigovsky
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

	def get_autoload_js(self, request):
		return (
			'Ext.ux.form.WeekDayField',
		)

	def get_controllers(self, request):
		return (
			'NetProfile.tickets.controller.TicketGrid',
		)

	@property
	def name(self):
		return _('Tickets')

