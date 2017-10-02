#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Tests for setup routines and entry points
# Copyright © 2017 Alex Unigovsky
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

from babel import Locale
import netprofile
from netprofile import (
    VHostPredicate,
    get_csrf,
    get_current_locale,
    get_debug,
    get_locales,
    locale_neg,
    main,
    setup_config
)
from netprofile.common.factory import RootFactory


class TestNegotiateLocale(unittest.TestCase):
    def setUp(self):
        req = mock.MagicMock()
        req.locales = {'en': Locale('en'),
                       'ru': Locale('ru')}
        req.accept_language = None
        req.params.get.return_value = None
        req.session.get.return_value = None
        req.registry.settings.get.return_value = 'en'

        self.req = req

    def test_default(self):
        req = self.req
        loc = locale_neg(req)
        self.assertEqual(loc, 'en')
        req.registry.settings.get.assert_called_once_with(
                'pyramid.default_locale_name',
                'en')
        req.session.__setitem__.assert_called_once_with('ui.locale', 'en')

    def test_wrong_default(self):
        self.req.registry.settings.get.return_value = 'fr'
        loc = locale_neg(self.req)
        self.assertEqual(loc, 'en')

    def test_accept_lang(self):
        self.req.accept_language = ('ru-RU',)
        loc = locale_neg(self.req)
        self.assertEqual(loc, 'ru')

    def test_wrong_accept_lang(self):
        self.req.accept_language = ('fr',)
        loc = locale_neg(self.req)
        self.assertEqual(loc, 'en')

    def test_session(self):
        self.req.session.get.return_value = 'ru'
        loc = locale_neg(self.req)
        self.assertEqual(loc, 'ru')

    def test_wrong_session(self):
        self.req.session.get.return_value = 'fr'
        loc = locale_neg(self.req)
        self.assertEqual(loc, 'en')

    def test_param(self):
        self.req.params.get.return_value = 'ru'
        loc = locale_neg(self.req)
        self.assertEqual(loc, 'ru')

    def test_wrong_param(self):
        self.req.params.get.return_value = 'fr'
        loc = locale_neg(self.req)
        self.assertEqual(loc, 'en')


class TestGetters(unittest.TestCase):
    def test_get_debug(self):
        req = mock.MagicMock()
        req.registry.settings.get.return_value = True
        self.assertTrue(get_debug(req))
        req.registry.settings.get.assert_called_once_with('netprofile.debug',
                                                          False)
        req.registry.settings.get.return_value = False
        self.assertFalse(get_debug(req))

    def test_get_locales(self):
        req = mock.MagicMock()
        req.registry.settings.get.return_value = ''
        self.assertEqual(get_locales(req), {})
        req.registry.settings.get.assert_called_once_with(
                'pyramid.available_languages', '')
        req.registry.settings.get.return_value = 'en ru'
        self.assertEqual(get_locales(req), {'en': Locale('en'),
                                            'ru': Locale('ru')})

    def test_get_current_locale(self):
        req = mock.MagicMock()
        req.locales = {'en': Locale('en'),
                       'ru': Locale('ru')}
        req.locale_name = 'ru'
        self.assertEqual(get_current_locale(req), Locale('ru'))
        req.locale_name = 'fr'
        self.assertIsNone(get_current_locale(req))

    def test_get_csrf(self):
        req = mock.MagicMock()
        req.session.get_csrf_token.return_value = 'TOKEN'
        self.assertEqual(get_csrf(req), 'TOKEN')
        req.session.get_csrf_token.return_value = b'TOKEN'
        self.assertEqual(get_csrf(req), 'TOKEN')

        req.session = None
        self.assertIsNone(get_csrf(req))


class TestVHostPredicate(unittest.TestCase):
    def setUp(self):
        self.cfg = mock.MagicMock()
        self.cfg.registry.settings.get.return_value = 'test1'
        self.predicate = VHostPredicate('test1', self.cfg)

    def test_init(self):
        self.cfg.registry.settings.get.assert_called_once_with(
                'netprofile.vhost')
        self.assertEqual(self.predicate.needed, 'test1')
        self.assertEqual(self.predicate.current, 'test1')

    def test_text(self):
        self.assertEqual(self.predicate.text(),
                         'vhost = test1')

    def test_call(self):
        ctx = mock.MagicMock()
        req = mock.MagicMock()
        self.assertTrue(self.predicate(ctx, req))

    def test_call_main(self):
        self.predicate.needed = 'MAIN'
        ctx = mock.MagicMock()
        req = mock.MagicMock()
        self.assertFalse(self.predicate(ctx, req))
        self.predicate.current = None
        self.assertTrue(self.predicate(ctx, req))


class TestSetupConfig(unittest.TestCase):
    @mock.patch('netprofile.Configurator')
    @mock.patch('netprofile.cache')
    @mock.patch('netprofile.DBSession')
    @mock.patch('netprofile.engine_from_config')
    def test_setup_config(self, engine_from_cfg, dbsess, cache, conf):
        settings = {'netprofile.debug': 'false'}
        cache.cache = None

        cfg = setup_config(settings)
        conf.assert_called_once_with(settings=settings,
                                     root_factory=RootFactory,
                                     locale_negotiator=locale_neg)
        self.assertEqual(cfg, conf())
        self.assertFalse(settings['netprofile.debug'])
        self.assertEqual(netprofile.inst_id, 'ru.netprofile')
        engine_from_cfg.assert_called_once_with(settings, 'sqlalchemy.')
        dbsess.configure.assert_called_once_with(bind=engine_from_cfg())
        cache.configure_cache.assert_called_once_with(settings)
        self.assertEqual(cache.cache, cache.configure_cache())
        cfg.add_route_predicate.assert_called_once_with('vhost',
                                                        VHostPredicate)
        cfg.add_view_predicate.assert_called_once_with('vhost',
                                                       VHostPredicate)

        settings = {'netprofile.debug': 'true',
                    'netprofile.instance_id': 'INST'}
        cfg = setup_config(settings)
        self.assertTrue(settings['netprofile.debug'])
        self.assertEqual(netprofile.inst_id, 'INST')


class TestMain(unittest.TestCase):
    @mock.patch('netprofile.setup_config')
    def test_main(self, setup_cfg):
        settings = {}
        gcfg = mock.MagicMock()
        config = mock.MagicMock()
        mm = mock.MagicMock()
        config.registry.getUtility.return_value = mm
        setup_cfg.return_value = config

        app = main(gcfg, **settings)

        setup_cfg.assert_called_once_with(settings)
        config.add_subscriber.assert_has_calls((
                mock.call('netprofile.common.subscribers.add_renderer_globals',
                          'pyramid.events.BeforeRender'),
                mock.call('netprofile.common.subscribers.on_new_request',
                          'pyramid.events.ContextFound'),
                mock.call('netprofile.common.subscribers.on_response',
                          'pyramid.events.NewResponse')),
                any_order=True)
        config.add_request_method.assert_has_calls((
                mock.call(get_locales, str('locales'), reify=True),
                mock.call(get_current_locale, str('current_locale'),
                          reify=True),
                mock.call(get_debug, str('debug_enabled'), reify=True),
                mock.call(get_csrf, str('get_csrf'))),
                any_order=True)

        mm.load.assert_called_once_with('core')
        mm.load_enabled.assert_called_once_with()

        config.make_wsgi_app.assert_called_once_with()
        self.assertEqual(app, config.make_wsgi_app())
