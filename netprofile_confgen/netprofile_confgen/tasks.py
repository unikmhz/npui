#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Config Generation module - Tasks
# © Copyright 2014-2015 Alex 'Unik' Unigovsky
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
import redis
import transaction

from pyramid.i18n import TranslationStringFactory

from netprofile.celery import (
	app,
	task_cap
)
from netprofile.db.connection import DBSession
from netprofile.common.util import make_config_dict
from netprofile.common.locale import sys_localizer

from netprofile_confgen.models import Server
from netprofile_confgen.gen import ConfigGeneratorFactory

logger = logging.getLogger(__name__)

_ = TranslationStringFactory('netprofile_confgen')

@task_cap('SRV_CONFGEN')
@app.task
def task_generate(srv_ids=(), station_ids=()):
	cfg = app.settings
	rconf = make_config_dict(cfg, 'netprofile.rt.redis.')
	factory = ConfigGeneratorFactory(cfg, app.mmgr)

	ret = []
	sess = DBSession()
	rsess = redis.Redis(**rconf)
	loc = sys_localizer(app.mmgr.cfg.registry)

	q = sess.query(Server)
	if len(srv_ids) > 0:
		q = q.filter(Server.id.in_(srv_ids))
	if len(station_ids) > 0:
		q = q.filter(Server.host_id.in_(station_ids))
	for srv in q:
		gen = factory.get(srv.type.generator_name)
		logger.info('Generating config of type %s for host %s', srv.type.generator_name, str(srv.host))
		gen.generate(srv)
		ret.append(loc.translate(_('Successfully generated %s configuration for host %s.')) % (
			srv.type.name,
			str(srv.host)
		))

	hosts = factory.deploy()
	ret.append(loc.translate(_('Successfully deployed configuration for hosts: %s.')) % (', '.join(hosts),))

	factory.restore_umask()
	transaction.commit()
	return ret

