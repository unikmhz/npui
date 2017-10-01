#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Tests for modules API
# Copyright © 2016-2017 Alex Unigovsky
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

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

import unittest
import mock

# Test body begins here

import packaging
from pyramid import testing
from sqlalchemy.exc import (
    DatabaseError,
    ProgrammingError
)
from sqlalchemy.orm.exc import NoResultFound
from netprofile import main
from netprofile.common.modules import (
    IModuleManager,
    ModuleBase,
    ModuleError,
    ModuleManager,
    VersionPair,
    includeme
)


def _ver(spec):
    return packaging.version.Version(spec)


def _req(spec):
    return packaging.requirements.Requirement(spec)


def _no_result(*args, **kwargs):
    raise NoResultFound


def _prog_error(*args, **kwargs):
    raise ProgrammingError('', [], DatabaseError)


class TestModulesAPI(unittest.TestCase):
    def setUp(self):
        from netprofile.common import cache
        cache.cache = cache.configure_cache({
            'netprofile.cache.backend': 'dogpile.cache.memory'
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
        self.assertTrue(vp12.is_upgrade_from(_ver('1.4')))
        self.assertFalse(vp12.is_downgrade_to('1.4'))
        self.assertFalse(vp12.is_downgrade_to(_ver('1.4')))

        vp21 = VersionPair('2.0', '1.0')
        self.assertFalse(vp21.is_upgrade)
        self.assertTrue(vp21.is_downgrade)
        self.assertFalse(vp21.is_upgrade_from('1.4'))
        self.assertFalse(vp21.is_upgrade_from(_ver('1.4')))
        self.assertTrue(vp21.is_downgrade_to('1.4'))
        self.assertTrue(vp21.is_downgrade_to(_ver('1.4')))

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

    @mock.patch('pkg_resources.get_distribution')
    def test_module_base(self, get_dist):
        get_dist.return_value = None
        vers = ModuleBase.version.__func__(main)
        self.assertIsNone(vers)

        get_dist.return_value = mock.MagicMock(version='1.0')
        vers = ModuleBase.version.__func__(main)
        self.assertEqual(vers, _ver('1.0'))

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
        cfg.get_settings.return_value = {'netprofile.vhost': 'test1'}

        mm = ModuleManager(cfg)
        self.assertIs(mm.cfg, cfg)
        self.assertEqual(mm.vhost, 'test1')

        mm = ModuleManager(cfg, vhost='test2')
        self.assertEqual(mm.vhost, 'test2')

    @mock.patch('pkg_resources.iter_entry_points')
    def test_module_scan(self, iep):
        ep1 = mock.MagicMock()
        type(ep1).name = mock.PropertyMock(return_value='netprofile')
        ep1.dist.project_name = 'netprofile'

        ep2 = mock.MagicMock()
        type(ep2).name = mock.PropertyMock(return_value='core')
        ep2.dist.project_name = 'netprofile-core'

        ep3 = mock.MagicMock()
        type(ep3).name = mock.PropertyMock(return_value='test')
        ep3.dist.project_name = 'netprofile-nottest'

        iep.return_value = [ep1, ep1, ep2, ep2, ep3]
        cfg = mock.MagicMock()

        mm = ModuleManager(cfg)
        ret = mm.scan()

        iep.assert_called_once_with('netprofile.modules')
        self.assertEqual(ret, ['core'])

    @mock.patch('pkg_resources.iter_entry_points')
    @mock.patch('pkg_resources.working_set.find_plugins')
    def test_module_rescan(self, fplug, iep):
        cfg = mock.MagicMock()
        mm = ModuleManager(cfg)

        old_mod = ('exists1', 'exists2')
        new_mod = (('netprofile', 'netprofile'),
                   ('test1', 'netprofile-test1'),
                   ('test2', 'test2'),
                   ('test3', 'netprofile-whatever'),
                   ('exists1', 'netprofile-exists1'),
                   ('exists2', 'wrong-exists2'),
                   ('wrong1', 'np-wrong1'),
                   ('wrong2', 'np-whatever'))

        for mod in old_mod:
            ep = mock.MagicMock()
            type(ep).name = mock.PropertyMock(return_value=mod)
            ep.dist.project_name = 'netprofile-' + mod
            mm.modules[mod] = ep

        new_dists = []
        new_eps = []

        def _new_mod(mod_name, dist_name):
            ep = mock.MagicMock()
            dist = mock.MagicMock()
            type(ep).name = mock.PropertyMock(return_value=mod_name)
            dist.project_name = dist_name
            ep.dist = dist
            new_eps.append(ep)
            new_dists.append(dist)

        for mod_name, dist_name in new_mod:
            _new_mod(mod_name, dist_name)

        fplug.return_value = [new_dists, []]
        iep.return_value = new_eps

        ret = mm.rescan()

        fplug.assert_called_once()
        iep.assert_called_once_with('netprofile.modules')
        self.assertEqual(ret, ['test1'])

        fplug.reset_mock()
        iep.reset_mock()
        new_dists = []
        new_eps = []

        new_mod = (
            ('test1', 'netprofile-test1'),
            ('wrong', 'np-wrong')
        )

        for mod_name, dist_name in new_mod:
            _new_mod(mod_name, dist_name)

        fplug.return_value = [new_dists, []]
        iep.return_value = new_eps

        ret = mm.rescan()

        fplug.assert_called_once()
        iep.assert_not_called()
        self.assertEqual(ret, [])

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

        mm.modules['core'] = mock.MagicMock()
        self.assertFalse(mm.load('core'))

        mm.loaded['core'] = True

        ep1 = mock.MagicMock()
        ep1.load.side_effect = ImportError
        mm.installed['mod1'] = _ver('1.0')
        mm.modules['mod1'] = ep1
        self.assertFalse(mm.load('mod1'))

        with mock.patch(
                'netprofile.common.modules.ModuleBase.version'
                    ) as mock_version:
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

            with mock.patch(
                    'netprofile.common.modules.ModuleBase.get_deps'
                        ) as mock_deps:
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

            ep7 = mock.MagicMock()
            ep7.version.return_value = _ver('1.0')
            mm.installed['mod7'] = _ver('1.0')
            mm.modules['mod7'] = ep7
            ep7.load.return_value = ModuleBase
            self.assertTrue(mm.load(_req('mod7 > 0.9')))
            ep7.load.assert_called_once_with()

            def _cfg_include(func, route_prefix=None):
                func(cfg)

            mm.cfg.include.side_effect = _cfg_include
            with mock.patch(
                    'netprofile.common.modules.ModuleBase.add_routes'
                        ) as add_routes:
                ep8 = mock.MagicMock()
                ep8.version.return_value = _ver('1.0')
                mm.installed['mod8'] = _ver('1.0')
                mm.modules['mod8'] = ep8
                ep8.load.return_value = ModuleBase
                self.assertTrue(mm.load(_req('mod8 > 0.9')))
                ep8.load.assert_called_once_with()
                add_routes.assert_called_once_with(mm.cfg)

    @mock.patch('netprofile.common.modules.ModuleBase.get_sql_events')
    @mock.patch('netprofile.common.modules.ModuleBase.get_sql_views')
    @mock.patch('netprofile.common.modules.ModuleBase.get_sql_functions')
    @mock.patch('netprofile.common.modules.ModuleBase.get_models')
    @mock.patch('netprofile.common.modules.ModuleBase.version')
    @mock.patch('netprofile.common.modules.ModuleManager._import_model')
    def test_module_load_import(self, import_model, mock_version,
                                get_models, get_sqlfunc,
                                get_sqlview, get_sqlevt):
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
        ep1.module_name = 'netprofile_mod1'
        ep1.load.return_value = ModuleBase
        mm.modules['mod1'] = ep1

        self.assertTrue(mm.load('mod1'))
        cfg.add_static_view.assert_called_once_with('static/mod1',
                                                    'netprofile_mod1:static',
                                                    cache_max_age=3600)
        cfg.commit.assert_called_once_with()
        cfg.scan.assert_called_once_with('netprofile_mod1')
        get_models.assert_called_once_with()
        import_model.assert_called_once()
        get_sqlfunc.assert_called_once_with()
        get_sqlview.assert_called_once_with()
        get_sqlevt.assert_called_once_with()

    @mock.patch('netprofile.common.modules.ModuleBase.version')
    def test_module_load_no_scan(self, mock_version):
        mock_version.return_value = _ver('1.0')

        class ModuleBaseNoScan(ModuleBase):
            enable_scan = False

        cfg = mock.MagicMock()
        mm = ModuleManager(cfg)
        mm.installed = {}
        mm.loaded['core'] = True

        ep1 = mock.MagicMock()
        ep1.version.return_value = mm.installed['mod1'] = _ver('1.0')
        ep1.module_name = 'netprofile_mod1'
        ep1.load.return_value = ModuleBaseNoScan
        mm.modules['mod1'] = ep1

        self.assertTrue(mm.load('mod1'))
        cfg.scan.assert_not_called()

    @mock.patch('netprofile.common.modules.ModuleBase.get_sql_events',
                new_callable=mock.NonCallableMagicMock)
    @mock.patch('netprofile.common.modules.ModuleBase.get_sql_views',
                new_callable=mock.NonCallableMagicMock)
    @mock.patch('netprofile.common.modules.ModuleBase.get_sql_functions',
                new_callable=mock.NonCallableMagicMock)
    @mock.patch('netprofile.common.modules.ModuleBase.get_models',
                new_callable=mock.NonCallableMagicMock)
    @mock.patch('netprofile.common.modules.ModuleBase.version')
    @mock.patch('netprofile.common.modules.ModuleManager._import_model')
    def test_module_load_import_no_methods(self, import_model, mock_version,
                                           get_models, get_sqlfunc,
                                           get_sqlview, get_sqlevt):
        mock_version.return_value = _ver('1.0')

        cfg = mock.MagicMock()
        mm = ModuleManager(cfg)
        mm.installed = {}
        mm.loaded['core'] = True

        ep1 = mock.MagicMock()
        ep1.version.return_value = mm.installed['mod1'] = _ver('1.0')
        ep1.load.return_value = ModuleBase
        mm.modules['mod1'] = ep1

        self.assertTrue(mm.load('mod1'))

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

        ep2 = mock.MagicMock()
        ep2.version.return_value = mm.installed['mod2'] = _ver('1.0')
        ep2.load.return_value = ModuleBase
        mm.modules['mod2'] = ep2
        self.assertTrue(mm.preload(_req('mod2 < 2.0')))
        ep2.load.assert_called_once_with()

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

        load.assert_has_calls((mock.call('mod1'),
                               mock.call('mod2')))

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

        load.assert_has_calls((mock.call('mod1'),
                               mock.call('mod2')))

        query.side_effect = _prog_error
        self.assertFalse(mm.load_enabled())

    def test_assert_loaded(self):
        cfg = mock.MagicMock()
        mm = ModuleManager(cfg)
        mm.installed = {}
        mm.loaded['core'] = True

        self.assertIsNone(mm.assert_loaded('core'))
        self.assertIsNone(mm.assert_loaded(['core']))

        with self.assertRaises(ModuleError):
            mm.assert_loaded('missing')

    @mock.patch('pkg_resources.iter_entry_points')
    def test_find_ep(self, iter_ep):
        cfg = mock.MagicMock()
        mm = ModuleManager(cfg)
        mm.installed = {}
        mm.loaded['core'] = True

        ep1 = mock.MagicMock()
        mm.modules['mod1'] = ep1
        self.assertEqual(mm._find_ep('mod1'), ep1)

        iter_ep.return_value = []
        with self.assertRaises(ModuleError):
            mm._find_ep('missing')

        iter_ep.return_value = ['too', 'many']
        with self.assertRaises(ModuleError):
            mm._find_ep('too')

        ep2 = mock.MagicMock()
        ep2_name = mock.PropertyMock(return_value='wrong')
        type(ep2).name = ep2_name
        iter_ep.return_value = [ep2]
        with self.assertRaises(ModuleError):
            mm._find_ep('right')

        ep3 = mock.MagicMock()
        ep3_name = mock.PropertyMock(return_value='mod3')
        type(ep3).name = ep3_name
        iter_ep.return_value = [ep3]
        self.assertEqual(mm._find_ep('mod3'), ep3)
        self.assertIn('mod3', mm.modules)
        self.assertEqual(mm.modules['mod3'], ep3)

    def test_cls_version(self):
        cfg = mock.MagicMock()
        mm = ModuleManager(cfg)

        cls = mock.MagicMock(spec=[])
        self.assertEqual(mm._cls_version(cls), packaging.version.parse('0'))

        cls = mock.MagicMock()
        cls.version.return_value = packaging.version.parse('1')
        self.assertEqual(mm._cls_version(cls), packaging.version.parse('1'))

    def test_import_model(self):
        cfg = mock.MagicMock()
        mm = ModuleManager(cfg)
        hm = mock.MagicMock()
        mb = mock.MagicMock()
        mb.__getitem__.return_value.__getitem__.return_value = 'TEST'

        model1 = mock.MagicMock()
        model1.__name__ = 'testmodel1'
        mm.models['mod1'] = {}

        mm._import_model('mod1', model1, mb, hm, False)
        self.assertEqual(model1.__moddef__, 'mod1')

        model2 = mock.MagicMock()
        model2.__name__ = 'testmodel2'
        mm.models['mod2'] = {}

        mm._import_model('mod2', model2, mb, hm, True)
        self.assertEqual(model2.__moddef__, 'mod2')
        self.assertEqual(mm.models['mod2'], {'testmodel2': model2})
        mb.__getitem__.assert_called_once_with('mod2')
        mb.__getitem__.return_value.__getitem__.assert_called_once_with(
                'testmodel2')
        hm.run_hook.assert_called_once_with('np.model.load', mm, 'TEST')

    @mock.patch('netprofile.common.modules.get_alembic_config')
    @mock.patch('netprofile.common.modules.ModuleManager._cls_version')
    @mock.patch('netprofile.common.modules.ModuleManager._find_ep')
    @mock.patch('netprofile.common.modules.ModuleManager.preload')
    @mock.patch('netprofile.common.modules.ModuleManager.upgrade')
    @mock.patch('netprofile.common.modules.ModuleManager.is_installed')
    @mock.patch('alembic.command.stamp')
    def test_install(self, stamp, is_installed, upgrade, preload, find_ep,
                     cls_ver, get_alembic_cfg):
        cfg = mock.MagicMock()
        sess = mock.MagicMock()
        mm = ModuleManager(cfg)
        mm.installed = {}

        is_installed.return_value = True
        upgrade.return_value = True
        req = 'mod1'

        with self.assertRaises(ModuleError):
            mm.install(req, sess)

        mm.loaded['core'] = True

        self.assertFalse(mm.install(req, sess, allow_upgrades=False))
        upgrade.assert_not_called()
        self.assertTrue(mm.install(req, sess, allow_upgrades=True))
        upgrade.assert_called_once()

        is_installed.return_value = False
        find_ep.side_effect = ModuleError

        with self.assertRaises(ModuleError):
            mm.install(req, sess)
        find_ep.assert_called_once_with(req)

        find_ep.reset_mock()
        find_ep.side_effect = None
        ep = mock.MagicMock()
        find_ep.return_value = ep
        ep.load.side_effect = ImportError

        with self.assertRaises(ModuleError):
            mm.install(req, sess)
        find_ep.assert_called_once_with(req)
        ep.load.assert_called_once_with()

        find_ep.reset_mock()
        ep.load.reset_mock()
        ep.load.side_effect = None

        modcls = mock.MagicMock()
        ep.load.return_value = modcls

        req = 'mod1 >= 2.0'
        cls_ver.return_value = _ver('1.0')

        with self.assertRaises(ModuleError):
            mm.install(req, sess)
        cls_ver.assert_called_once_with(modcls)
        cls_ver.reset_mock()
        req = _req(req)
        with self.assertRaises(ModuleError):
            mm.install(req, sess)
        cls_ver.assert_called_once_with(modcls)

        def _custom_is_installed(req, sess):
            if req.name == 'mod2':
                _custom_is_installed.mod2 = True
                return True
            if req.name == 'mod3':
                _custom_is_installed.mod3 = True
                return False
            return mock.DEFAULT

        is_installed.reset_mock()
        is_installed.side_effect = _custom_is_installed

        req = 'mod1 >= 0.5'
        cls_ver.reset_mock()

        def _custom_get_deps():
            if _custom_get_deps.ran:
                return []
            _custom_get_deps.ran = True
            return mock.DEFAULT
        _custom_get_deps.ran = False

        modcls.get_deps.return_value = ['mod2', 'mod3']
        modcls.get_deps.side_effect = _custom_get_deps

        sqlfunc = mock.MagicMock()
        sqlfunc.create.return_value = 'FUNC SQL'
        modcls.get_sql_functions.return_value = (sqlfunc,)

        sqlview = mock.MagicMock()
        sqlview.create.return_value = 'VIEW SQL'
        modcls.get_sql_views.return_value = (sqlview,)

        sqlevt = mock.MagicMock()
        sqlevt.create.return_value = 'EVENT SQL'
        modcls.get_sql_events.return_value = (sqlevt,)

        alembic_cfg = mock.MagicMock()
        get_alembic_cfg.return_value = alembic_cfg

        self.assertTrue(mm.install(req, sess, allow_upgrades=False))
        modcls.get_deps.assert_has_calls((mock.call(), mock.call()))
        modcls.prepare.assert_has_calls((mock.call(), mock.call()))
        preload.assert_has_calls((mock.call('mod3'), mock.call('mod1')))
        # TODO: test exact calls instead of call count
        self.assertEqual(modcls.get_models.call_count, 2)
        self.assertEqual(modcls.get_sql_functions.call_count, 2)
        self.assertEqual(modcls.get_sql_views.call_count, 2)
        self.assertEqual(modcls.get_sql_data.call_count, 2)
        self.assertEqual(modcls.get_sql_events.call_count, 2)
        modcls.install.assert_has_calls((mock.call(sess), mock.call(sess)))

        sqlfunc.create.assert_has_calls((mock.call('mod3'), mock.call('mod1')))
        sqlview.create.assert_has_calls((mock.call(), mock.call()))
        sqlevt.create.assert_has_calls((mock.call('mod3'), mock.call('mod1')))
        sess.execute.assert_has_calls((mock.call('FUNC SQL'),
                                       mock.call('VIEW SQL'),
                                       mock.call('EVENT SQL'),
                                       mock.call('FUNC SQL'),
                                       mock.call('VIEW SQL'),
                                       mock.call('EVENT SQL')))
        self.assertEqual(sess.add.call_count, 2)
        sess.flush.assert_has_calls((mock.call(), mock.call()))
        get_alembic_cfg.assert_has_calls((mock.call(mm, stdout=mm.stdout),
                                          mock.call(mm, stdout=mm.stdout)))
        stamp.assert_has_calls((mock.call(alembic_cfg, 'mod3@head'),
                                mock.call(alembic_cfg, 'mod1@head')))

        sess.add.reset_mock()
        sess.flush.reset_mock()
        modcls.get_deps = mock.NonCallableMock()
        modcls.prepare = mock.NonCallableMock()
        preload.reset_mock()
        modcls.get_models = mock.NonCallableMock()
        modcls.get_sql_functions = mock.NonCallableMock()
        modcls.get_sql_views = mock.NonCallableMock()
        modcls.get_sql_data = mock.NonCallableMock()
        modcls.get_sql_events = mock.NonCallableMock()
        modcls.install = mock.NonCallableMock()
        get_alembic_cfg.reset_mock()
        stamp.reset_mock()

        self.assertTrue(mm.install(req, sess, allow_upgrades=False))
        preload.assert_called_once_with('mod1')
        self.assertEqual(sess.add.call_count, 1)
        sess.flush.assert_called_once_with()
        get_alembic_cfg.assert_called_once_with(mm, stdout=mm.stdout)
        stamp.assert_called_once_with(alembic_cfg, 'mod1@head')

    @mock.patch('netprofile.common.modules.get_alembic_config')
    @mock.patch('netprofile.common.modules.ModuleManager._cls_version')
    @mock.patch('netprofile.common.modules.ModuleManager._find_ep')
    @mock.patch('netprofile.common.modules.ModuleManager.preload')
    @mock.patch('netprofile.common.modules.ModuleManager.is_installed')
    @mock.patch('alembic.command.stamp')
    def test_install_core(self, stamp, is_installed, preload, find_ep, cls_ver,
                          get_alembic_cfg):
        cfg = mock.MagicMock()
        sess = mock.MagicMock()
        mm = ModuleManager(cfg)
        mm.installed = None

        is_installed.return_value = False
        ep = mock.MagicMock()
        find_ep.return_value = ep
        modcls = mock.MagicMock()
        ep.load.return_value = modcls
        cls_ver.return_value = _ver('1.0')

        alembic_cfg = mock.MagicMock()
        get_alembic_cfg.return_value = alembic_cfg

        self.assertTrue(mm.install('core', sess, allow_upgrades=False))
        modcls.get_deps.assert_called_once_with()
        modcls.prepare.assert_called_once_with()
        preload.assert_not_called()
        modcls.get_models.assert_called_once_with()
        modcls.get_sql_functions.assert_called_once_with()
        modcls.get_sql_views.assert_called_once_with()
        modcls.get_sql_data.assert_called_once()
        modcls.get_sql_events.assert_called_once_with()
        modcls.install.assert_called_once_with(sess)
        sess.flush.assert_called_once_with()
        get_alembic_cfg.assert_called_once_with(mm, stdout=mm.stdout)
        stamp.assert_called_once_with(alembic_cfg, 'core@head')

    @mock.patch('netprofile.common.modules.get_alembic_config')
    @mock.patch('netprofile.common.modules.ModuleManager._cls_version')
    @mock.patch('netprofile.common.modules.ModuleManager._find_ep')
    @mock.patch('netprofile.common.modules.ModuleManager.is_installed')
    @mock.patch('netprofile.common.modules.ModuleManager.preload')
    @mock.patch('netprofile.common.modules.ModuleManager.install')
    @mock.patch('alembic.command.upgrade')
    def test_upgrade(self, upgrade, install, preload, is_installed, find_ep,
                     cls_ver, get_alembic_cfg):
        cfg = mock.MagicMock()
        sess = mock.MagicMock()
        mm = ModuleManager(cfg)
        mm.installed = {}

        with self.assertRaises(ModuleError):
            mm.upgrade('mod1', sess)
        with self.assertRaises(ModuleError):
            mm.upgrade(_req('mod1'), sess)
        is_installed.assert_not_called()

        mm.loaded['core'] = True
        is_installed.return_value = False
        with self.assertRaises(ModuleError):
            mm.upgrade('mod1', sess)
        is_installed.assert_called_once()

        is_installed.reset_mock()
        is_installed.return_value = True

        ep = mock.MagicMock()
        find_ep.return_value = ep
        ep.load.side_effect = ImportError
        with self.assertRaises(ModuleError):
            mm.upgrade('mod1', sess)
        find_ep.assert_called_once_with('mod1')
        ep.load.assert_called_once_with()

        ep.load.reset_mock()
        ep.load.side_effect = None
        modcls = mock.MagicMock()
        ep.load.return_value = modcls

        cls_ver.return_value = _ver('1.0')
        modobj = mock.MagicMock()
        modobj.parsed_version = _ver('1.0')
        sess.query.return_value.filter.return_value.one.return_value = modobj
        with self.assertRaises(ModuleError):
            mm.upgrade('mod1 >= 1.2', sess)
        cls_ver.assert_called_once_with(modcls)

        modobj.parsed_version = _ver('1.2')
        self.assertFalse(mm.upgrade('mod1 >= 1.0', sess))

        cls_ver.reset_mock()
        cls_ver.return_value = _ver('2.0')
        alembic_cfg = mock.MagicMock()
        get_alembic_cfg.return_value = alembic_cfg
        mm.installed['mod2'] = _ver('1.2')
        mm.installed['mod3'] = _ver('1.3')
        is_installed.reset_mock()
        is_installed.side_effect = (True, False, True)
        modcls.get_deps.return_value = ('mod2 == 1.3', 'mod3 == 1.3')
        install.return_value = True

        self.assertTrue(mm.upgrade('mod1 >= 1.0', sess))
        cls_ver.assert_called_once_with(modcls)
        modcls.get_deps.assert_called_once_with()
        modcls.prepare.assert_called_once_with()
        preload.assert_called_once_with('mod1')
        get_alembic_cfg.assert_called_once_with(mm, stdout=mm.stdout)
        upgrade.assert_called_once_with(alembic_cfg, 'mod1@head')
        sess.flush.assert_called_once_with()
        modcls.get_sql_data.assert_called_once()
        modcls.upgrade.assert_called_once()

        cls_ver.reset_mock()
        preload.reset_mock()
        get_alembic_cfg.reset_mock()
        upgrade.reset_mock()
        sess.flush.reset_mock()
        is_installed.reset_mock()
        is_installed.side_effect = None

        modcls.get_deps = mock.NonCallableMock()
        modcls.prepare = mock.NonCallableMock()
        modcls.get_sql_data = mock.NonCallableMock()
        modcls.upgrade = mock.NonCallableMock()

        self.assertTrue(mm.upgrade('mod1 >= 1.0', sess))
        cls_ver.assert_called_once_with(modcls)
        preload.assert_called_once_with('mod1')
        get_alembic_cfg.assert_called_once_with(mm, stdout=mm.stdout)
        upgrade.assert_called_once_with(alembic_cfg, 'mod1@head')
        sess.flush.assert_called_once_with()

    @mock.patch('netprofile.common.modules.get_alembic_config')
    @mock.patch('netprofile.common.modules.ModuleManager.load')
    @mock.patch('netprofile.common.modules.ModuleManager._cls_version')
    @mock.patch('netprofile.common.modules.ModuleManager._find_ep')
    @mock.patch('netprofile.common.modules.ModuleManager.preload')
    @mock.patch('netprofile.common.modules.ModuleManager.is_installed')
    @mock.patch('alembic.command.upgrade')
    def test_upgrade_core(self, upgrade, is_installed, preload, find_ep,
                          cls_ver, load, get_alembic_cfg):
        cfg = mock.MagicMock()
        sess = mock.MagicMock()
        mm = ModuleManager(cfg)
        mm.installed = {'core': _ver('1.0')}

        is_installed.return_value = True
        ep = mock.MagicMock()
        find_ep.return_value = ep
        modcls = mock.MagicMock()
        ep.load.return_value = modcls
        cls_ver.return_value = _ver('2.0')

        modobj = mock.MagicMock()
        modobj.parsed_version = _ver('1.0')
        sess.query.return_value.filter.return_value.one.return_value = modobj

        alembic_cfg = mock.MagicMock()
        get_alembic_cfg.return_value = alembic_cfg

        self.assertTrue(mm.upgrade('core', sess))
        is_installed.assert_called_once()
        find_ep.assert_called_once_with('core')
        ep.load.assert_called_once_with()
        cls_ver.assert_called_once_with(modcls)
        modcls.get_deps.assert_called_once_with()
        modcls.prepare.assert_called_once_with()
        preload.assert_not_called()
        get_alembic_cfg.assert_called_once_with(mm, stdout=mm.stdout)
        upgrade.assert_called_once_with(alembic_cfg, 'core@head')
        sess.flush.assert_called_once_with()
        modcls.get_sql_data.assert_called_once()
        modcls.upgrade.assert_called_once()
        load.assert_called_once_with('core')

    def test_get_module_browser(self):
        from netprofile.ext.data import ExtBrowser

        cfg = mock.MagicMock()
        mm = ModuleManager(cfg)
        mb = mm.get_module_browser()
        self.assertIsInstance(mb, ExtBrowser)

    @mock.patch('pkg_resources.iter_entry_points')
    def test_get_export_formats(self, iep):
        cfg = mock.MagicMock()
        mm = ModuleManager(cfg)

        ep1 = mock.MagicMock()
        type(ep1).name = mock.PropertyMock(return_value='EP1')
        ep1.load.return_value.return_value = 'DATA1'

        ep2 = mock.MagicMock()
        type(ep2).name = mock.PropertyMock(return_value='EP2')
        ep2.load.side_effect = ImportError

        iep.return_value = [ep1, ep2]
        ret = mm.get_export_formats()
        iep.assert_called_once_with('netprofile.export.formats')
        self.assertEqual(ret, {'EP1': 'DATA1'})

    @mock.patch('pkg_resources.iter_entry_points')
    def test_get_export_format(self, iep):
        cfg = mock.MagicMock()
        mm = ModuleManager(cfg)

        iep.return_value = []
        with self.assertRaises(ModuleError):
            mm.get_export_format('EP0')
        iep.assert_called_once_with('netprofile.export.formats', 'EP0')

        ep1 = mock.MagicMock()
        type(ep1).name = mock.PropertyMock(return_value='EP1')
        ep1.load.return_value.return_value = 'DATA1'

        ep2 = mock.MagicMock()
        type(ep2).name = mock.PropertyMock(return_value='EP2')
        ep2.load.side_effect = ImportError

        iep.reset_mock()
        iep.return_value = [ep1]
        ret = mm.get_export_format('EP1')
        iep.assert_called_once_with('netprofile.export.formats', 'EP1')
        self.assertEqual(ret, 'DATA1')

        iep.reset_mock()
        iep.return_value = [ep2]
        with self.assertRaises(ModuleError):
            mm.get_export_format('EP2')
        iep.assert_called_once_with('netprofile.export.formats', 'EP2')

    def test_get_settings(self):
        cfg = mock.MagicMock()
        cfg.get_settings.return_value = {'netprofile.vhost': None}
        mm = ModuleManager(cfg)
        mod1 = mock.MagicMock()
        mod2 = mock.MagicMock()
        mod3 = mock.MagicMock()

        sect1 = mock.MagicMock()
        type(sect1).name = 'sect1'
        sect1.vhost = 'MAIN'
        sect1.scope = 'global'
        mod1.get_settings.return_value = (sect1,)

        sect2 = mock.MagicMock()
        type(sect2).name = 'sect2'
        sect2.vhost = 'MAIN'
        sect2.scope = 'user'
        mod2.get_settings.return_value = (sect2,)

        sect3 = mock.MagicMock()
        type(sect3).name = 'sect3'
        sect3.vhost = 'client'
        sect3.scope = 'global'
        mod3.get_settings.return_value = (sect3,)

        mm.loaded = {'mod1': mod1, 'mod2': mod2, 'mod3': mod3}

        settings = mm.get_settings()
        self.assertEqual(settings, {'mod1': {'sect1': sect1}})

        settings = mm.get_settings('user')
        self.assertEqual(settings, {'mod2': {'sect2': sect2}})

        mm.vhost = 'client'
        mm.get_settings.cache_clear()
        settings = mm.get_settings()
        self.assertEqual(settings, {'mod3': {'sect3': sect3}})

    @mock.patch('netprofile.common.modules.ModuleManager')
    def test_pyramid_include(self, mm):
        import netprofile
        cfg = mock.MagicMock()

        self.assertIsNone(netprofile.inst_mm)
        includeme(cfg)
        cfg.add_translation_dirs.assert_called_once_with('netprofile:locale/')
        mm.assert_called_once_with(cfg)
        mm().scan.assert_called_once_with()
        cfg.registry.registerUtility.assert_called_once_with(mm(),
                                                             IModuleManager)
        self.assertEqual(netprofile.inst_mm, mm())
        includeme(cfg)
        self.assertEqual(netprofile.inst_mm, mm())


class TestModuleGettersAPI(unittest.TestCase):
    def setUp(self):
        from netprofile.common import cache
        cache.cache = cache.configure_cache({
            'netprofile.cache.backend': 'dogpile.cache.memory'
        })
        self.req = testing.DummyRequest()
        self.cfg = testing.setUp(request=self.req)
        self.mm = ModuleManager(self.cfg)
        self.mod_names = ('test1', 'test2', 'empty')
        self.dict = False

    def setup_mocks(self, cb_value):
        for mod_name in self.mod_names:
            mod = mock.MagicMock()
            fn = getattr(mod, self.fn)
            if mod_name.startswith('empty'):
                fn.return_value = {} if self.dict else []
            else:
                fn.return_value = cb_value(mod_name)
            self.mm.loaded[mod_name] = mod

    def assert_getter(self, ret, assert_ret, *args, **kwargs):
        for mod_name in self.mod_names:
            fn = getattr(self.mm.loaded[mod_name], self.fn)
            fn.assert_called_once_with(*args, **kwargs)
        self.assertEqual(ret, assert_ret)

    def tearDown(self):
        testing.tearDown()

    def test_get_js(self):
        self.fn = 'get_js'
        self.setup_mocks(lambda mod: [mod + '.js'])
        ret = self.mm.get_js(self.req)
        self.assert_getter(set(ret), set(['test1.js', 'test2.js']), self.req)

    def test_get_local_js(self):
        self.fn = 'get_local_js'
        self.setup_mocks(lambda mod: [mod + '-loc.js'])
        ret = self.mm.get_local_js(self.req, 'en')
        self.assert_getter(set(ret),
                           set(['test1-loc.js', 'test2-loc.js']),
                           self.req,
                           'en')

    def test_get_css(self):
        self.fn = 'get_css'
        self.setup_mocks(lambda mod: [mod + '.css'])
        ret = self.mm.get_css(self.req)
        self.assert_getter(set(ret), set(['test1.css', 'test2.css']), self.req)

    def test_get_autoload_js(self):
        self.fn = 'get_autoload_js'
        self.setup_mocks(lambda mod: [mod.capitalize()])
        ret = self.mm.get_autoload_js(self.req)
        self.assert_getter(set(ret), set(['Test1', 'Test2']), self.req)

    def test_get_contollers(self):
        self.fn = 'get_controllers'
        self.setup_mocks(lambda mod: [mod.capitalize()])
        ret = self.mm.get_controllers(self.req)
        self.assert_getter(set(ret), set(['Test1', 'Test2']), self.req)

    def test_get_rt_handlers(self):
        self.fn = 'get_rt_handlers'
        self.dict = True
        self.setup_mocks(lambda mod: {mod: mod + '_rt'})
        ret = self.mm.get_rt_handlers(self.req)
        self.assert_getter(ret,
                           {'test1': 'test1_rt', 'test2': 'test2_rt'},
                           self.req)

    def test_get_rt_routes(self):
        self.fn = 'get_rt_routes'
        self.setup_mocks(lambda mod: [mod + '_rt'])
        ret = self.mm.get_rt_routes()
        self.assert_getter(set(ret), set(['test1_rt', 'test2_rt']))

    def test_get_dav_plugins(self):
        self.fn = 'get_dav_plugins'
        self.dict = True
        self.setup_mocks(lambda mod: {mod: 'DAV' + mod.capitalize()})
        ret = self.mm.get_dav_plugins(self.req)
        self.assert_getter(ret,
                           {'test1': 'DAVTest1', 'test2': 'DAVTest2'},
                           self.req)

    def test_get_task_imports(self):
        self.fn = 'get_task_imports'
        self.setup_mocks(lambda mod: [mod])
        ret = self.mm.get_task_imports()
        self.assert_getter(set(ret), set(['test1', 'test2']))

    def test_menu_generator(self):
        menus = {}
        for mod_name in self.mod_names:
            if mod_name.startswith('empty'):
                continue
            menu = mock.MagicMock()
            menus[mod_name] = menu
        self.fn = 'get_menus'
        self.setup_mocks(lambda mod: [menus[mod]])
        ret = list(self.mm.menu_generator(self.req))
        self.assert_getter(set(ret), set(menus.values()), self.req)
        for mod_name, menu in menus.items():
            self.assertEqual(menu.__moddef__, mod_name)
