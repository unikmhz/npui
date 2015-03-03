#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Centralized CLI utility
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
#
# NB: Used only once during initial NetProfile installation.

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import logging
import os
import pkg_resources
import sys

from cliff.app import App
from cliff.interactive import InteractiveApp
from cliff.commandmanager import CommandManager

from pyramid import threadlocal
from pyramid.decorator import reify
from pyramid.paster import get_appsettings
from pyramid.interfaces import IRendererFactory
from pyramid.path import DottedNameResolver
import pyramid_mako

from netprofile import setup_config
from netprofile.db.connection import DBSession
from netprofile.db.clauses import SetVariable
from netprofile.common.modules import ModuleManager
from netprofile.common.hooks import IHookManager
from netprofile.common.locale import sys_localizer

class CLIInteractiveApp(InteractiveApp):
	"""
	cmd2 interactive application for npctl utility
	"""
	def completedefault(self, text, line, begidx, endidx):
		completions = []
		words = line.split()
		num_words = len(words)

		for n, v in self.command_manager:
			idx = 0
			cmd_words = n.split()

			while len(cmd_words) > 0:
				if idx >= num_words:
					completions.append(cmd_words[0])
					break
				cword = cmd_words.pop(0)
				if cword == words[idx]:
					idx += 1
					continue
				if text and cword.startswith(text) and ((idx + 1) == num_words):
					completions.append(cword)
					break

		return sorted(completions)

	def completenames(self, text, line, begidx, endidx):
		dotext = 'do_' + text
		cmds = [a[3:] for a in self.get_names() if a.startswith(dotext)]

		for n, v in self.command_manager:
			word = n.split()[0]
			if (not text) or (word.startswith(text)):
					cmds.append(word)

		return sorted(cmds)

class CLIApplication(App):
	"""
	Cliff application for npctl utility
	"""
	log = logging.getLogger(__name__)

	def __init__(self):
		np = pkg_resources.get_distribution('netprofile')

		super(CLIApplication, self).__init__(
			description='NetProfile CLI utility',
			version=np.version,
			command_manager=CommandManager('netprofile.cli.commands'),
			interactive_app_factory=CLIInteractiveApp
		)

		self._mako_setup = False
		self.dist = np

	def build_option_parser(self, descr, vers, argparse_kwargs=None):
		parser = super(CLIApplication, self).build_option_parser(descr, vers, argparse_kwargs)

		parser.add_argument(
			'-i', '--ini-file',
			metavar='FILE',
			default=self.default_ini_file,
			help='Specify .ini file to use.'
		)
		parser.add_argument(
			'-a', '--application',
			metavar='SECTION',
			default=self.default_ini_name,
			help='Default app section of .ini file to use.'
		)

		return parser

	def initialize_app(self, argv):
		self.log.debug('Starting NetProfile CLI shell')

	def prepare_to_run_command(self, cmd):
		self.log.debug('Running command %s', cmd.__class__.__name__)

	def clean_up(self, cmd, result, err):
		self.log.debug('Finishing command %s', cmd.__class__.__name__)
		if err:
			self.log.debug('Got an error: %s', err)

	@reify
	def default_ini_file(self):
		if 'NP_INI_FILE' in os.environ:
			return os.environ['NP_INI_FILE']
		return 'production.ini'

	@reify
	def default_ini_name(self):
		if 'NP_INI_NAME' in os.environ:
			return os.environ['NP_INI_NAME']
		return 'netprofile'

	@reify
	def locale(self):
		return sys_localizer(self.app_config.registry)

	@reify
	def mm(self):
		return ModuleManager(self.app_config)

	@reify
	def db_session(self):
		sess = DBSession()
		sess.execute(SetVariable('accessuid', 0))
		sess.execute(SetVariable('accessgid', 0))
		sess.execute(SetVariable('accesslogin', '[NPCTL]'))
		return sess

	@reify
	def app_config(self):
		config_uri = '#'.join((
			self.options.ini_file,
			self.options.application
		))
		settings = get_appsettings(config_uri)

		cfg = setup_config(settings)
		cfg.commit()
		return cfg

	@reify
	def hooks(self):
		return self.app_config.registry.getUtility(IHookManager)

	def setup_mako_sql(self):
		if self._mako_setup:
			return
		reg = threadlocal.get_current_registry()
		factory = pyramid_mako.MakoRendererFactory()

		name_resolver = DottedNameResolver()
		lookup_opts = pyramid_mako.parse_options_from_settings(
			self.app_config.registry.settings,
			'mako.',
			name_resolver.maybe_resolve
		)
		lookup_opts.update({
			'default_filters' : ['context[\'self\'].ddl.ddl_fmt']
		})
		factory.lookup = pyramid_mako.PkgResourceTemplateLookup(**lookup_opts)

		reg.registerUtility(factory, IRendererFactory, name='.mak')
		self._mako_setup = True

def main(argv=sys.argv[1:]):
	app = CLIApplication()
	return app.run(argv)

if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))

