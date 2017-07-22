#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Devices module - Bundled device handlers
# Copyright © 2015-2017 Alex Unigovsky
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

import snimpy.manager as mgr
from snimpy.snmp import (
    SNMPNoCreation,
    SNMPNoSuchObject
)
from pyramid.decorator import reify

from netprofile.common import ipaddr


class TableProxy(object):
    def __init__(self, hdl, table, idx):
        self._hdl = hdl
        self._table = table
        self._idx = idx

    def __getattr__(self, attr):
        return getattr(self._hdl.snmp_ro, attr)[self._idx]


class NetworkDeviceHandler(object):
    def __init__(self, devtype, dev):
        self.type = devtype
        self.dev = dev

    @reify
    def snmp_ro(self):
        return self.dev.snmp_context()

    @reify
    def snmp_rw(self):
        if not self.dev.snmp_has_rw_context:
            return self.snmp_ro
        return self.dev.snmp_context(is_rw=True)

    def load_mib(self, mib):
        flagname = 'SNMP: ' + mib
        if not self.type.has_flag(flagname):
            raise NotImplementedError('Current device does not implement %s' %
                                      (mib,))
        mgr.load(mib)

    @property
    def interfaces(self):
        self.load_mib('IF-MIB')
        tbl = self.snmp_ro.ifIndex.proxy.table
        for idx in self.snmp_ro.ifIndex:
            yield TableProxy(self, tbl, idx)

    @property
    def base_ports(self):
        self.load_mib('BRIDGE-MIB')
        tbl = self.snmp_ro.dot1dBasePort.proxy.table
        for baseport in self.snmp_ro.dot1dBasePort:
            yield TableProxy(self, tbl, baseport)

    @property
    def vlans(self):
        self.load_mib('Q-BRIDGE-MIB')
        tbl = self.snmp_ro.dot1qVlanFdbId.proxy.table
        for timemark, vlanid in self.snmp_ro.dot1qVlanFdbId:
            yield TableProxy(self, tbl, (timemark, vlanid))

    def ifindex_by_address(self, addr):
        self.load_mib('IP-MIB')

        if isinstance(addr, ipaddr.IPv4Address):
            addrtype = 1
        elif isinstance(addr, ipaddr.IPv6Address):
            addrtype = 2
        else:
            return None

        try:
            return int(self.snmp_ro.ipAddressIfIndex[addrtype, str(addr)])
        except SNMPNoSuchObject:
            pass
        if addrtype == 1:
            try:
                return int(self.snmp_ro.ipAdEntIfIndex[str(addr)])
            except SNMPNoSuchObject:
                pass
        return None

    def get_arp_entry(self, ifindex, addr):
        self.load_mib('IP-MIB')

        if isinstance(addr, ipaddr.IPv4Address):
            addrtype = 1
        elif isinstance(addr, ipaddr.IPv6Address):
            addrtype = 2
        else:
            return None

        try:
            return int(self.snmp_ro.ipNetToPhysicalType[ifindex, addrtype,
                                                        str(addr)])
        except SNMPNoSuchObject:
            pass
        if addrtype == 1:
            try:
                return int(self.snmp_ro.ipNetToMediaType[ifindex, str(addr)])
            except SNMPNoSuchObject:
                pass
        return None

    def clear_arp_entry(self, ifindex, addr):
        self.load_mib('IP-MIB')

        if isinstance(addr, ipaddr.IPv4Address):
            addrtype = 1
        elif isinstance(addr, ipaddr.IPv6Address):
            addrtype = 2
        else:
            return False

        try:
            # 2 = invalid
            self.snmp_rw.ipNetToPhysicalType[ifindex, addrtype, str(addr)] = 2
            return True
        except (SNMPNoCreation, SNMPNoSuchObject):
            pass
        if addrtype == 1:
            try:
                # 2 = invalid
                self.snmp_rw.ipNetToMediaType[ifindex, str(addr)] = 2
                return True
            except (SNMPNoCreation, SNMPNoSuchObject):
                pass

        return False

    def get_arp_table(self, ifindex=None):
        self.load_mib('IP-MIB')

        tfilter = []
        if ifindex is not None:
            tfilter.append(ifindex)
        tbl = []

        try:
            for idx, phys in self.snmp_ro.ipNetToPhysicalPhysAddress.iteritems(
                    *tfilter):
                if idx[1] == 1:
                    addr = ipaddr.IPv4Address(str(idx[2]))
                elif idx[1] == 2:
                    addr = ipaddr.IPv6Address(str(idx[2]))
                else:
                    continue
                tbl.append((int(idx[0]), addr, phys._toBytes()))
        except SNMPNoSuchObject:
            for idx, phys in self.snmp_ro.ipNetToMediaPhysAddress.iteritems(
                    *tfilter):
                tbl.append((int(idx[0]),
                            ipaddr.IPv4Address(idx[1]),
                            phys._toBytes()))

        return tbl
