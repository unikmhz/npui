#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Tests for hooks API
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
from pyramid import testing

# Test body begins here

import os
from netprofile.common.hooks import (
    HookManager,
    IHookManager,
    register_block,
    register_hook,
    includeme,
    _run_block,
    _run_hook,
    gen_block
)
from netprofile.tpl import TemplateObject


def _noop1(*args, **kwargs):
    pass


def _noop2(*args, **kwargs):
    pass


def _str_a(*args, **kwargs):
    return 'A'


def _str_b(*args, **kwargs):
    return 'B'


class TestHooksAPI(unittest.TestCase):
    def setUp(self):
        self.hm = HookManager()

    def test_init(self):
        self.assertEqual(self.hm.hooks, {})
        self.assertEqual(self.hm.blocks, {})

    def test_reg_block(self):
        self.hm.reg_block('b1', _noop1)
        self.hm.reg_block('b1', _noop1)
        self.hm.reg_block('b2', _noop1)
        self.hm.reg_block('b2', _noop2)

        self.assertEqual(self.hm.blocks, {'b1': [_noop1],
                                          'b2': [_noop1, _noop2]})

    def test_reg_hook(self):
        self.hm.reg_hook('h1', _noop1)
        self.hm.reg_hook('h1', _noop1)
        self.hm.reg_hook('h2', _noop1)
        self.hm.reg_hook('h2', _noop2)

        with self.assertRaises(ValueError):
            self.hm.reg_hook('h1', 'wrong')

        self.assertEqual(self.hm.hooks, {'h1': [_noop1],
                                         'h2': [_noop1, _noop2]})

    def test_run_block(self):
        self.assertEqual(self.hm.run_block('missing'), '')

        self.hm.reg_block('b1', _str_a)
        self.hm.reg_block('b1', _str_a)
        self.hm.reg_block('b1', _str_b)
        self.hm.reg_block('b1', 'C')
        self.hm.reg_block('b1', 'C')

        self.assertEqual(self.hm.run_block('b1'), 'ABC')

    @mock.patch('netprofile.tpl.TemplateObject.render')
    def test_run_block_tpl(self, render):
        render.return_value = 'X'

        here = os.path.abspath(os.path.dirname(__file__))
        req = mock.MagicMock()
        to = TemplateObject(os.path.join(here, 'test_tpl.mak'))

        self.hm.reg_block('b1', _str_b)
        self.hm.reg_block('b1', to)
        self.hm.reg_block('b1', _str_b)
        self.hm.reg_block('b1', to)
        self.assertEqual(self.hm.run_block('b1', 1, 2, 3, request=req, req=req,
                                           item1=1, item2=2, item3=3),
                         'BX')

        render.assert_called_once_with(req, argv=(1, 2, 3),
                                       item1=1, item2=2, item3=3)

    def test_run_hook(self):
        self.assertFalse(self.hm.run_hook('missing'))

        cb1 = mock.MagicMock(return_value=1)
        cb2 = mock.MagicMock(return_value=2)

        self.hm.reg_hook('h1', cb1)
        self.hm.reg_hook('h1', cb2)
        self.hm.reg_hook('h1', cb2)
        self.hm.reg_hook('h1', cb1)

        self.assertEqual(self.hm.run_hook('h1'), [1, 2])

        cb1.assert_called_once_with()
        cb2.assert_called_once_with()

    @mock.patch('venusian.attach')
    def test_dec_reg_block(self, ven_attach):
        dec = register_block('b1')
        self.assertEqual(dec.name, 'b1')

        wrapped = dec(_str_a)
        self.assertIs(_str_a, wrapped)
        ven_attach.assert_called_once_with(_str_a, dec.register)

        mock_scanner = mock.MagicMock()
        mock_scanner.config.registry.getUtility.return_value = self.hm
        dec.register(mock_scanner, 'b1', _str_a)

        self.assertEqual(self.hm.blocks, {'b1': [_str_a]})

    @mock.patch('venusian.attach')
    def test_dec_reg_hook(self, ven_attach):
        dec = register_hook('h1')
        self.assertEqual(dec.name, 'h1')

        wrapped = dec(_noop1)
        self.assertIs(_noop1, wrapped)
        ven_attach.assert_called_once_with(_noop1, dec.register)

        mock_scanner = mock.MagicMock()
        mock_scanner.config.registry.getUtility.return_value = self.hm
        dec.register(mock_scanner, 'h1', _noop1)

        self.assertEqual(self.hm.hooks, {'h1': [_noop1]})


class TestPyramidHooksAPI(unittest.TestCase):
    def setUp(self):
        self.req = testing.DummyRequest()
        self.config = testing.setUp(request=self.req)
        includeme(self.config)

    def tearDown(self):
        testing.tearDown()

    def test_hooks(self):
        cb1 = mock.MagicMock(return_value=1)
        cb2 = mock.MagicMock(return_value=2)

        self.config.register_hook('h1', cb1)
        self.config.register_hook('h1', cb2)

        hm = self.config.registry.getUtility(IHookManager)
        self.assertEqual(hm.hooks, {'h1': [cb1, cb2]})

        self.assertEqual(_run_hook(self.req, 'h1'), [1, 2])
        cb1.assert_called_once_with()
        cb2.assert_called_once_with()

    def test_blocks(self):
        cb1 = mock.MagicMock(return_value='A')
        cb2 = mock.MagicMock(return_value='B')

        self.config.register_block('b1', cb1)
        self.config.register_block('b1', cb2)

        hm = self.config.registry.getUtility(IHookManager)
        self.assertEqual(hm.blocks, {'b1': [cb1, cb2]})

        self.assertEqual(_run_block(self.req, 'b1'), 'AB')
        cb1.assert_called_once_with()
        cb2.assert_called_once_with()

    def test_gen_block(self):
        ctx = mock.MagicMock()
        ctx.get.return_value = self.req
        ctx.kwargs = {'a': 'test'}

        cb1 = mock.MagicMock(return_value='A')
        cb2 = mock.MagicMock(return_value='B')

        self.config.register_block('b1', cb1)
        self.config.register_block('b1', cb2)

        self.assertEqual(gen_block(ctx, 'b1', 1, 2, 3, b='test'), 'AB')

        cb1.assert_called_once_with(1, 2, 3, a='test', b='test')
        cb2.assert_called_once_with(1, 2, 3, a='test', b='test')
