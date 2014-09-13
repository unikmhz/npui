#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: CLI commands
# © Copyright 2014 Alex 'Unik' Unigovsky
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

import logging

from cliff.lister import Lister
from cliff.show import ShowOne
from cliff.command import Command

from pyramid.i18n import TranslationStringFactory
from sqlalchemy.exc import ProgrammingError

_ = TranslationStringFactory('netprofile')

class ListModules(Lister):
	"""
	List available/installed modules.
	"""

	log = logging.getLogger(__name__)

	def get_parser(self, prog_name):
		parser = super(ListModules, self).get_parser(prog_name)
		parser.add_argument(
			'-F', '--filter',
			choices=('all', 'installed', 'uninstalled', 'enabled', 'disabled'),
			default='all',
			help='Show only modules in this state.'
		)
		return parser

	def take_action(self, args):
		has_core = True
		loc = self.app.locale
		flt = args.filter
		try:
			from netprofile_core.models import NPModule
		except ImportError:
			has_core = False

		columns = (
			loc.translate(_('Name')),
			loc.translate(_('Available')),
			loc.translate(_('Installed')),
			loc.translate(_('Enabled'))
		)
		data = []

		installed = {}
		if has_core:
			sess = self.app.db_session
			try:
				for mod in sess.query(NPModule):
					installed[mod.name] = (mod.current_version, mod.enabled)
			except ProgrammingError:
				installed = {}
				has_core = False

		self.app.mm.rescan()
		for moddef, ep in self.app.mm.modules.items():
			curversion = _('- N/A -')
			enabled = _('- N/A -')
			if moddef in installed:
				if installed[moddef][1] and (flt == 'disabled'):
					continue
				if (not installed[moddef][1]) and (flt == 'enabled'):
					continue
				curversion = installed[moddef][0]
				enabled = _('YES') if installed[moddef][1] else _('NO')
			elif flt in ('installed', 'enabled', 'disabled'):
				continue
			data.append((moddef, ep.dist.version, loc.translate(curversion), loc.translate(enabled)))

		return (columns, data)

class ShowModule(ShowOne):
	"""
	Show module details.
	"""

	log = logging.getLogger(__name__)

	def take_action(self, args):
		raise RuntimeError('Not implemented.')

class InstallModule(Command):
	"""
	Install available module to database.
	"""

	log = logging.getLogger(__name__)

	def get_parser(self, prog_name):
		parser = super(InstallModule, self).get_parser(prog_name)
		parser.add_argument(
			'name',
			help='Name of the module to install or a special value \'all\'.'
		)
		return parser

	def take_action(self, args):
		self.app.setup_mako_sql()
		sess = self.app.db_session
		mm = self.app.mm

		if len(mm.modules) > 0:
			mm.rescan()
		else:
			mm.scan()
		if args.name != 'core':
			mm.load('core')
		mm.load_all()

		if args.name.lower() == 'all':
			mm.install('core', sess)
			for mod in mm.modules:
				if mod != 'core':
					mm.install(mod, sess)
			self.app.stdout.write('All done.\n')
			return

		ret = mm.install(args.name, sess)
		if isinstance(ret, bool):
			if ret:
				self.app.stdout.write('Module \'%s\' successfully installed.\n' % (args.name,))
				return
			raise RuntimeError('Error: Module \'%s\' is already installed.' % (args.name,))
		raise RuntimeError('Error: Unknown result.')

class UninstallModule(Command):
	"""
	Uninstall module from database.
	"""

	log = logging.getLogger(__name__)

	def get_parser(self, prog_name):
		parser = super(UninstallModule, self).get_parser(prog_name)
		parser.add_argument(
			'name',
			help='Name of the module to uninstall or a special value \'all\'.'
		)
		return parser

	def take_action(self, args):
		raise RuntimeError('Not implemented.')

class EnableModule(Command):
	"""
	Enable installed module.
	"""

	log = logging.getLogger(__name__)

	def get_parser(self, prog_name):
		parser = super(EnableModule, self).get_parser(prog_name)
		parser.add_argument(
			'name',
			help='Name of the module to enable or a special value \'all\'.'
		)
		return parser

	def take_action(self, args):
		self.app.setup_mako_sql()
		sess = self.app.db_session
		mm = self.app.mm

		if len(mm.modules) > 0:
			mm.rescan()
		else:
			mm.scan()

		if not mm.load('core'):
			raise RuntimeError('Error: Unable to proceed without core module.')

		if args.name.lower() == 'all':
			for mod in mm.modules:
				if mm.is_installed(mod, sess) and (mod != 'core'):
					mm.enable(mod)
			self.app.stdout.write('All done.\n')
			return

		ret = mm.enable(args.name)
		if isinstance(ret, bool):
			if ret:
				self.app.stdout.write('Enabled module \'%s\'.\n' % (args.name,))
				return
			raise RuntimeError('Error: Module \'%s\' wasn\'t found or is not installed.' % (args.name,))
		raise RuntimeError('Error: Unknown result.')

class DisableModule(Command):
	"""
	Disable installed module.
	"""

	log = logging.getLogger(__name__)

	def get_parser(self, prog_name):
		parser = super(DisableModule, self).get_parser(prog_name)
		parser.add_argument(
			'name',
			help='Name of the module to disable or a special value \'all\'.'
		)
		return parser

	def take_action(self, args):
		self.app.setup_mako_sql()
		sess = self.app.db_session
		mm = self.app.mm

		if len(mm.modules) > 0:
			mm.rescan()
		else:
			mm.scan()

		if not mm.load('core'):
			raise RuntimeError('Error: Unable to proceed without core module.')

		if args.name.lower() == 'all':
			for mod in mm.modules:
				if mm.is_installed(mod, sess) and (mod != 'core'):
					mm.disable(mod)
			self.app.stdout.write('All done.\n')
			return

		ret = mm.disable(args.name)
		if isinstance(ret, bool):
			if ret:
				self.app.stdout.write('Disabled module \'%s\'.\n' % (args.name,))
				return
			else:
				raise RuntimeError('Error: Module \'%s\' wasn\'t found or is not installed.' % (args.name,))
		raise RuntimeError('Error: Unknown result.')

