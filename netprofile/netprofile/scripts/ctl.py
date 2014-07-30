#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Centralized CLI utility
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
#
# NB: Used only once during initial NetProfile installation.

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import os
import locale
import transaction

from argh import (
	ArghParser,

	aliases,
	arg,
	expects_obj,
	named,
	wrap_errors
)

from babel import Locale
from prettytable import PrettyTable
from pyramid import threadlocal
from pyramid.paster import (
	get_appsettings,
	setup_logging
)
from pyramid.interfaces import IRendererFactory
from pyramid.path import DottedNameResolver
from pyramid.i18n import (
	ITranslationDirectories,
	TranslationStringFactory,
	make_localizer
)
import pyramid_mako

from sqlalchemy.exc import ProgrammingError

from netprofile import setup_config
from netprofile.db.connection import DBSession
from netprofile.db.clauses import SetVariable

from netprofile.common.modules import (
	ModuleError,
	ModuleManager
)

_loc = None
_ = TranslationStringFactory('netprofile')

def setup_app(ini_file, app_name):
	config_uri = '#'.join((ini_file, app_name))
	settings = get_appsettings(config_uri)

	cfg = setup_config(settings)
	cfg.commit()
	return cfg

def setup_mako_sql(cfg):
	reg = threadlocal.get_current_registry()
	factory = pyramid_mako.MakoRendererFactory()

	name_resolver = DottedNameResolver()
	lookup_opts = pyramid_mako.parse_options_from_settings(cfg.registry.settings, 'mako.', name_resolver.maybe_resolve)
	lookup_opts.update({
		'default_filters' : ['context[\'self\'].ddl.ddl_fmt']
	})
	factory.lookup = pyramid_mako.PkgResourceTemplateLookup(**lookup_opts)

	reg.registerUtility(factory, IRendererFactory, name='.mak')

def get_loc(cfg):
	global _loc

	reg = cfg.registry
	cur_locale = reg.settings.get('pyramid.default_locale_name', 'en')
	sys_locale = locale.getlocale()[0]

	if sys_locale:
		new_locale = Locale.negotiate(
			(locale.getlocale()[0],),
			reg.settings.get('pyramid.available_languages', '').split()
		)
		if new_locale:
			cur_locale = str(new_locale)
	else:
		cur_locale = 'en'

	tdirs = reg.queryUtility(ITranslationDirectories, default=[])
	_loc = make_localizer(cur_locale, tdirs)
	return _loc

def get_session():
	sess = DBSession()
	sess.execute(SetVariable('accessuid', 0))
	sess.execute(SetVariable('accessgid', 0))
	sess.execute(SetVariable('accesslogin', '[NPCTL]'))
	return sess

@named('list')
@aliases('ls')
@arg('--filter', '-f',
	choices=('all', 'installed', 'uninstalled', 'enabled', 'disabled'),
	default='all',
	help='Show only modules in this state'
)
@expects_obj
def module_list(args):
	"""
	List available/installed modules
	"""
	cfg = setup_app(args.ini_file, args.application)
	loc = get_loc(cfg)
	has_core = True
	flt = args.filter
	try:
		from netprofile_core.models import NPModule
	except ImportError:
		has_core = False

	tr_name = loc.translate(_('Name'))
	tr_avail = loc.translate(_('Available'))
	tr_inst = loc.translate(_('Installed'))
	tr_enab = loc.translate(_('Enabled'))
	mm = ModuleManager(cfg)
	tbl = PrettyTable((
		tr_name,
		tr_avail,
		tr_inst,
		tr_enab
	))
	tbl.align = 'l'
	tbl.align[tr_enab] = 'c'
	tbl.sortby = tr_name
	tbl.padding_width = 2

	installed = {}
	if has_core:
		sess = get_session()
		try:
			for mod in sess.query(NPModule):
				installed[mod.name] = (mod.current_version, mod.enabled)
		except ProgrammingError:
			has_core = False

	for moddef, data in mm.prepare().items():
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
		tbl.add_row((
			moddef,
			data[1],
			loc.translate(curversion),
			loc.translate(enabled)
		))

	return tbl

