#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Initial database creation script
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
#
# NB: Used only once during initial NetProfile installation.

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

from pyramid import threadlocal
from pyramid.paster import (
	get_appsettings,
	setup_logging
)
from pyramid.interfaces import IRendererFactory
from pyramid.path import DottedNameResolver
import pyramid_mako

from netprofile.db.connection import (
	DBSession,
	Base
)

from netprofile.common import cache
from netprofile.common.modules import ModuleManager

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

	reg = threadlocal.get_current_registry()
	factory = pyramid_mako.MakoRendererFactory()

	name_resolver = DottedNameResolver()
	lookup_opts = pyramid_mako.parse_options_from_settings(settings, 'mako.', name_resolver.maybe_resolve)
	lookup_opts.update({
		'default_filters' : ['context[\'self\'].ddl.ddl_fmt']
	})
	factory.lookup = pyramid_mako.PkgResourceTemplateLookup(**lookup_opts)

	reg.registerUtility(factory, IRendererFactory, name='.mak')

	ModuleManager.prepare()
	Base.metadata.create_all(engine)

