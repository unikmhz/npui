#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Tests for authentication API
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

import time
from collections import OrderedDict
from pyramid.security import (
    Authenticated,
    Everyone
)
from pyramid.httpexceptions import HTTPFound

from netprofile.common.auth import (
    auth_add,
    auth_remove,
    DigestAuthenticationPolicy,
    PluginAuthenticationPolicy,
    _add_www_authenticate,
    _filter_token,
    _format_kvpairs,
    _generate_digest_challenge,
    _generate_nonce,
    _is_valid_nonce,
    _is_valid_nonce_timestamp,
    _parse_authorization
)


class TestHTTPDigestHeader(unittest.TestCase):
    def setUp(self):
        self.ts = str(round(time.time()))
        self.req = testing.DummyRequest()
        self.req.authorization = None

    def test_generate_nonce(self):
        nonce = _generate_nonce(self.ts, 'secret')
        self.assertEqual(len(nonce), len(self.ts) + 50)
        self.assertRegex(nonce, r'^\d{10,11}:[0-9A-F]{16}:[0-9a-fA-F]{32}$')

        parts = nonce.split(':')
        self.assertEqual(parts[0], self.ts)

        nonce2 = _generate_nonce(self.ts, 'secret', parts[1])
        self.assertEqual(nonce, nonce2)

    def test_filter_token(self):
        filter_map = {'normal': 'normal',
                      '\u007fchars\u0010\u0011': 'chars',
                      '"spe"cial\\': 'special'}
        for tok_in, tok_out in filter_map.items():
            self.assertEqual(_filter_token(tok_in), tok_out)

    def test_format_kvpairs(self):
        kv = {'val1': 'plain',
              'val2': '\\"\'special\'"\\'}

        formatted = _format_kvpairs(**kv).split(', ')
        formatted.sort()
        self.assertEqual(formatted, ['val1="plain"',
                                     'val2="\'special\'"'])

    def test_is_valid_nonce(self):
        self.assertTrue(_is_valid_nonce(
            '1234567890:0123456789ABCDEF:355087d404b3c5e7b6782df5ca930d1e',
            'secret'))
        self.assertTrue(_is_valid_nonce(
            '1234567890:FEDCBA9876543210:e376eccc2dd057250eadb8345772b385',
            'secret'))

        self.assertFalse(_is_valid_nonce(
            '1234567890:FEDCBA9876543210:e376eccc2dd057250eadb8345772b385',
            'SECRET'))
        self.assertFalse(_is_valid_nonce(
            'FEDCBA9876543210:e376eccc2dd057250eadb8345772b385',
            'secret'))
        self.assertFalse(_is_valid_nonce(
            '1234567890:e376eccc2dd057250eadb8345772b385',
            'secret'))
        self.assertFalse(_is_valid_nonce(
            '1234567890::e376eccc2dd057250eadb8345772b385',
            'secret'))
        self.assertFalse(_is_valid_nonce(
            '1234567890:0123456789ABCDEF:e376eccc2dd057250eadb8345772b385',
            'secret'))

    @mock.patch('time.time')
    def test_is_valid_nonce_timestamp(self, mock_time):
        mock_time.return_value = 1234567890.0

        nonce = ('NOT-A-TIMESTAMP:'
                 '0123456789ABCDEF:'
                 '355087d404b3c5e7b6782df5ca930d1e')
        self.assertFalse(_is_valid_nonce_timestamp(nonce, 5, 120))

        nonce = '1234567890:0123456789ABCDEF:355087d404b3c5e7b6782df5ca930d1e'
        self.assertTrue(_is_valid_nonce_timestamp(nonce, 5, 120))

        mock_time.return_value = 1234567885.0
        self.assertTrue(_is_valid_nonce_timestamp(nonce, 5, 120))
        mock_time.return_value = 1234568010.0
        self.assertTrue(_is_valid_nonce_timestamp(nonce, 5, 120))

        mock_time.return_value = 1234567884.0
        self.assertFalse(_is_valid_nonce_timestamp(nonce, 5, 120))
        mock_time.return_value = 1234568011.0
        self.assertFalse(_is_valid_nonce_timestamp(nonce, 5, 120))

    @mock.patch('netprofile.common.auth._generate_nonce')
    @mock.patch('netprofile.common.auth._format_kvpairs')
    def test_generate_digest_challenge(self, format_kvp, gen_nonce):
        format_kvp.return_value = 'DUMMY'
        gen_nonce.return_value = 'NONCE'

        ch = _generate_digest_challenge(self.ts, 'secret', 'realm', 'opaque')

        self.assertEqual(ch, 'Digest DUMMY')
        gen_nonce.assert_called_once_with(self.ts, 'secret')
        format_kvp.assert_called_once_with(
                realm='realm', qop='auth', nonce='NONCE', opaque='opaque',
                algorithm='MD5', stale='false')

    def test_add_www_authenticate(self):
        _add_www_authenticate(self.req, 'secret', 'realm')
        wwwa = self.req.response.www_authenticate

        self.assertIsNotNone(wwwa)
        self.assertEqual(len(wwwa), 2)
        self.assertEqual(wwwa[0], 'Digest')
        self.assertIn('nonce', wwwa[1])
        nonce = wwwa[1]['nonce']
        self.assertEqual(wwwa[1], {'algorithm': 'MD5',
                                   'qop': 'auth',
                                   'realm': 'realm',
                                   'nonce': nonce,
                                   'opaque': 'NPDIGEST',
                                   'stale': 'false'})

        self.req.response.www_authenticate = 'Test Value'
        _add_www_authenticate(self.req, 'secret', 'realm')
        wwwa = self.req.response.www_authenticate

        self.assertEqual(wwwa, ('Test', 'Value'))

    def test_parse_no_header(self):
        ret = _parse_authorization(self.req, 'secret', 'realm')
        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertIsNone(ret)

        self.req.response.www_authenticate = None
        self.req.authorization = ('Wrong',)
        ret = _parse_authorization(self.req, 'secret', 'realm')
        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertIsNone(ret)

        self.req.response.www_authenticate = None
        self.req.authorization = ('Basic', {})
        ret = _parse_authorization(self.req, 'secret', 'realm')
        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertIsNone(ret)

    def test_parse_missing_response(self):
        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': '60b4780f24585c574183655c47f17399',
                                   'uri': '/index.html',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'NPDIGEST'})

        ret = _parse_authorization(self.req, 'secret', 'realm')
        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertIsNone(ret)

    def test_parse_wrong_opaque(self):
        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': '60b4780f24585c574183655c47f17399',
                                   'uri': '/index.html',
                                   'response':
                                       'fe6636cdb8b1733ecca83dcb14b13323',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'WRONG',
                                   'algorithm': 'MD5'})

        ret = _parse_authorization(self.req, 'secret', 'realm')
        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertIsNone(ret)

    def test_parse_ok(self):
        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': '60b4780f24585c574183655c47f17399',
                                   'uri': '/index.html',
                                   'response':
                                       'fe6636cdb8b1733ecca83dcb14b13323',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'NPDIGEST'})

        ret = _parse_authorization(self.req, 'secret', 'realm')
        self.assertIsNone(self.req.response.www_authenticate)
        self.assertEqual(ret, {'username': 'testuser',
                               'realm': 'realm',
                               'nonce': '60b4780f24585c574183655c47f17399',
                               'uri': '/index.html',
                               'response': 'fe6636cdb8b1733ecca83dcb14b13323',
                               'cnonce': '1f3f713c',
                               'nc': '00000001',
                               'opaque': 'NPDIGEST',
                               'algorithm': 'MD5'})