@named('install')
@aliases('in')
@arg('name',
	help='Name of the module to install or a special value \'all\''
)
@wrap_errors((ModuleError,), processor=lambda e: 'Error: %s' % (e,))
@expects_obj
def module_install(args):
	"""
	Install available module to database
	"""
	cfg = setup_app(args.ini_file, args.application)
	setup_mako_sql(cfg)
	mm = ModuleManager(cfg)
	sess = get_session()
	mm.scan()
	if args.name != 'core':
		mm.load('core')
	mm.load_all()

	if args.name.lower() == 'all':
		mm.install('core', sess)
		for mod in mm.modules:
			if mod != 'core':
				mm.install(mod, sess)
		return 'All done.'

	ret = mm.install(args.name, sess)
	if isinstance(ret, bool):
		if ret:
			return 'Module \'%s\' successfully installed.' % (args.name,)
		else:
			return 'Error: Module \'%s\' is already installed.' % (args.name,)
	return 'Error: Unknown result.'

@named('uninstall')
@aliases('un')
@wrap_errors((ModuleError,), processor=lambda e: 'Error: %s' % (e,))
@expects_obj
@arg('name',
	help='Name of the module to uninstall or a special value \'all\''
)
def module_uninstall(args):
	"""
	Uninstall module from database
	"""
	cfg = setup_app(args.ini_file, args.application)
	setup_mako_sql(cfg)
	mm = ModuleManager(cfg)
	sess = get_session()
	mm.scan()
	raise Exception('Unimplemented')

@named('enable')
@aliases('en')
@arg('name',
	help='Name of the module to enable or a special value \'all\''
)
@wrap_errors((ModuleError,), processor=lambda e: 'Error: %s' % (e,))
@expects_obj
def module_enable(args):
	"""
	Enable installed module
	"""
	cfg = setup_app(args.ini_file, args.application)
	setup_mako_sql(cfg)
	mm = ModuleManager(cfg)
	sess = get_session()
	mm.scan()
	if not mm.load('core'):
		return 'Error: Unable to proceed without core module.'

	if args.name.lower() == 'all':
		for mod in mm.modules:
			if mm.is_installed(mod, sess) and (mod != 'core'):
				mm.enable(mod)
		return 'All done.'

	ret = mm.enable(args.name)
	if isinstance(ret, bool):
		if ret:
			return 'Enabled module \'%s\'.' % (args.name,)
		else:
			return 'Error: Module \'%s\' wasn\'t found or is not installed.' % (args.name,)
	return 'Error: Unknown result.'

@named('disable')
@aliases('dis')
@arg('name',
	help='Name of the module to disable or a special value \'all\''
)
@wrap_errors((ModuleError,), processor=lambda e: 'Error: %s' % (e,))
@expects_obj
def module_disable(args):
	"""
	Disable installed module
	"""
	cfg = setup_app(args.ini_file, args.application)
	setup_mako_sql(cfg)
	mm = ModuleManager(cfg)
	sess = get_session()
	mm.scan()
	if not mm.load('core'):
		return 'Error: Unable to proceed without core module.'

	if args.name.lower() == 'all':
		for mod in mm.modules:
			if mm.is_installed(mod, sess) and (mod != 'core'):
				mm.disable(mod)
		return 'All done.'

	ret = mm.disable(args.name)
	if isinstance(ret, bool):
		if ret:
			return 'Disabled module \'%s\'.' % (args.name,)
		else:
			return 'Error: Module \'%s\' wasn\'t found or is not installed.' % (args.name,)
	return 'Error: Unknown result.'

def main():
	parser = ArghParser()

	parser.add_commands(
		(
			module_list,
			module_install,
			module_uninstall,
			module_enable,
			module_disable
		),
		namespace='module',
		title='Module commands',
		description='Group of commands related to listing or (un)installing modules'
	)

	ini_file='production.ini'
	if 'NP_INI_FILE' in os.environ:
		ini_file = os.environ['NP_INI_FILE']

	ini_name='netprofile'
	if 'NP_INI_NAME' in os.environ:
		ini_name = os.environ['NP_INI_NAME']

	parser.add_argument('--ini-file', '-i', default=ini_file, help='Specify .ini file to use')
	parser.add_argument('--application', '-a', default=ini_name, help='Default app section of .ini file to use')

	parser.dispatch()

