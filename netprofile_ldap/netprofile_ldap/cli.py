#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: LDAP module - CLI commands
# © Copyright 2015 Alex 'Unik' Unigovsky
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

import ldap3
import logging
import tempfile

from cliff.command import Command

from netprofile_ldap.ldap import (
	_gen_attrlist,
	_gen_ldap_object_rdn,
	_get_base
)

class CreateLDIF(Command):
	"""
	Generate a ldapmodify-compatible LDIF to create all stored objects.
	"""

	log = logging.getLogger(__name__)

	def take_action(self, args):
		vlevel = self.app.options.verbose_level
		mm = self.app.mm

		if len(mm.modules) > 0:
			mm.rescan()
		else:
			mm.scan()

		if not mm.load('core'):
			raise RuntimeError('Unable to proceed without core module.')
		if not mm.load_enabled():
			raise RuntimeError('Unable to load enabled modules.')

		settings = self.app.app_config.registry.settings
		sess = self.app.db_session
		browser = mm.get_module_browser()

		LDAPConn = ldap3.Connection(None, client_strategy=ldap3.LDIF)
		LDAPConn.stream = tempfile.TemporaryFile(mode='w+t')

		with LDAPConn as lc:
			for module in browser:
				for model in browser[module]:
					em = browser[module][model]
					info = em.model.__table__.info
					if ('ldap_classes' not in info) or ('ldap_rdn' not in info):
						continue
					cols = em.get_read_columns()
					base = _get_base(em, settings)
					rdn_attr = info.get('ldap_rdn')
					get_attrlist = _gen_attrlist(cols, settings, info)
					get_rdn = _gen_ldap_object_rdn(em, rdn_attr)
					for obj in sess.query(em.model):
						dn = '%s,%s' % (get_rdn(obj), base)
						attrs = get_attrlist(obj)
						attrs = dict((k, v) for k, v in attrs.items() if v is not None)
						lc.add(dn, attributes=attrs)
			lc.stream.seek(0)
			self.app.stdout.write(lc.stream.read())
			lc.stream.close()

