#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Real-time services via Tornado
# © Copyright 2013-2014 Alex 'Unik' Unigovsky
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

import os
import sys

from sqlalchemy import engine_from_config

from pyramid.config import Configurator
from pyramid.paster import (
	get_appsettings,
	setup_logging
)

from netprofile import (
	VHostPredicate,
	locale_neg
)
from netprofile.db.connection import DBSession
from netprofile.common import (
	cache,
	rt
)
from netprofile.common.modules import IModuleManager
from netprofile.common.factory import RootFactory

def usage(argv):
	cmd = os.path.basename(argv[0])
	print('usage: %s <config_uri>\n'
		'(example: "%s development.ini")' % (cmd, cmd)) 
	sys.exit(1)

def main(argv=sys.argv):
	if len(argv) != 2:
		usage(argv)
	config_uri = argv[1]
	setup_logging(config_uri)
	settings = get_appsettings(config_uri)
	engine = engine_from_config(settings, 'sqlalchemy.')
	DBSession.configure(bind=engine)
	cache.cache = cache.configure_cache(settings)

	config = Configurator(
		settings=settings,
		root_factory=RootFactory,
		locale_negotiator=locale_neg
	)
	config.add_route_predicate('vhost', VHostPredicate)
	config.add_view_predicate('vhost', VHostPredicate)
	config.commit()

	mmgr = config.registry.getUtility(IModuleManager)
	mmgr.load('core')
	mmgr.load_enabled()

	rts = rt.configure(mmgr, config.registry)
	return rt.run(rts)

if __name__ == '__main__':
	sys.exit(main(sys.argv))

