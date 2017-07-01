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

from pyramid.config import aslist

__all__ = (
	'get_random',
	'get_salt_bytes',
	'get_salt_string',
	'hash_password',
	'verify_password',
	'PasswordHandler',
	'ScryptPasswordHandler',
	'DigestHA1PasswordHandler'
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

	def __init__(self, settings):
		raise NotImplementedError

	def hash(self, user, password):
		raise NotImplementedError

	def verify(self, user, password, hashed):
		raise NotImplementedError

class ScryptPasswordHandler(PasswordHandler):
	scheme = 'scrypt'
	elements = 6

	def __init__(self, settings):
		self.salt_len = int(settings.get('netprofile.crypto.scrypt.salt_length', 20))
		self.n_exp = int(settings.get('netprofile.crypto.scrypt.n_exponent', 14))
		self.r = int(settings.get('netprofile.crypto.scrypt.r_value', 8))
		self.p = int(settings.get('netprofile.crypto.scrypt.p_value', 1))
		self.buflen = int(settings.get('netprofile.crypto.scrypt.buffer_length', 64))

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

	def __init__(self, settings):
		enabled = aslist(settings.get('netprofile.auth.enabled_hashes', ''))
		self.enabled = 'digest-ha1' in enabled
		self.realm = settings.get('netprofile.auth.digest.realm', 'NetProfile UI')

	def hash(self, user, password):
		if not self.enabled:
			return None
		ctx = hashlib.md5()
		ctx.update(('%s:%s:%s' % (user, self.realm, password)).encode())
		return ctx.hexdigest()

	def verify(self, user, password, hashed):
		if not self.enabled:
			return False
		new_hashed = self.hash(user, password)
		return hmac.compare_digest(hashed.encode(), new_hashed.encode())

_HASH_HANDLERS = {
	'scrypt': ScryptPasswordHandler,
	'digest-ha1': DigestHA1PasswordHandler
}

def hash_password(user, password, scheme='scrypt'):
	if scheme not in _HASH_HANDLERS:
		raise ValueError('Unknown hash scheme: %r' % (scheme,))
	return _HASH_HANDLERS[scheme].hash(user, password)

def verify_password(user, password, hashed, scheme=None):
	if scheme is None:
		spl = hashed.split('$', 1)
		if len(spl) != 2:
			raise ValueError('No hash scheme found')
		scheme = spl[0]
	if scheme not in _HASH_HANDLERS:
		raise ValueError('Unknown hash scheme: %r' % (scheme,))
	return _HASH_HANDLERS[scheme].verify(user, password, hashed)

def includeme(config):
	settings = config.registry.settings

	for scheme in _HASH_HANDLERS:
		_HASH_HANDLERS[scheme] = _HASH_HANDLERS[scheme](settings)

