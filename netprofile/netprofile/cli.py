#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: CLI commands
# © Copyright 2014-2016 Alex 'Unik' Unigovsky
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

import inspect
import logging
import os
import pkg_resources
import re

from cliff.lister import Lister
from cliff.show import ShowOne
from cliff.command import Command

from pyramid.i18n import TranslationStringFactory
from sqlalchemy.exc import ProgrammingError
from alembic import command as alembic_cmd

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

	def get_parser(self, prog_name):
		parser = super(ShowModule, self).get_parser(prog_name)
		parser.add_argument(
			'name',
			help='Name of the module to inspect.'
		)
		return parser

	def take_action(self, args):
		loc = self.app.locale

		columns = (
			loc.translate(_('Module')),
			loc.translate(_('Summary')),
			loc.translate(_('Homepage')),
			loc.translate(_('Author')),
			loc.translate(_('E-Mail')),
			loc.translate(_('License')),
			loc.translate(_('Location')),
			loc.translate(_('Version'))
		)
		data = [None]*len(columns)

		mm = self.app.mm
		if len(mm.modules) > 0:
			mm.rescan()
		else:
			mm.scan()

		mod = args.name.lower()
		if mod not in mm.modules:
			raise RuntimeError('Seems like module \'%s\' does not exist.' % args.name)

		modcode = mm.modules[mod].module_name
		data[0] = modcode

		'''
		Probably not the best method to get metadata, but it works.
		Needs pkg_resources to be imported.
		'''
		pkg = next(pkg_resources.find_distributions(modcode, only=True))
		#pkg = pkg_resources.get_distribution(modcode)

		if not pkg or not pkg.has_metadata(pkg_resources.Distribution.PKG_INFO):
			raise RuntimeError('PKG-INFO not found')

		for line in pkg.get_metadata_lines(pkg_resources.Distribution.PKG_INFO):
			if ': ' in line:
				(k, v) = line.split(': ', 1)
				if k == "Summary":
					data[1] = v
				elif k == "Home-page":
					data[2] = v
				elif k == "Author":
					data[3] = v
				elif k == "Author-email":
					data[4] = v
				elif k == "License":
					data[5] = v

		data[6] = pkg.location
		data[7] = pkg.parsed_version

		self.app.hooks.run_hook('np.cli.module.show', self.app, columns, data)
		return (columns, data)

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
		raise NotImplementedError('Not implemented.')

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

# Taken nearly verbatim from alembic.config:CommandLine
class Alembic(Command):
	"""
	Invoke alembic migration commands directly.
	"""

	log = logging.getLogger(__name__)

	def get_parser(self, prog_name):
		kwargs_opts = {
			'template': (
				'-t', '--template',
				dict(
					default='generic',
					type=str,
					help='Setup template for use with \'init\'.'
				)
			),
			'message': (
				'-m', '--message',
				dict(
					type=str,
					help='Message string to use with \'revision\'.'
				)
			),
			'sql': (
				'-S', '--sql',
				dict(
					action='store_true',
					help='Don\'t emit SQL to database - dump to standard output/file instead.'
				)
			),
			'tag': (
				'--tag',
				dict(
					type=str,
					help='Arbitrary \'tag\' name - can be used by custom env.py scripts.'
				)
			),
			'head': (
				'--head',
				dict(
					type=str,
					help='Specify head revision or <branchname>@head to base new revision on.'
				)
			),
			'splice': (
				'--splice',
				dict(
					action='store_true',
					help='Allow a non-head revision as the \'head\' to splice onto.'
				)
			),
			'depends_on': (
				'-D', '--depends-on',
				dict(
					action='append',
					help='Specify one or more revision identifiers which this revision should depend on.'
				)
			),
			'rev_id': (
				'-R', '--rev-id',
				dict(
					type=str,
					help='Specify a hardcoded revision id instead of generating one.'
				)
			),
			'version_path': (
				'--version-path',
				dict(
					type=str,
					help='Specify specific path from config for version file.'
				)
			),
			'branch_label': (
				'--branch-label',
				dict(
					type=str,
					help='Specify a branch label to apply to the new revision.'
				)
			),
			'verbose': (
				'-V', '--alembic-verbose',
				dict(
					action='store_true',
					help='Use more verbose output.'
				)
			),
			'resolve_dependencies': (
				'--resolve-dependencies',
				dict(
					action='store_true',
					help='Treat dependency versions as down revisions.'
				)
			),
			'autogenerate': (
				'-A', '--autogenerate',
				dict(
					action='store_true',
					help='Populate revision script with candidate migration operations, based on comparison of database to model.'
				)
			),
			'head_only': (
				'--head-only',
				dict(
					action='store_true',
					help='Deprecated.  Use --verbose for additional output.'
				)
			),
			'rev_range': (
				'-r', '--rev-range',
				dict(
					action='store',
					help='Specify a revision range; format is [start]:[end].'
				)
			)
		}
		positional_help = {
			'directory' : 'Location of scripts directory.',
			'revision'  : 'Revision identifier.',
			'revisions' : 'One or more revisions, or \'heads\' for all heads.'
		}

		parser = super(Alembic, self).get_parser(prog_name)
		parser.add_argument(
			'-x', action='append',
			help='Additional arguments consumed by custom env.py scripts, e.g. -x setting1=somesetting -x setting2=somesetting.'
		)
		subparsers = parser.add_subparsers(help='Help for Alembic commands.')

		for fn in [getattr(alembic_cmd, n) for n in dir(alembic_cmd)]:
			if inspect.isfunction(fn) and fn.__name__[0] != '_' and fn.__module__ == 'alembic.command':
				spec = inspect.getargspec(fn)
				if spec[3]:
					positional = spec[0][1:-len(spec[3])]
					kwargs = spec[0][-len(spec[3]):]
				else:
					positional = spec[0][1:]
					kwargs = []

				subparser = subparsers.add_parser(
					fn.__name__,
					help=fn.__doc__
				)

				for arg in kwargs:
					if arg in kwargs_opts:
						pa_args = kwargs_opts[arg]
						pa_args, pa_kwargs = pa_args[0:-1], pa_args[-1]
						subparser.add_argument(*pa_args, **pa_kwargs)
				for arg in positional:
					if arg == 'revisions':
						subparser.add_argument(arg, nargs='+', help=positional_help.get(arg))
					else:
						subparser.add_argument(arg, help=positional_help.get(arg))

				subparser.set_defaults(cmd=(fn, positional, kwargs))

		return parser

	def take_action(self, args):
		from netprofile.db import migrations

		self.app.setup_mako_sql()
		mm = self.app.mm

		if len(mm.modules) > 0:
			mm.rescan()
		else:
			mm.scan()
		if not mm.load('core'):
			raise RuntimeError('Unable to proceed without core module.')
		mm.load_all()

		if not hasattr(args, 'cmd'):
			raise RuntimeError('too few arguments')

		if self.app.options.verbose_level > 1:
			args.verbose = True
		elif 'alembic_verbose' in args:
			args.verbose = args.alembic_verbose
		else:
			args.verbose = False

		fn, positional, kwargs = args.cmd

		cfg = self.app.alembic_config
		fn(
			cfg,
			*[getattr(args, k) for k in positional],
			**dict((k, getattr(args, k)) for k in kwargs)
		)

