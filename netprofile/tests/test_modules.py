#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Tests for modules API
# © Copyright 2016 Alex 'Unik' Unigovsky
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

import unittest
try:
	from unittest import mock
except ImportError:
	import mock

# Test body begins here

import packaging
from sqlalchemy.exc import (
	DatabaseError,
	ProgrammingError
)
from sqlalchemy.orm.exc import NoResultFound
from netprofile import (
	main,
	__version__
)
from netprofile.common.modules import (
	ModuleBase,
	ModuleManager,
	VersionPair
)
from netprofile.db.connection import DBSession

def _ver(spec):
	return packaging.version.Version(spec)

def _no_result(*args, **kwargs):
	raise NoResultFound

def _prog_error(*args, **kwargs):
	raise ProgrammingError('', [], DatabaseError)

class TestModulesAPI(unittest.TestCase):
	def setUp(self):
		from netprofile.common import cache
		cache.cache = cache.configure_cache({
			'netprofile.cache.backend' : 'dogpile.cache.memory'
		})

	def test_version_pairs(self):
		vp12 = VersionPair('1.0', '2.0')
		self.assertEqual(vp12.old, _ver('1.0'))
		self.assertEqual(vp12.new, _ver('2.0'))
		self.assertFalse(vp12.is_install)
		self.assertFalse(vp12.is_uninstall)
		self.assertTrue(vp12.is_upgrade)
		self.assertFalse(vp12.is_downgrade)
		self.assertFalse(vp12.is_noop)
		self.assertTrue(vp12.is_upgrade_from('1.4'))
		self.assertFalse(vp12.is_downgrade_to('1.4'))

		vp21 = VersionPair('2.0', '1.0')
		self.assertFalse(vp21.is_upgrade)
		self.assertTrue(vp21.is_downgrade)
		self.assertFalse(vp21.is_upgrade_from('1.4'))
		self.assertTrue(vp21.is_downgrade_to('1.4'))

		vpi = VersionPair(None, '1.0')
		self.assertTrue(vpi.is_install)
		self.assertFalse(vpi.is_uninstall)
		self.assertFalse(vpi.is_upgrade)
		self.assertFalse(vpi.is_downgrade)

		vpu = VersionPair('2.0', None)
		self.assertFalse(vpu.is_install)
		self.assertTrue(vpu.is_uninstall)
		self.assertFalse(vpu.is_upgrade)
		self.assertFalse(vpu.is_downgrade)

	def test_module_base(self):
		vers = ModuleBase.version.__func__(main)
		self.assertEqual(vers, packaging.version.parse(__version__))

	def test_module_base_defaults(self):
		self.assertEqual(ModuleBase.get_deps(), ())
		self.assertIsNone(ModuleBase.install(None))
		self.assertIsNone(ModuleBase.uninstall(None))
		self.assertIsNone(ModuleBase.upgrade(None, None))
		self.assertEqual(ModuleBase.get_models(), ())
		self.assertEqual(ModuleBase.get_sql_functions(), ())
		self.assertEqual(ModuleBase.get_sql_views(), ())
		self.assertEqual(ModuleBase.get_sql_events(), ())
		self.assertIsNone(ModuleBase.get_sql_data(None, None, None))

		cfg = mock.MagicMock()
		mm = ModuleManager(cfg)
		mod = ModuleBase(mm)

		self.assertIsNone(mod.add_routes(None))
		self.assertEqual(mod.get_menus(None), ())
		self.assertEqual(mod.get_js(None), ())
		self.assertEqual(mod.get_local_js(None, 'en'), ())
		self.assertEqual(mod.get_css(None), ())
		self.assertEqual(mod.get_autoload_js(None), ())
		self.assertEqual(mod.get_controllers(None), ())
		self.assertEqual(mod.get_rt_handlers(), {})
		self.assertEqual(mod.get_rt_routes(), ())
		self.assertEqual(mod.get_dav_plugins(None), {})
		self.assertEqual(mod.get_task_imports(), ())
		self.assertIsNone(mod.load())
		self.assertIsNone(mod.unload())
		self.assertEqual(mod.get_settings(), ())
		self.assertEqual(mod.name, 'netprofile.common.modules')

	def test_module_manager(self):
		cfg = mock.MagicMock()
		cfg.get_settings.return_value = {'netprofile.vhost' : 'test1'}

		mm = ModuleManager(cfg)
		self.assertIs(mm.cfg, cfg)
		self.assertEqual(mm.vhost, 'test1')

		mm = ModuleManager(cfg, vhost='test2')
		self.assertEqual(mm.vhost, 'test2')

	@mock.patch('pkg_resources.iter_entry_points')
	def test_module_scan(self, iep):
		entry_point = mock.MagicMock()
		entry_point.name = 'netprofile'
		iep.return_value = [entry_point, entry_point]
		cfg = mock.MagicMock()

		mm = ModuleManager(cfg)
		ret = mm.scan()

		iep.assert_called_once_with('netprofile.modules')
		self.assertEqual(ret, ['netprofile'])

	@mock.patch('pkg_resources.iter_entry_points')
	@mock.patch('pkg_resources.working_set.find_plugins')
	def test_module_rescan(self, fplug, iep):
		cfg = mock.MagicMock()
		mm = ModuleManager(cfg)

		old_mod = ('exists',)
		new_mod = ('netprofile', 'netprofile-test', 'netprofile-exists', 'np-wrong')
		new_mocks = []
		for mod in old_mod:
			ep = mock.MagicMock()
			ep.name = ep.project_name = mod
			mm.modules[mod] = ep
		for mod in new_mod:
			ep = mock.MagicMock()
			ep.name = ep.project_name = mod
			new_mocks.append(ep)

		fplug.return_value = [new_mocks, []]
		iep.return_value = new_mocks

		ret = mm.rescan()

		fplug.assert_called_once()
		iep.assert_called_once_with('netprofile.modules')
		self.assertEqual(ret, ['test'])

	def test_module_is_installed(self):
		cfg = mock.MagicMock()
		mm = ModuleManager(cfg)

		self.assertFalse(mm.is_installed('mod', None))
		mm.loaded['core'] = True

		sess = mock.MagicMock()
		mod = mock.MagicMock()
		mod.name = 'mod'
		mod.parsed_version = _ver('2.0')
		sess.query.return_value = [mod]

		self.assertTrue(mm.is_installed('mod', sess))
		self.assertFalse(mm.is_installed('notfound', sess))

		mod = mock.MagicMock()
		mod.version.return_value = _ver('2.0')
		mm.loaded['mod'] = mod
		self.assertTrue(mm.is_installed('mod == 2.0', None))
		self.assertFalse(mm.is_installed('mod == 1.0', None))

		mm.installed = None
		sess.query.side_effect = _prog_error
		self.assertFalse(mm.is_installed('errormod', sess))

	def test_module_load(self):
		cfg = mock.MagicMock()
		mm = ModuleManager(cfg)

		found = mock.MagicMock()
		mm.modules['found'] = found

		self.assertFalse(mm.load('notfound'))
		self.assertFalse(mm.load('found'))

		version_loaded = mock.MagicMock()
		version_loaded.version.return_value = _ver('1.0')
		mm.loaded['vmod'] = version_loaded
		self.assertFalse(mm.load('vmod == 2.0'))
		self.assertTrue(mm.load('vmod == 1.0'))

		mm.installed = {}
		mm.loaded['core'] = True

		ep1 = mock.MagicMock()
		ep1.load.side_effect = ImportError
		mm.installed['mod1'] = _ver('1.0')
		mm.modules['mod1'] = ep1
		self.assertFalse(mm.load('mod1'))

		with mock.patch('netprofile.common.modules.ModuleBase.version') as mock_version:
			mock_version.return_value = _ver('1.0')

			ep2 = mock.MagicMock()
			ep2.version.return_value = _ver('1.0')
			mm.installed['mod2'] = _ver('1.0')
			mm.modules['mod2'] = ep2
			ep2.load.return_value = ModuleBase
			self.assertTrue(mm.load('mod2'))
			ep2.load.assert_called_once_with()

			ep3 = mock.MagicMock()
			ep3.version.return_value = _ver('1.0')
			mm.installed['mod3'] = _ver('1.0')
			mm.modules['mod3'] = ep3
			ep3.load.return_value = mock.MagicMock
			self.assertFalse(mm.load('mod3'))
			ep3.load.assert_called_once_with()

			ep4 = mock.MagicMock()
			ep4.version.return_value = _ver('2.0')
			mm.installed['mod4'] = _ver('2.0')
			mm.modules['mod4'] = ep4
			ep4.load.return_value = ModuleBase
			self.assertFalse(mm.load('mod4 == 2.0'))
			ep4.load.assert_called_once_with()

			with mock.patch('netprofile.common.modules.ModuleBase.get_deps') as mock_deps:
				mock_deps.return_value = ('mod5',)

				ep5 = mock.MagicMock()
				ep5.version.return_value = _ver('1.0')
				mm.installed['mod5'] = _ver('1.0')
				mm.modules['mod5'] = ep5
				ep5.load.return_value = ModuleBase
				self.assertTrue(mm.load('mod5'))
				ep5.load.assert_called_once_with()
				mock_deps.assert_called_once_with()

				mock_deps.reset_mock()
				mock_deps.return_value = ('missing',)

				ep6 = mock.MagicMock()
				ep6.version.return_value = _ver('1.0')
				mm.installed['mod6'] = _ver('1.0')
				mm.modules['mod6'] = ep6
				ep6.load.return_value = ModuleBase
				self.assertFalse(mm.load('mod6'))
				ep6.load.assert_called_once_with()
				mock_deps.assert_called_once_with()

	@mock.patch('netprofile.common.modules.ModuleBase.get_sql_events')
	@mock.patch('netprofile.common.modules.ModuleBase.get_sql_views')
	@mock.patch('netprofile.common.modules.ModuleBase.get_sql_functions')
	@mock.patch('netprofile.common.modules.ModuleBase.get_models')
	@mock.patch('netprofile.common.modules.ModuleBase.version')
	@mock.patch('netprofile.common.modules.ModuleManager._import_model')
	def test_module_load_import(self, import_model, mock_version, get_models, get_sqlfunc, get_sqlview, get_sqlevt):
		mock_version.return_value = _ver('1.0')
		get_models.return_value = (mock.MagicMock(),)
		get_sqlfunc.return_value = (mock.MagicMock(),)
		get_sqlview.return_value = (mock.MagicMock(),)
		get_sqlevt.return_value = (mock.MagicMock(),)

		cfg = mock.MagicMock()
		mm = ModuleManager(cfg)
		mm.installed = {}
		mm.loaded['core'] = True

		ep1 = mock.MagicMock()
		ep1.version.return_value = mm.installed['mod1'] = _ver('1.0')
		ep1.load.return_value = ModuleBase
		mm.modules['mod1'] = ep1

		mm.load('mod1')
		get_models.assert_called_once_with()
		import_model.assert_called_once()
		get_sqlfunc.assert_called_once_with()
		get_sqlview.assert_called_once_with()
		get_sqlevt.assert_called_once_with()

	@mock.patch('netprofile.common.modules.ModuleBase.version')
	def test_module_preload(self, mock_version):
		mock_version.return_value = _ver('1.0')

		cfg = mock.MagicMock()
		mm = ModuleManager(cfg)
		mm.installed = {}
		mm.loaded['core'] = True

		ep1 = mock.MagicMock()
		ep1.version.return_value = mm.installed['mod1'] = _ver('1.0')
		ep1.load.return_value = ModuleBase
		mm.modules['mod1'] = ep1
		self.assertTrue(mm.preload('mod1'))
		ep1.load.assert_called_once_with()

	@mock.patch('sqlalchemy.orm.session.Session.query')
	@mock.patch('netprofile.common.modules.ModuleBase.version')
	def test_module_enable(self, mock_version, query):
		mock_version.return_value = _ver('1.0')

		cfg = mock.MagicMock()
		mm = ModuleManager(cfg)
		mm.installed = {}
		mm.loaded['core'] = True

		self.assertFalse(mm.enable('missing'))

		query.side_effect = _no_result

		ep1 = mock.MagicMock()
		mm.modules['mod1'] = ep1
		self.assertFalse(mm.enable('mod1'))
		query.assert_called_once()

		modobj = mock.MagicMock()
		enabled = mock.PropertyMock(return_value=False)
		type(modobj).enabled = enabled
		query.reset_mock()
		query.side_effect = None
		query.return_value.filter.return_value.one.return_value = modobj

		ep2 = mock.MagicMock()
		ep2.version.return_value = mm.installed['mod2'] = _ver('1.0')
		ep2.load.return_value = ModuleBase
		mm.modules['mod2'] = ep2
		self.assertTrue(mm.enable('mod2'))
		enabled.assert_called_with(True)

		enabled.return_value = True
		enabled.reset_mock()
		ep3 = mock.MagicMock()
		ep3.version.return_value = mm.installed['mod3'] = _ver('1.0')
		ep3.load.return_value = ModuleBase
		mm.modules['mod3'] = ep3
		self.assertTrue(mm.enable('mod3'))
		enabled.assert_called_once_with()

	@mock.patch('sqlalchemy.orm.session.Session.query')
	@mock.patch('netprofile.common.modules.ModuleBase.version')
	def test_module_disable(self, mock_version, query):
		mock_version.return_value = _ver('1.0')

		cfg = mock.MagicMock()
		mm = ModuleManager(cfg)
		mm.installed = {}
		mm.loaded['core'] = True

		self.assertFalse(mm.disable('missing'))

		query.side_effect = _no_result

		ep1 = mock.MagicMock()
		mm.modules['mod1'] = ep1
		self.assertFalse(mm.disable('mod1'))
		query.assert_called_once()

		modobj = mock.MagicMock()
		enabled = mock.PropertyMock(return_value=True)
		type(modobj).enabled = enabled
		query.reset_mock()
		query.side_effect = None
		query.return_value.filter.return_value.one.return_value = modobj

		ep2 = mock.MagicMock()
		ep2.version.return_value = mm.installed['mod2'] = _ver('1.0')
		ep2.load.return_value = ModuleBase
		mm.modules['mod2'] = ep2
		self.assertTrue(mm.disable('mod2'))
		enabled.assert_called_with(False)

		enabled.return_value = False
		enabled.reset_mock()
		ep3 = mock.MagicMock()
		ep3.version.return_value = mm.installed['mod3'] = _ver('1.0')
		ep3.load.return_value = ModuleBase
		mm.modules['mod3'] = ep3
		self.assertTrue(mm.disable('mod3'))
		enabled.assert_called_once_with()

	@mock.patch('netprofile.common.modules.ModuleManager.load')
	@mock.patch('sqlalchemy.orm.session.Session.query')
	def test_load_all(self, query, load):
		mod_names = ['core', 'mod1', 'mod2']
		mods = []
		for modname in mod_names:
			mod = mock.MagicMock()
			name = mock.PropertyMock(return_value=modname)
			type(mod).name = name
			mods.append(mod)
		query.return_value = mods

		cfg = mock.MagicMock()
		mm = ModuleManager(cfg)
		self.assertTrue(mm.load_all())

		load.assert_has_calls((
			mock.call('mod1'),
			mock.call('mod2')
		))

		query.side_effect = _prog_error
		self.assertFalse(mm.load_all())

	@mock.patch('netprofile.common.modules.ModuleManager.load')
	@mock.patch('sqlalchemy.orm.session.Session.query')
	def test_load_enabled(self, query, load):
		mod_names = ['core', 'mod1', 'mod2']
		mods = []
		for modname in mod_names:
			mod = mock.MagicMock()
			name = mock.PropertyMock(return_value=modname)
			type(mod).name = name
			mods.append(mod)
		query.return_value.filter.return_value = mods

		cfg = mock.MagicMock()
		mm = ModuleManager(cfg)
		self.assertTrue(mm.load_enabled())

		load.assert_has_calls((
			mock.call('mod1'),
			mock.call('mod2')
		))

		query.side_effect = _prog_error
		self.assertFalse(mm.load_enabled())

