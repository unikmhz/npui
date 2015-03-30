#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: CLI commands
# © Copyright 2014-2015 Alex 'Unik' Unigovsky
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
import os
import pkg_resources
import re

from cliff.lister import Lister
from cliff.show import ShowOne
from cliff.command import Command

from pyramid.i18n import TranslationStringFactory
from sqlalchemy.exc import ProgrammingError

from netprofile.common.modules import ModuleError

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

		self.app.hooks.run_hook('np.cli.module.list', self.app, columns, data)
		return (columns, sorted(data, key=lambda row: row[0]))

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
			is_ok = True
			for mod in mm.modules:
				if mod != 'core':
					try:
						self.app.hooks.run_hook('np.cli.module.install.before', self.app, mod, sess)
						ret = mm.install(mod, sess)
						self.app.hooks.run_hook('np.cli.module.install.after', self.app, mod, sess, ret)
					except ModuleError as e:
						if self.app.options.debug:
							raise e
						is_ok = False
						self.log.error(e)
					else:
						self.log.info('Module \'%s\' successfully installed.', mod)
			if not is_ok:
				raise RuntimeError('Some modules failed to install.')
			self.log.info('All done.')
			return

		self.app.hooks.run_hook('np.cli.module.install.before', self.app, args.name, sess)
		ret = mm.install(args.name, sess)
		self.app.hooks.run_hook('np.cli.module.install.after', self.app, args.name, sess, ret)
		if isinstance(ret, bool):
			if ret:
				self.log.info('Module \'%s\' successfully installed.', args.name)
				return
			raise RuntimeError('Module \'%s\' is already installed.' % (args.name,))
		raise RuntimeError('Unknown result.')

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
		vlevel = self.app.options.verbose_level
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
		vlevel = self.app.options.verbose_level
		self.app.setup_mako_sql()
		sess = self.app.db_session
		mm = self.app.mm

		if len(mm.modules) > 0:
			mm.rescan()
		else:
			mm.scan()

		if not mm.load('core'):
			raise RuntimeError('Unable to proceed without core module.')

		if args.name.lower() == 'all':
			for mod in mm.modules:
				if mm.is_installed(mod, sess):
					if mod != 'core':
						self.app.hooks.run_hook('np.cli.module.enable.before', self.app, mod, sess)
						ret = mm.enable(mod)
						self.app.hooks.run_hook('np.cli.module.enable.after', self.app, mod, sess, ret)
						if ret:
							self.log.info('Enabled module \'%s\'.', mod)
				elif vlevel > 1:
					self.log.info('Module \'%s\' is not installed, so can\'t enable.', mod)
			self.log.info('All done.')
			return

		if not mm.is_installed(args.name, sess):
			raise RuntimeError('Module \'%s\' is not installed, so can\'t enable.' % (args.name,))
		if args.name == 'core':
			raise RuntimeError('Can\'t enable core module.')
		self.app.hooks.run_hook('np.cli.module.enable.before', self.app, args.name, sess)
		ret = mm.enable(args.name)
		self.app.hooks.run_hook('np.cli.module.enable.after', self.app, args.name, sess, ret)
		if isinstance(ret, bool):
			if ret:
				self.log.info('Enabled module \'%s\'.', args.name)
				return
			else:
				raise RuntimeError('Module \'%s\' wasn\'t found or is not installed.' % (args.name,))
		raise RuntimeError('Unknown result.')

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
		vlevel = self.app.options.verbose_level
		self.app.setup_mako_sql()
		sess = self.app.db_session
		mm = self.app.mm

		if len(mm.modules) > 0:
			mm.rescan()
		else:
			mm.scan()

		if not mm.load('core'):
			raise RuntimeError('Unable to proceed without core module.')

		if args.name.lower() == 'all':
			for mod in mm.modules:
				if mm.is_installed(mod, sess):
					if (mod != 'core'):
						self.app.hooks.run_hook('np.cli.module.disable.before', self.app, mod, sess)
						ret = mm.disable(mod)
						self.app.hooks.run_hook('np.cli.module.disable.after', self.app, mod, sess, ret)
						if ret:
							self.log.info('Disabled module \'%s\'.', mod)
				elif vlevel > 1:
					self.log.info('Module \'%s\' is not installed, so can\'t disable.', mod)
			self.log.info('All done.')
			return

		if not mm.is_installed(args.name, sess):
			raise RuntimeError('Module \'%s\' is not installed, so can\'t disable.' % (args.name,))
		if args.name == 'core':
			raise RuntimeError('Can\'t disable core module.')
		self.app.hooks.run_hook('np.cli.module.disable.before', self.app, args.name, sess)
		ret = mm.disable(args.name)
		self.app.hooks.run_hook('np.cli.module.disable.after', self.app, args.name, sess, ret)
		if isinstance(ret, bool):
			if ret:
				self.log.info('Disabled module \'%s\'.', args.name)
				return
			else:
				raise RuntimeError('Module \'%s\' wasn\'t found or is not installed.' % (args.name,))
		raise RuntimeError('Unknown result.')

