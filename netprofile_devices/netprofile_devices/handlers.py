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

import snimpy.manager as mgr

from pyramid.decorator import reify

class TableProxy(object):
	def __init__(self, hdl, table, idx):
		self._hdl = hdl
		self._table = table
		self._idx = idx

	def __getattr__(self, attr):
		return getattr(self._hdl.snmp_ro, attr)[self._idx]

class NetworkDeviceHandler(object):
	def __init__(self, devtype, dev, req):
		self.type = devtype
		self.dev = dev
		self.req = req

	@reify
	def snmp_ro(self):
		return self.dev.snmp_context(self.req)

	@reify
	def snmp_rw(self):
		if not self.dev.snmp_has_rw_context:
			return self.snmp_ro
		return self.dev.snmp_context(self.req, is_rw=True)

	@property
	def interfaces(self):
		mgr.load('IF-MIB')
		tbl = self.snmp_ro.ifIndex.proxy.table
		for idx in self.snmp_ro.ifIndex:
			yield TableProxy(self, tbl, idx)

	@property
	def base_ports(self):
		mgr.load('BRIDGE-MIB')
		tbl = self.snmp_ro.dot1dBasePort.proxy.table
		for baseport in self.snmp_ro.dot1dBasePort:
			yield TableProxy(self, tbl, baseport)

	@property
	def vlans(self):
		if self.type.has_flag('SNMP: CISCO-VTP-MIB'):
			mgr.load('CISCO-VTP-MIB')
			tbl = self.snmp_ro.vtpVlanState.proxy.table
			for mgmtid, vlanid in self.snmp_ro.vtpVlanState:
				yield TableProxy(self, tbl, (mgmtid, vlanid))
		else:
			mgr.load('Q-BRIDGE-MIB')
			tbl = self.snmp_ro.dot1qVlanFdbId.proxy.table
			for timemark, vlanid in self.snmp_ro.dot1qVlanFdbId:
				yield TableProxy(self, tbl, (timemark, vlanid))