class DBRevision(Command):
	"""
	Create new database revision.
	"""

	log = logging.getLogger(__name__)

	def get_parser(self, prog_name):
		parser = super(DBRevision, self).get_parser(prog_name)
		parser.add_argument(
			'-m', '--message',
			help='Message string to use.'
		)
		parser.add_argument(
			'-A', '--autogenerate',
			action='store_true',
			help='Populate revision script with candidate migration operations, based on comparison of database to model.'
		)
		parser.add_argument(
			'-S', '--sql',
			action='store_true',
			help='Don\'t emit SQL to database - dump to standard output/file instead.'
		)
		parser.add_argument(
			'-R', '--rev-id',
			help='Specify a hardcoded revision id instead of generating one.'
		)
		parser.add_argument(
			'-D', '--depends-on',
			action='append',
			help='Specify one or more revision identifiers which this revision should depend on.'
		)
		# this is equivalent to alembic's --branch-label=moddef
		parser.add_argument(
			'-I', '--initial',
			action='store_true',
			help='This revision is an initial one for a module.'
		)
		parser.add_argument(
			'name',
			help='Name of the module to create DB revision for.'
		)
		return parser

	def take_action(self, args):
		from netprofile.db import migrations

		self.app.setup_mako_sql()
		mm = self.app.mm

		if len(mm.modules) > 0:
			mm.rescan()
		else:
			mm.scan()
		if not mm.preload('core'):
			raise RuntimeError('Unable to proceed without core module.')
		moddef = args.name
		if moddef != 'core':
			if not mm.preload(moddef):
				raise RuntimeError('Requested module \'%s\' can\'t be loaded.' % (moddef,))
		mod = mm.modules[moddef]
		version_dir = os.path.join(mod.dist.location, 'migrations')

		cfg = self.app.alembic_config
		cfg.attributes['module'] = moddef
		if not os.path.isdir(version_dir):
			# TODO: create dir, append to version_locations
			if args.initial:
				pass
			else:
				raise RuntimeError('Can\'t find version directory: \'%s\'.' % (version_dir,))

		kwargs = {
			'head'         : moddef + '@head',
			'version_path' : version_dir
		}
		if args.message:
			kwargs['message'] = args.message
		if args.autogenerate:
			kwargs['autogenerate'] = True
		if args.sql:
			kwargs['sql'] = True
		if args.rev_id:
			kwargs['rev_id'] = args.rev_id
		if args.depends_on:
			# TODO: get alembic deps from module deps
			kwargs['depends_on'] = args.depends_on
		if args.initial:
			kwargs['head'] = 'base'
			kwargs['branch_label'] = moddef

		alembic_cmd.revision(cfg, **kwargs)

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

