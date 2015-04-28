#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Devices module - Bundled device handlers
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

import snimpy.manager

from pyramid.decorator import reify

class NetworkDeviceHandler(object):
	def __init__(self, devtype, dev, req):
		self.type = devtype
		self.dev = dev
		self.req = req

	@reify
	def snmp_ro(self):
		return self.dev.snmp_context(req)

	@reify
	def snmp_rw(self):
		if not self.dev.snmp_has_rw_context:
			return self.snmp_ro
		return self.dev.snmp_context(req, is_rw=True)

