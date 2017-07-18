#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Cryptography helper routines
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

import base64
import crypt
import hashlib
import hmac
import random
import scrypt
import string

from six import PY3
from pyramid.settings import aslist

from netprofile.common.util import make_config_dict

__all__ = (
    'get_random',
    'get_salt_bytes',
    'get_salt_string',
    'hash_password',
    'verify_password',
    'PasswordHandler',
    'ScryptPasswordHandler',
    'DigestHA1PasswordHandler',
    'NTLMPasswordHandler',
    'CryptPasswordHandler',
    'PlainTextPasswordHandler'
)


def get_random(system_rng=True):
    if system_rng:
        try:
            return random.SystemRandom()
        except NotImplementedError:  # pragma: no cover
            pass
    return random.Random()


if PY3:
    def get_salt_bytes(length,
                       chars=bytes(string.ascii_letters + string.digits,
                                   'ascii')):
        rnd = get_random()
        if chars is None:
            return bytes(rnd.randint(0, 255) for _ in range(length))
        if not isinstance(chars, bytes):
            chars = chars.encode('ascii')
        return bytes(rnd.choice(chars) for _ in range(length))
else:  # pragma: no cover
    def get_salt_bytes(length,
                       chars=bytes(string.ascii_letters + string.digits)):
        rnd = get_random()
        if chars is None:
            return b''.join(chr(rnd.randint(0, 255)) for _ in range(length))
        if not isinstance(chars, bytes):
            chars = chars.encode('ascii')
        return b''.join(rnd.choice(chars) for _ in range(length))


def get_salt_string(length, chars=string.ascii_letters + string.digits):
    rnd = get_random()
    return ''.join(rnd.choice(chars) for _ in range(length))


class PasswordHandler(object):
    elements = 1

    def _pack(self, *args):
        if len(args) != self.elements:
            raise ValueError('Invalid hash format')
        return '$'.join(args)

    def _unpack(self, packed):
        if isinstance(packed, bytes):
            packed = packed.decode()
        unpacked = packed.split('$')
        if len(unpacked) != self.elements:
            raise ValueError('Invalid hash format')
        return unpacked

    def __init__(self, cfg):
        pass

    def hash(self, user, password):
        raise NotImplementedError

    def verify(self, user, password, hashed):
        new_hashed = self.hash(user, password)
        return hmac.compare_digest(hashed, new_hashed)


class ScryptPasswordHandler(PasswordHandler):
    elements = 6

    def __init__(self, cfg):
        PasswordHandler.__init__(self, cfg)
        self.salt_len = int(cfg.get('netprofile.crypto.scrypt.salt_length',
                                    20))
        self.n_exp = int(cfg.get('netprofile.crypto.scrypt.n_exponent', 14))
        self.r = int(cfg.get('netprofile.crypto.scrypt.r_value', 8))
        self.p = int(cfg.get('netprofile.crypto.scrypt.p_value', 1))
        self.buflen = int(cfg.get('netprofile.crypto.scrypt.buffer_length',
                                  64))

    def hash(self, user, password):
        if not isinstance(password, bytes):
            password = password.encode()

        salt = get_salt_bytes(self.salt_len)
        hashed = scrypt.hash(
            password, salt,
            1 << self.n_exp, self.r, self.p, self.buflen
        )

        return self._pack(
            salt.decode(),
            str(self.n_exp), str(self.r), str(self.p), str(self.buflen),
            base64.b64encode(hashed).decode()
        )

    def verify(self, user, password, hashed):
        if not isinstance(password, bytes):
            password = password.encode()

        salt, n_exp, r, p, buflen, hashed = self._unpack(hashed)

        salt = salt.encode()
        hashed = base64.b64decode(hashed)

        new_hashed = scrypt.hash(
            password, salt,
            1 << int(n_exp), int(r), int(p), int(buflen)
        )

        return hmac.compare_digest(hashed, new_hashed)


class DigestHA1PasswordHandler(PasswordHandler):
    def __init__(self, cfg):
        PasswordHandler.__init__(self, cfg)
        self.realm = cfg.get('netprofile.auth.digest.realm', 'NetProfile UI')

    def hash(self, user, password):
        ctx = hashlib.md5()
        ctx.update(('%s:%s:%s' % (user, self.realm, password)).encode())
        digest = ctx.hexdigest()
        if isinstance(digest, bytes):
            digest = digest.decode()
        return digest


