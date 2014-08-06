#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Config Generation module - Tasks
# © Copyright 2014 Alex 'Unik' Unigovsky
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
import os
import shutil

from netprofile.celery import app

from netprofile.db.connection import DBSession

logger = logging.getLogger(__name__)

def _prep_confgen(cfg):
	if 'confgen.station_id' not in cfg:
		raise RuntimeError('Station ID is not defined in INI file.')
	st_id = int(cfg['confgen.station_id'])
	if 'confgen.output' not in cfg:
		raise RuntimeError('Output directory for configuration generator not defined in INI file.')
	outdir = cfg['confgen.output']
	if not os.path.isdir(outdir):
		if os.path.exists(outdir):
			raise RuntimeError('Output path exists but is not a directory.')
		os.mkdir(outdir, 0o700)
		logger.warn('Created confgen output directory: %s', outdir)
	return (st_id, outdir)

@app.task
def task_generate(station_ids=()):
	cfg = app.settings
	st_id, outdir = _prep_confgen(cfg)

	pass

