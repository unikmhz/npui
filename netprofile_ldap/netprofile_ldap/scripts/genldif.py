#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.config import Configurator
from pyramid.paster import (
	get_appsettings,
	setup_logging
)

from netprofile.db.connection import (
	DBSession,
	Base
)

from netprofile.common import cache
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
	cache.cache = cache.configure_cache(settings)
	engine = engine_from_config(settings, 'sqlalchemy.')
	DBSession.configure(bind=engine)

	config = Configurator(
		settings=settings,
		root_factory=RootFactory
	)

	mmgr = config.registry.getUtility(IModuleManager)
	mmgr.load('core')
	mmgr.load_enabled()

	mb = mmgr.get_module_browser()

#	ModuleManager.prepare()
#	Base.metadata.create_all(engine)