class NTLMPasswordHandler(PasswordHandler):
    def hash(self, user, password):
        ctx = hashlib.new('md4')
        ctx.update(password.encode('utf-16le'))
        digest = ctx.hexdigest()
        if isinstance(digest, bytes):
            digest = digest.decode()
        return digest


class CryptPasswordHandler(PasswordHandler):
    elements = 3

    def __init__(self, cfg):
        # TODO: use passlib module if native crypt doesn't know about
        #       selected method.
        PasswordHandler.__init__(self, cfg)
        self.method = cfg.get('netprofile.crypto.crypt.method', 'sha512')
        if self.method not in ('sha256', 'sha512'):
            self.method = 'sha512'

    def _mksalt(self):
        if hasattr(crypt, 'mksalt'):
            mname = 'METHOD_' + self.method.upper()
            method = getattr(crypt, mname, None)
            if method is None:
                raise ValueError('Unsupported crypt(3) method: %s' %
                                 (self.method,))
            return crypt.mksalt(method)

        salt_chars = string.ascii_letters + string.digits + './'

        if self.method == 'sha256':
            return '$5$%s' % (get_salt_string(16, salt_chars),)
        if self.method == 'sha512':
            return '$6$%s' % (get_salt_string(16, salt_chars),)

        raise ValueError('Unsupported crypt(3) method: %s' % (self.method,))

    def hash(self, user, password):
        if isinstance(password, bytes):
            password = password.decode()
        hashed = crypt.crypt(password, self._mksalt())
        if isinstance(hashed, bytes):
            hashed = hashed.decode()
        return hashed


class PlainTextPasswordHandler(PasswordHandler):
    def hash(self, user, password):
        if isinstance(password, bytes):
            return password.decode()
        if '$' in password:
            raise ValueError('Invalid password')
        return password

    def verify(self, user, password, hashed):
        if isinstance(password, bytes):
            password = password.decode()
        if '$' in password:
            raise ValueError('Invalid password')
        if isinstance(hashed, bytes):
            hashed = hashed.decode()
        return hmac.compare_digest(password, hashed)


_HANDLERS = {
    'scrypt': ScryptPasswordHandler,
    'digest-ha1': DigestHA1PasswordHandler,
    'ntlm': NTLMPasswordHandler,
    'crypt': CryptPasswordHandler,
    'plain': PlainTextPasswordHandler
}
_ENABLED_HANDLERS = {}
_DEFAULT_HANDLERS = {}


def hash_password(user, password, scheme=None, subject='users',
                  prepend_scheme=False):
    if scheme is None:
        prepend_scheme = True
        scheme = _DEFAULT_HANDLERS.get(subject, 'scrypt')
    if scheme not in _ENABLED_HANDLERS.get(subject, ('scrypt',)):
        return None
    if scheme not in _HANDLERS:
        raise ValueError('Unknown hash scheme: %r' % (scheme,))
    return ((scheme + '$') if prepend_scheme
            else '') + _HANDLERS[scheme].hash(user, password)


def verify_password(user, password, hashed, scheme=None, subject='users'):
    spl = hashed.split('$', 1)
    if scheme is None:
        if len(spl) == 2:
            scheme, hashed = spl
        else:
            scheme = _DEFAULT_HANDLERS.get(subject, 'scrypt')
    elif len(spl) == 2 and scheme == spl[0]:
        hashed = spl[1]
    if scheme not in _ENABLED_HANDLERS.get(subject, ('scrypt',)):
        return False
    if scheme not in _HANDLERS:
        raise ValueError('Unknown hash scheme: %r' % (scheme,))
    return _HANDLERS[scheme].verify(user, password, hashed)


def includeme(config):
    cfg = config.registry.settings
    enabled_for = make_config_dict(cfg, 'netprofile.auth.enabled_for.')
    default_hash = make_config_dict(cfg, 'netprofile.auth.default_hash.')

    _DEFAULT_HANDLERS.update(default_hash)

    for subject, methods in enabled_for.items():
        methods = aslist(methods)
        default = _DEFAULT_HANDLERS.setdefault(subject, 'scrypt')
        if default not in methods:
            methods.append(default)
        _ENABLED_HANDLERS[subject] = methods

    for scheme in _HANDLERS:
        _HANDLERS[scheme] = _HANDLERS[scheme](cfg)
