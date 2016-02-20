#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Devices module - Host probers
# © Copyright 2016 Alex 'Unik' Unigovsky
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

__all__ = [
	'HostProbeResult',
	'HostProber',
	'FPingProber',
	'FPingARPProber'
]

import io
import os
import subprocess
from collections import (
	defaultdict,
	namedtuple
)
from sqlalchemy.orm import joinedload

from netprofile.db.connection import DBSession

HostProbeResult = namedtuple('HostProbeResult', ('sent', 'returned', 'min', 'max', 'avg', 'detected'))

def _clone_with_detected(result, detected):
	return HostProbeResult(
		sent=result.sent,
		returned=result.returned,
		min=result.min,
		max=result.max,
		avg=result.avg,
		detected=detected
	)

class HostProber(object):
	def __init__(self, cfg):
		self.cfg = cfg

	def probe(self, hosts):
		raise NotImplementedError

class FPingProber(HostProber):
	def _arg(self, name, kwargs, defvalue=None):
		return kwargs.get(name, self.cfg.get('netprofile.devices.fping.' + name, defvalue))

	def _arg6(self, name, kwargs, defvalue=None):
		return kwargs.get(name, self.cfg.get('netprofile.devices.fping6.' + name, defvalue))

	def _fping_args(self, v6=False, **kwargs):
		cfg = self.cfg
		if v6:
			arg = self._arg6
			fping_bin = cfg.get('netprofile.devices.fping6.path')
		else:
			arg = self._arg
			fping_bin = cfg.get('netprofile.devices.fping.path')
		if fping_bin is None:
			raise RuntimeError('Path to fping binary is not configured.')
		if not os.path.isfile(fping_bin):
			raise RuntimeError('Can\'t locate configured fping binary.')
		if not os.access(fping_bin, os.X_OK):
			raise RuntimeError('Configured fping binary is not executable by current user.')

		fping_interval = int(arg('packet_interval', kwargs, 12))
		fping_tgt_interval = int(arg('per_target_packet_interval', kwargs, 110))
		fping_bytes = int(arg('packet_size', kwargs, 1400))
		fping_count = int(arg('packet_count', kwargs, 3))

		fping_srcaddr = arg('source_address', kwargs)
		fping_srcif = arg('source_interface', kwargs)

		ret = [
			fping_bin,
			'-A', '-q', '-e',
			'-i', str(fping_interval),
			'-t', str(fping_tgt_interval),
			'-p', str(fping_tgt_interval),
			'-b', str(fping_bytes),
			'-C', str(fping_count)
		]
		if fping_srcaddr is not None:
			ret.extend(('-S', str(fping_srcaddr)))
		if fping_srcif is not None:
			ret.extend(('-I', str(fping_srcif)))
		return ret

	def _fping_run(self, addrs, v6=False, **kwargs):
		args = self._fping_args(v6=v6, **kwargs)
		proc = subprocess.Popen(
			args,
			shell=False,
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			bufsize=1,
			universal_newlines=True
		)

		ret = dict()
		stdout, stderr = proc.communicate('\n'.join(addrs))
		for outstr in stdout.splitlines():
			addr, rtts = outstr.split(':', 1)
			rtts = rtts.strip().split()
			cnt_total = len(rtts)
			cnt_failed = 0
			rtt_min = None
			rtt_max = None
			rtt_sum = 0.0
			for rtt in rtts:
				if rtt == '-':
					cnt_failed += 1
					continue
				rtt = float(rtt)
				rtt_sum += rtt
				if (rtt_min is None) or (rtt_min > rtt):
					rtt_min = rtt
				if (rtt_max is None) or (rtt_max < rtt):
					rtt_max = rtt

			ret[addr.strip()] = HostProbeResult(
				sent=cnt_total,
				returned=(cnt_total - cnt_failed),
				min=rtt_min,
				max=rtt_max,
				avg=None if (cnt_total == cnt_failed) else (rtt_sum / (cnt_total - cnt_failed)),
				detected=True if cnt_total > cnt_failed else False
			)

		return ret

	def _fping_addrs(self, addrs, ret, v6=False):
		ping_addrs = dict()
		for addr in addrs:
			addrobj = addr.address
			if addrobj is not None:
				ping_addrs[str(addrobj)] = addr
		if len(ping_addrs) > 0:
			for addrobj, proberes in self._fping_run(ping_addrs.keys(), v6).items():
				addr = ping_addrs[addrobj]
				ret[addr.host][addr] = proberes

	def probe(self, hosts):
		v4addrs = []
		v6addrs = []
		ret = defaultdict(dict)

		for host in hosts:
			v4addrs.extend(host.ipv4_addresses)
			v6addrs.extend(host.ipv6_addresses)

		if len(v4addrs) > 0:
			self._fping_addrs(v4addrs, ret, False)
		if len(v6addrs) > 0:
			self._fping_addrs(v6addrs, ret, True)

		return ret

class FPingARPProber(FPingProber):
	def probe(self, hosts):
		from netprofile_networks.models import NetworkService

		sess = DBSession()
		v4addrs = []
		v6addrs = []
		nets = set()
		failed = set()
		netmgmt = dict()
		ret = defaultdict(dict)
		gw_ifindexes = defaultdict(set)

		for host in hosts:
			for v4addr in host.ipv4_addresses:
				nets.add(v4addr.network)
				v4addrs.append(v4addr)
			for v6addr in host.ipv6_addresses:
				nets.add(v6addr.network)
				v6addrs.append(v6addr)

		for net in nets:
			mgmt = net.management_device
			if (mgmt is None) or (mgmt.host is None):
				continue
			if mgmt in netmgmt:
				handler = netmgmt[mgmt]
			else:
				handler = mgmt.get_handler()
				if handler is None:
					continue
				netmgmt[mgmt] = handler

			# Get network gateway IPs
			gwq = sess.query(NetworkService).filter(
				NetworkService.network == net,
				NetworkService.type_id == 4
			).options(joinedload(NetworkService.host))
			for service in gwq:
				# Get ifIndex of gateway interfaces
				for addr in service.host.ipv4_addresses + service.host.ipv6_addresses:
					ifindex = handler.ifindex_by_address(addr.address)
					if ifindex is not None:
						gw_ifindexes[net].add(ifindex)

		# Try to clear addresses from neighbor tables
		for addr in v4addrs + v6addrs:
			net = addr.network
			mgmt = net.management_device
			if (net not in gw_ifindexes) or (mgmt not in netmgmt):
				failed.add(addr)
				continue
			cleared = False
			for gw_ifindex in gw_ifindexes[net]:
				if netmgmt[mgmt].clear_arp_entry(gw_ifindex, addr.address):
					cleared = True
					break
			if not cleared:
				failed.add(addr)

		# Spawn fping, collect results
		if len(v4addrs) > 0:
			self._fping_addrs(v4addrs, ret, False)
		if len(v6addrs) > 0:
			self._fping_addrs(v6addrs, ret, True)

		# Check newly created neighbor entries to detect hosts behind firewalls
		for host, addrs in ret.items():
			for addr, proberes in addrs.items():
				if addr in failed:
					continue
				if not proberes.detected:
					mgmt = addr.network.management_device
					if netmgmt[mgmt].get_arp_entry == 3:
						ret[host][addr] = _clone_with_detected(proberes, True)

		return ret