class TestDigestAuthenticationPolicy(unittest.TestCase):
    def setUp(self):
        self.ts = str(round(time.time()))
        self.callback = mock.MagicMock()
        self.req = testing.DummyRequest()
        self.req.authorization = None
        self.cfg = testing.setUp(request=self.req)

        self.pol = DigestAuthenticationPolicy('secret', self.callback,
                                              realm='realm')

    def tearDown(self):
        testing.tearDown()

    def test_init(self):
        self.assertEqual(self.pol.secret, 'secret')
        self.assertEqual(self.pol.callback, self.callback)
        self.assertEqual(self.pol.realm, 'realm')

    def test_remember(self):
        self.assertEqual(self.pol.remember(self.req, 'princ'), [])

    @mock.patch('netprofile.common.auth._generate_digest_challenge')
    def test_forget(self, gen_digest):
        gen_digest.return_value = 'CHALLENGE'

        ret = self.pol.forget(self.req)

        self.assertEqual(ret, [('WWW-Authenticate', 'CHALLENGE')])

    def test_unauth_no_header(self):
        ret = self.pol.unauthenticated_userid(self.req)

        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertIsNone(ret)

    def test_unauth_invalid_nonce(self):
        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': 'INVALID',
                                   'uri': '/index.html',
                                   'response':
                                       'fe6636cdb8b1733ecca83dcb14b13323',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'NPDIGEST',
                                   'algorithm': 'MD5'})

        ret = self.pol.unauthenticated_userid(self.req)

        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertIsNone(ret)

    @mock.patch('time.time')
    def test_unauth_invalid_nonce_timestamp(self, mock_time):
        mock_time.return_value = 1234567890.0

        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': ('1234567290:0123456789ABCDEF:'
                                             '50396f1fd279bfc5'
                                             'b81af6146e3ad02d'),
                                   'uri': '/index.html',
                                   'response':
                                       'fe6636cdb8b1733ecca83dcb14b13323',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'NPDIGEST',
                                   'algorithm': 'MD5'})

        ret = self.pol.unauthenticated_userid(self.req)

        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertIsNone(ret)

        wwwa = self.req.response.www_authenticate
        self.assertEqual(wwwa, ('Digest',
                                {'algorithm': 'MD5',
                                 'qop': 'auth',
                                 'realm': 'realm',
                                 'nonce': wwwa[1]['nonce'],
                                 'opaque': 'NPDIGEST',
                                 'stale': 'true'}))

    def test_unauth_ok(self):
        nonce = _generate_nonce(self.ts, 'secret')
        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': nonce,
                                   'uri': '/index.html',
                                   'response':
                                       'fe6636cdb8b1733ecca83dcb14b13323',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'NPDIGEST',
                                   'algorithm': 'MD5'})

        ret = self.pol.unauthenticated_userid(self.req)

        self.assertIsNone(self.req.response.www_authenticate)
        self.assertEqual(ret, 'u:testuser')

    def test_auth_no_header(self):
        ret = self.pol.authenticated_userid(self.req)

        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertIsNone(ret)

    def test_auth_invalid_nonce(self):
        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': 'INVALID',
                                   'uri': '/index.html',
                                   'response':
                                       'fe6636cdb8b1733ecca83dcb14b13323',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'NPDIGEST',
                                   'algorithm': 'MD5'})

        ret = self.pol.authenticated_userid(self.req)

        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertIsNone(ret)

    @mock.patch('time.time')
    def test_auth_invalid_nonce_timestamp(self, mock_time):
        mock_time.return_value = 1234567890.0

        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': ('1234568490:'
                                             '0123456789ABCDEF:'
                                             '0da457bab1f2c04d'
                                             'e5bce45b3435c818'),
                                   'uri': '/index.html',
                                   'response':
                                       'fe6636cdb8b1733ecca83dcb14b13323',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'NPDIGEST',
                                   'algorithm': 'MD5'})

        ret = self.pol.authenticated_userid(self.req)

        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertIsNone(ret)

        wwwa = self.req.response.www_authenticate
        self.assertEqual(wwwa, ('Digest',
                                {'algorithm': 'MD5',
                                 'qop': 'auth',
                                 'realm': 'realm',
                                 'nonce': wwwa[1]['nonce'],
                                 'opaque': 'NPDIGEST',
                                 'stale': 'true'}))

    def test_auth_callback_failed(self):
        self.callback.return_value = None
        nonce = _generate_nonce(self.ts, 'secret')
        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': nonce,
                                   'uri': '/index.html',
                                   'response':
                                       'fe6636cdb8b1733ecca83dcb14b13323',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'NPDIGEST',
                                   'algorithm': 'MD5'})

        ret = self.pol.authenticated_userid(self.req)

        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertIsNone(ret)
        self.callback.assert_called_once_with(self.req.authorization[1],
                                              self.req)

    def test_auth_callback_ok(self):
        self.callback.return_value = ['g:testgroup1', 'g:testgroup2']
        nonce = _generate_nonce(self.ts, 'secret')
        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': nonce,
                                   'uri': '/index.html',
                                   'response':
                                       'fe6636cdb8b1733ecca83dcb14b13323',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'NPDIGEST',
                                   'algorithm': 'MD5'})

        ret = self.pol.authenticated_userid(self.req)

        self.assertIsNone(self.req.response.www_authenticate)
        self.assertEqual(ret, 'u:testuser')
        self.callback.assert_called_once_with(self.req.authorization[1],
                                              self.req)

    def test_ep_no_header(self):
        ret = self.pol.effective_principals(self.req)

        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertEqual(ret, [Everyone])

    def test_ep_invalid_nonce(self):
        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': 'INVALID',
                                   'uri': '/index.html',
                                   'response':
                                       'fe6636cdb8b1733ecca83dcb14b13323',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'NPDIGEST',
                                   'algorithm': 'MD5'})

        ret = self.pol.effective_principals(self.req)

        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertEqual(ret, [Everyone])

    @mock.patch('time.time')
    def test_ep_invalid_nonce_timestamp(self, mock_time):
        mock_time.return_value = 1234567890.0

        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': ('1234567290:'
                                             '0123456789ABCDEF:'
                                             '50396f1fd279bfc5'
                                             'b81af6146e3ad02d'),
                                   'uri': '/index.html',
                                   'response':
                                       'fe6636cdb8b1733ecca83dcb14b13323',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'NPDIGEST',
                                   'algorithm': 'MD5'})

        ret = self.pol.effective_principals(self.req)

        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertEqual(ret, [Everyone])

        wwwa = self.req.response.www_authenticate
        self.assertEqual(wwwa, ('Digest',
                                {'algorithm': 'MD5',
                                 'qop': 'auth',
                                 'realm': 'realm',
                                 'nonce': wwwa[1]['nonce'],
                                 'opaque': 'NPDIGEST',
                                 'stale': 'true'}))

    def test_ep_callback_failed(self):
        self.callback.return_value = None
        nonce = _generate_nonce(self.ts, 'secret')
        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': nonce,
                                   'uri': '/index.html',
                                   'response':
                                       'fe6636cdb8b1733ecca83dcb14b13323',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'NPDIGEST',
                                   'algorithm': 'MD5'})

        ret = self.pol.effective_principals(self.req)

        self.assertIsNotNone(self.req.response.www_authenticate)
        self.assertEqual(ret, [Everyone])
        self.callback.assert_called_once_with(self.req.authorization[1],
                                              self.req)

    def test_ep_callback_ok(self):
        self.callback.return_value = ['g:testgroup1', 'g:testgroup2']
        nonce = _generate_nonce(self.ts, 'secret')
        self.req.authorization = ('Digest',
                                  {'username': 'testuser',
                                   'realm': 'realm',
                                   'nonce': nonce,
                                   'uri': '/index.html',
                                   'response':
                                       'fe6636cdb8b1733ecca83dcb14b13323',
                                   'cnonce': '1f3f713c',
                                   'nc': '00000001',
                                   'opaque': 'NPDIGEST',
                                   'algorithm': 'MD5'})

        ret = self.pol.effective_principals(self.req)

        self.assertIsNone(self.req.response.www_authenticate)
        self.assertEqual(ret, [Everyone, Authenticated,
                               'u:testuser', 'g:testgroup1', 'g:testgroup2'])
        self.callback.assert_called_once_with(self.req.authorization[1],
                                              self.req)


