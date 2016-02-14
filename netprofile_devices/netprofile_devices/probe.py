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

import io
import os
import subprocess
from collections import namedtuple

HostProbeResult = namedtuple('HostProbeResult', ('sent', 'returned', 'min', 'max', 'avg'))

class HostProber(object):
	def __init__(self, cfg):
		self.cfg = cfg

	def probe(self, addrs):
		raise NotImplementedError

class FPingProber(HostProber):
	def _arg(self, name, kwargs, defvalue=None):
		return kwargs.get(name, self.cfg.get('netprofile.devices.fping.' + name, defvalue))

	def _fping_args(self, **kwargs):
		cfg = self.cfg
		fping_bin = cfg.get('netprofile.devices.fping.path')
		if fping_bin is None:
			raise RuntimeError('Path to fping binary is not configured.')
		if not os.path.isfile(fping_bin):
			raise RuntimeError('Can\'t locate configured fping binary.')
		if not os.access(fping_bin, os.X_OK):
			raise RuntimeError('Configured fping binary is not executable by current user.')

		fping_interval = int(self._arg('packet_interval', kwargs, 12))
		fping_tgt_interval = int(self._arg('per_target_packet_interval', kwargs, 110))
		fping_bytes = int(self._arg('packet_size', kwargs, 1400))
		fping_count = int(self._arg('packet_count', kwargs, 3))

		fping_srcaddr = self._arg('source_address', kwargs)
		fping_srcif = self._arg('source_interface', kwargs)

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

	def _fping_run(self, addrs, **kwargs):
		args = self._fping_args(**kwargs)
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
				avg=rtt_sum / (cnt_total - cnt_failed)
			)

		return ret

	def probe(self, addrs):
		return self._fping_run(addrs)

class FPingARPProber(FPingProber):
	def probe(self, addrs):
		ret = self._fping_run(addrs)
		return ret

