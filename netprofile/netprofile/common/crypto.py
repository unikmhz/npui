#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Cryptography helper routines
# © Copyright 2017 Alex 'Unik' Unigovsky
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

import base64
import hashlib
import hmac
import random
import scrypt
import string

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
	'PlainTextPasswordHandler'
)

def get_random(system_rng=True):
	if system_rng:
		try:
			return random.SystemRandom()
		except NotImplementedError:  # pragma: no cover
			pass
	return random.Random()

def get_salt_bytes(length, chars=bytes(string.ascii_letters + string.digits, 'utf8')):
	if not isinstance(chars, bytes):
		chars = chars.encode('ascii')
	rnd = get_random()
	return bytes(rnd.choice(chars) for _ in range(length))

def get_salt_string(length, chars=string.ascii_letters + string.digits):
	rnd = get_random()
	return ''.join(rnd.choice(chars) for _ in range(length))

class PasswordHandler(object):
	scheme = 'undef'
	elements = 1

	def _pack(self, *args):
		if len(args) != self.elements:
			raise ValueError('Invalid hash format')
		return '$'.join((self.scheme,) + args)

	def _unpack(self, packed):
		if isinstance(packed, bytes):
			packed = packed.decode()
		unpacked = packed.split('$')
		if len(unpacked) != self.elements + 1:
			raise ValueError('Invalid hash format')
		if unpacked.pop(0) != self.scheme:
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
	scheme = 'scrypt'
	elements = 6

	def __init__(self, cfg):
		PasswordHandler.__init__(self, cfg)
		self.salt_len = int(cfg.get('netprofile.crypto.scrypt.salt_length', 20))
		self.n_exp = int(cfg.get('netprofile.crypto.scrypt.n_exponent', 14))
		self.r = int(cfg.get('netprofile.crypto.scrypt.r_value', 8))
		self.p = int(cfg.get('netprofile.crypto.scrypt.p_value', 1))
		self.buflen = int(cfg.get('netprofile.crypto.scrypt.buffer_length', 64))

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
	scheme = 'digest-ha1'
	elements = 1

	def __init__(self, cfg):
		PasswordHandler.__init__(self, cfg)
		self.realm = cfg.get('netprofile.auth.digest.realm', 'NetProfile UI')

	def hash(self, user, password):
		ctx = hashlib.md5()
		ctx.update(('%s:%s:%s' % (user, self.realm, password)).encode())
		return ctx.hexdigest()

class NTLMPasswordHandler(PasswordHandler):
	scheme = 'ntlm'
	elements = 1

	def hash(self, user, password):
		ctx = hashlib.new('md4')
		ctx.update(password.encode('utf-16le'))
		return ctx.hexdigest()

class PlainTextPasswordHandler(PasswordHandler):
	scheme = 'plain'
	elements = 1

	def hash(self, user, password):
		if isinstance(password, bytes):
			return password.decode()
		return password

	def verify(self, user, password, hashed):
		if isinstance(password, bytes):
			password = password.decode()
		if isinstance(hashed, bytes):
			hashed = hashed.decode()
		return hmac.compare_digest(password, hashed)

_HANDLERS = {
	'scrypt': ScryptPasswordHandler,
	'digest-ha1': DigestHA1PasswordHandler,
	'ntlm': NTLMPasswordHandler,
	'plain': PlainTextPasswordHandler
}
_ENABLED_HANDLERS = {}
_DEFAULT_HANDLERS = {}

def hash_password(user, password, scheme=None, subject='users'):
	if scheme is None:
		scheme = _DEFAULT_HANDLERS[subject]
	if scheme not in _ENABLED_HANDLERS[subject]:
		return None
	if scheme not in _HANDLERS:
		raise ValueError('Unknown hash scheme: %r' % (scheme,))
	return _HANDLERS[scheme].hash(user, password)

def verify_password(user, password, hashed, scheme=None, subject='users'):
	if scheme is None:
		spl = hashed.split('$', 1)
		if len(spl) == 2:
			scheme = spl[0]
		else:
			scheme = _DEFAULT_HANDLERS[subject]
	if scheme not in _ENABLED_HANDLERS[subject]:
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