class TestPluginAuthenticationPolicy(unittest.TestCase):
    def setUp(self):
        self.req = testing.DummyRequest()
        self.cfg = testing.setUp(request=self.req)

        self.pol_default = mock.MagicMock()
        self.pol_t1 = mock.MagicMock()
        self.pol_t2 = mock.MagicMock()
        self.pol_x = mock.MagicMock()

        self.routes = OrderedDict((('/t1',    self.pol_t1),
                                   ('/t1/t2', self.pol_t2),
                                   ('/x',     self.pol_x)))
        self.pol = PluginAuthenticationPolicy(self.pol_default, self.routes)

    def tearDown(self):
        testing.tearDown()

    def test_init(self):
        # TODO: routes
        self.assertEqual(self.pol._default, self.pol_default)

    def test_init_no_routes(self):
        pol = PluginAuthenticationPolicy(self.pol_default)
        self.assertEqual(pol._routes, {})

    def test_add_plugin(self):
        new_plugin = mock.MagicMock()
        self.pol.add_plugin('/t9', new_plugin)

        self.assertIn('/t9', self.pol._routes)
        self.assertEqual(self.pol._routes['/t9'], new_plugin)

    def test_match_cached(self):
        self.req.auth_policy = self.pol_t1

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_t1)

    def test_match_default(self):
        self.req.path = '/no/matches'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_default)
        self.assertEqual(self.req.auth_policy, self.pol_default)

    def test_match_default_long(self):
        self.req.path = '/cheeky/t1'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_default)
        self.assertEqual(self.req.auth_policy, self.pol_default)

    def test_match_default_short(self):
        self.req.path = '/t'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_default)
        self.assertEqual(self.req.auth_policy, self.pol_default)

    def test_match_default_partial(self):
        self.req.path = '/t12'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_default)
        self.assertEqual(self.req.auth_policy, self.pol_default)

    def test_match_default_partial_long(self):
        self.req.path = '/t12/t1'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_default)
        self.assertEqual(self.req.auth_policy, self.pol_default)

    def test_match_t1(self):
        self.req.path = '/t1'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_t1)
        self.assertEqual(self.req.auth_policy, self.pol_t1)

    def test_match_t1_long(self):
        self.req.path = '/t1/suffix'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_t1)
        self.assertEqual(self.req.auth_policy, self.pol_t1)

    def test_match_t1_partial(self):
        self.req.path = '/t1/t'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_t1)
        self.assertEqual(self.req.auth_policy, self.pol_t1)

    def test_match_t1_partial2(self):
        self.req.path = '/t1/t22'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_t1)
        self.assertEqual(self.req.auth_policy, self.pol_t1)

    def test_match_t1_partial3(self):
        self.req.path = '/t1/t22/suffix'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_t1)
        self.assertEqual(self.req.auth_policy, self.pol_t1)

    def test_match_t2(self):
        self.req.path = '/t1/t2'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_t2)
        self.assertEqual(self.req.auth_policy, self.pol_t2)

    def test_match_t2_long(self):
        self.req.path = '/t1/t2/suffix'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_t2)
        self.assertEqual(self.req.auth_policy, self.pol_t2)

    def test_match_t2_long2(self):
        self.req.path = '/t1/t2/t1'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_t2)
        self.assertEqual(self.req.auth_policy, self.pol_t2)

    def test_match_x(self):
        self.req.path = '/x/y/z'

        matched = self.pol.match(self.req)
        self.assertEqual(matched, self.pol_x)
        self.assertEqual(self.req.auth_policy, self.pol_x)

    def test_default_auth_userid(self):
        self.pol.authenticated_userid(self.req)
        self.pol_default.authenticated_userid.assert_called_once_with(self.req)

    def test_default_unauth_userid(self):
        self.pol.unauthenticated_userid(self.req)
        self.pol_default.unauthenticated_userid.assert_called_once_with(
                self.req)

    def test_default_ep(self):
        self.pol.effective_principals(self.req)
        self.pol_default.effective_principals.assert_called_once_with(self.req)

    def test_default_remember(self):
        self.pol.remember(self.req, 'princ', a=1, b=2)
        self.pol_default.remember.assert_called_once_with(self.req, 'princ',
                                                          a=1, b=2)

    def test_default_forget(self):
        self.pol.forget(self.req)
        self.pol_default.forget.assert_called_once_with(self.req)

    def test_t1_auth_userid(self):
        self.req.path = '/t1/suffix'

        self.pol.authenticated_userid(self.req)
        self.pol_t1.authenticated_userid.assert_called_once_with(self.req)
        self.pol_default.authenticated_userid.assert_not_called()

    def test_t1_unauth_userid(self):
        self.req.path = '/t1/suffix'

        self.pol.unauthenticated_userid(self.req)
        self.pol_t1.unauthenticated_userid.assert_called_once_with(self.req)
        self.pol_default.unauthenticated_userid.assert_not_called()

    def test_t1_ep(self):
        self.req.path = '/t1/suffix'

        self.pol.effective_principals(self.req)
        self.pol_t1.effective_principals.assert_called_once_with(self.req)
        self.pol_default.effective_principals.assert_not_called()

    def test_t1_remember(self):
        self.req.path = '/t1/suffix'

        self.pol.remember(self.req, 'princ', a=1, b=2)
        self.pol_t1.remember.assert_called_once_with(self.req, 'princ',
                                                     a=1, b=2)
        self.pol_default.remember.assert_not_called()

    def test_t1_forget(self):
        self.req.path = '/t1/suffix'

        self.pol.forget(self.req)
        self.pol_t1.forget.assert_called_once_with(self.req)
        self.pol_default.forget.assert_not_called()


