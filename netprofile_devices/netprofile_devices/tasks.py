#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Devices module - Tasks
# Copyright © 2016-2017 Alex Unigovsky
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

import logging
import pkg_resources
import transaction
from pyramid.i18n import TranslationStringFactory

from netprofile.celery import (
    app,
    task_meta
)
from netprofile.common import ipaddr
from netprofile.common.hooks import IHookManager

logger = logging.getLogger(__name__)

_ = TranslationStringFactory('netprofile_devices')


@task_meta(cap='HOSTS_PROBE',
           title=_('Probe hosts'))
@app.task
def task_probe_hosts(probe_type='hosts', probe_ids=()):
    app.mmgr.assert_loaded('ipaddresses')

    cfg = app.settings
    hm = app.config.registry.getUtility(IHookManager)
    default_prober = cfg.get('netprofile.devices.host_probers.default',
                             'fping')

    # TODO: support non-default probers
    prober = tuple(pkg_resources.iter_entry_points(
            'netprofile.devices.host_probers',
            default_prober))
    if len(prober) == 0:
        transaction.abort()
        raise RuntimeError('Misconfigured default prober type.')
    cls = prober[0].load()
    prober = cls(cfg)

    queries = []
    ret = []

    hm.run_hook('devices.probe_hosts', probe_type, probe_ids, cfg, hm, queries)

    if len(queries) == 0:
        transaction.abort()
        raise ValueError('Invalid probe parameters specified.')
    try:
        for q in queries:
            for host, addrs in prober.probe(q).items():
                for addr, result in addrs.items():
                    ipa = addr.address
                    if isinstance(ipa, ipaddr.IPv4Address):
                        addrtype = 'v4'
                    elif isinstance(ipa, ipaddr.IPv6Address):
                        addrtype = 'v6'
                    else:
                        continue
                    ret.append({
                        'hostid':   host.id,
                        'host':     str(host),
                        'addrid':   addr.id,
                        'addrtype': addrtype,
                        'addr':     str(ipa),
                        'sent':     result.sent,
                        'returned': result.returned,
                        'min':      result.min,
                        'max':      result.max,
                        'avg':      result.avg,
                        'detected': result.detected
                    })
    except Exception:
        transaction.abort()
        raise

    transaction.abort()
    return ret
