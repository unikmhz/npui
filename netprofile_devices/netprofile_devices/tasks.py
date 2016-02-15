#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Devices module - Tasks
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

import logging
import pkg_resources
import transaction
from collections import defaultdict

from netprofile.celery import (
	app,
	task_cap
)
from netprofile.common.hooks import IHookManager

logger = logging.getLogger(__name__)

@task_cap('HOSTS_PROBE')
@app.task
def task_probe_hosts(probe_type='hosts', probe_ids=()):
	app.mmgr.assert_loaded('ipaddresses')

	cfg = app.settings
	hm = app.config.registry.getUtility(IHookManager)
	default_prober = cfg.get('netprofile.devices.host_probers.default', 'fping')

	# TODO: support non-default probers
	prober = tuple(pkg_resources.iter_entry_points('netprofile.devices.host_probers', default_prober))
	if len(prober) == 0:
		raise RuntimeError('Misconfigured default prober type.')
	cls = prober[0].load()
	prober = cls(cfg)

	queries = []
	ret = defaultdict(dict)

	hm.run_hook('devices.probe_hosts', probe_type, probe_ids, cfg, hm, queries)

	if len(queries) == 0:
		raise ValueError('Invalid probe parameters specified.')
	for q in queries:
		for host, addrs in prober.probe(q).items():
			for addr, result in addrs.items():
				ret[host.id][addr.id] = result

	transaction.abort()
	return ret