class Deploy(Command):
	"""
	Create deployment file hierarchy.
	"""

	log = logging.getLogger(__name__)
	_ini_section_rx = re.compile(r'^\s*\[(.+)\]')
	_ini_option_rx = re.compile(r'^(\s*)([^\s=:]+)(\s*[:=]\s*)(.*)$')

	def get_parser(self, prog_name):
		parser = super(Deploy, self).get_parser(prog_name)
		parser.add_argument(
			'path',
			help='Directory to create.'
		)
		return parser

	def _assert_dir(self, deploy_dir, name):
		fdir = os.path.join(deploy_dir, name)
		if not os.path.lexists(fdir):
			os.mkdir(fdir, 0o700)
		elif not os.path.isdir(fdir):
			os.umask(self.old_mask)
			raise RuntimeError('Path exists but is not a directory: "%s".' % (fdir,))

		return fdir

	def _write_ini(self, infile, outfile, replace={}):
		cur_section = ''
		with open(infile, 'r') as inf:
			with open(outfile, 'x') as outf:
				for line in inf:
					m = self._ini_section_rx.match(line)
					if m:
						cur_section = m.group(1)
					else:
						m = self._ini_option_rx.match(line)
						if m:
							key = m.group(2)
							if (cur_section in replace) and (key in replace[cur_section]):
								line = m.group(1) + key + m.group(3) + replace[cur_section][key] + '\n'
					outf.write(line)
		# This is racy
		os.chmod(outfile, 0o600)

	def _write_wsgi(self, wsgi_file, ini_file, ini_section):
		with open(wsgi_file, 'x') as outf:
			outf.write('#!/usr/bin/env python\n\nfrom pyramid.paster import get_app\napplication = get_app(\n')
			outf.write('    %s, %s)\n\n' % (repr(ini_file), repr(ini_section)))
		# This is racy
		os.chmod(wsgi_file, 0o700)

	def _write_activate(self, sh_file, ini_file):
		with open(sh_file, 'x') as outf:
			outf.write('NP_INI_FILE="%s"\nexport NP_INI_FILE\n\n' % (ini_file,))
			if 'VIRTUAL_ENV' in os.environ:
				outf.write('source %s/bin/activate\n\n' % (os.environ['VIRTUAL_ENV'],))
		# This is racy
		os.chmod(sh_file, 0o600)

	def take_action(self, args):
		self.old_mask = os.umask(0o077)
		np_dir = os.path.abspath(self.app.dist.location)
		deploy_dir = os.path.abspath(args.path)

		if not os.path.isdir(np_dir):
			os.umask(self.old_mask)
			raise RuntimeError('Can\'t locate netprofile module directory.')
		if os.path.lexists(deploy_dir) and (not os.path.isdir(deploy_dir)):
			os.umask(self.old_mask)
			raise RuntimeError('Invalid path specified.')

		if not os.path.exists(deploy_dir):
			os.mkdir(deploy_dir, 0o700)
		tplc_dir = self._assert_dir(deploy_dir, 'tplc')
		admin_tplc_dir = self._assert_dir(tplc_dir, 'admin')
		client_tplc_dir = self._assert_dir(tplc_dir, 'client')
		xop_tplc_dir = self._assert_dir(tplc_dir, 'xop')
		fonts_dir = self._assert_dir(deploy_dir, 'fonts')

		mail_dir = self._assert_dir(deploy_dir, 'maildir')

		replace = {
			'app:netprofile' : {
				'mail.queue_path'            : mail_dir,
				'mako.module_directory'      : admin_tplc_dir,
				'netprofile.fonts.directory' : fonts_dir
			},
			'app:app_npclient' : {
				'mail.queue_path'       : mail_dir,
				'mako.module_directory' : client_tplc_dir
			},
			'app:app_xop' : {
				'mail.queue_path'       : mail_dir,
				'mako.module_directory' : xop_tplc_dir
			}
		}

		ini_prod = os.path.join(deploy_dir, 'production.ini')
		ini_dev = os.path.join(deploy_dir, 'development.ini')

		self._write_ini(
			os.path.join(np_dir, 'production.ini'),
			ini_prod, replace
		)
		self._write_ini(
			os.path.join(np_dir, 'development.ini'),
			ini_dev, replace
		)

		self._write_wsgi(
			os.path.join(deploy_dir, 'netprofile-admin-prod.wsgi'),
			ini_prod, 'main'
		)
		self._write_wsgi(
			os.path.join(deploy_dir, 'netprofile-client-prod.wsgi'),
			ini_prod, 'npclient'
		)
		self._write_wsgi(
			os.path.join(deploy_dir, 'netprofile-xop-prod.wsgi'),
			ini_prod, 'xop'
		)
		self._write_wsgi(
			os.path.join(deploy_dir, 'netprofile-admin-devel.wsgi'),
			ini_dev, 'main'
		)
		self._write_wsgi(
			os.path.join(deploy_dir, 'netprofile-client-devel.wsgi'),
			ini_dev, 'npclient'
		)
		self._write_wsgi(
			os.path.join(deploy_dir, 'netprofile-xop-devel.wsgi'),
			ini_dev, 'xop'
		)

		self._write_activate(
			os.path.join(deploy_dir, 'activate-production'),
			ini_prod
		)
		self._write_activate(
			os.path.join(deploy_dir, 'activate-development'),
			ini_dev
		)

		os.umask(self.old_mask)
		self.log.info('Created NetProfile deployment: %s', deploy_dir)