class _mock_sess(dict):
    def __init__(self, *args, **kwargs):
        super(_mock_sess, self).__init__(*args, **kwargs)
        self.invalidate = mock.MagicMock()
        self.new_csrf_token = mock.MagicMock()


class TestAuthHelpers(unittest.TestCase):
    def setUp(self):
        self.req = testing.DummyRequest()
        self.req.session = self.sess = _mock_sess()
        self.req.route_url = mock.MagicMock()
        self.req.route_url.return_value = '/testurl'
        self.cfg = testing.setUp(request=self.req)

    def tearDown(self):
        testing.tearDown()

    @mock.patch('netprofile.common.auth.remember')
    def test_auth_add_no_sess(self, mock_remember):
        ret = auth_add(self.req, 'testuser', 'test.route')

        mock_remember.assert_called_once_with(self.req, 'testuser')
        self.req.route_url.assert_called_once_with('test.route')
        self.assertIsInstance(ret, HTTPFound)
        self.assertEqual(ret.location, '/testurl')

    @mock.patch('netprofile.common.auth.remember')
    def test_auth_add_sess1(self, mock_remember):
        self.sess['auth.acls'] = 'DUMMY'

        ret = auth_add(self.req, 'testuser', 'test.route')

        mock_remember.assert_called_once_with(self.req, 'testuser')
        self.req.route_url.assert_called_once_with('test.route')
        self.assertIsInstance(ret, HTTPFound)
        self.assertEqual(ret.location, '/testurl')
        self.assertEqual(self.sess, {})

    @mock.patch('netprofile.common.auth.remember')
    def test_auth_add_sess2(self, mock_remember):
        self.sess['auth.settings'] = 'DUMMY'

        ret = auth_add(self.req, 'testuser', 'test.route')

        mock_remember.assert_called_once_with(self.req, 'testuser')
        self.req.route_url.assert_called_once_with('test.route')
        self.assertIsInstance(ret, HTTPFound)
        self.assertEqual(ret.location, '/testurl')
        self.assertEqual(self.sess, {})

    @mock.patch('netprofile.common.auth.forget')
    def test_auth_remove_no_sess(self, mock_forget):
        ret = auth_remove(self.req, 'test.route')

        mock_forget.assert_called_once_with(self.req)
        self.req.route_url.assert_called_once_with('test.route')
        self.assertIsInstance(ret, HTTPFound)
        self.assertEqual(ret.location, '/testurl')

    @mock.patch('netprofile.common.auth.forget')
    def test_auth_remove_sess1(self, mock_forget):
        self.sess['auth.acls'] = 'DUMMY'

        ret = auth_remove(self.req, 'test.route')

        mock_forget.assert_called_once_with(self.req)
        self.req.route_url.assert_called_once_with('test.route')
        self.assertIsInstance(ret, HTTPFound)
        self.assertEqual(ret.location, '/testurl')
        self.assertEqual(self.sess, {})
        self.sess.invalidate.assert_called_once_with()
        self.sess.new_csrf_token.assert_called_once_with()

    @mock.patch('netprofile.common.auth.forget')
    def test_auth_remove_sess2(self, mock_forget):
        self.sess['auth.settings'] = 'DUMMY'

        ret = auth_remove(self.req, 'test.route')

        mock_forget.assert_called_once_with(self.req)
        self.req.route_url.assert_called_once_with('test.route')
        self.assertIsInstance(ret, HTTPFound)
        self.assertEqual(ret.location, '/testurl')
        self.assertEqual(self.sess, {})
        self.sess.invalidate.assert_called_once_with()
        self.sess.new_csrf_token.assert_called_once_with()
