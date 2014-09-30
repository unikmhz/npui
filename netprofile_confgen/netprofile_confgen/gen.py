#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Config Generation module - Generator classes
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
import pkg_resources

from pyramid.decorator import reify

logger = logging.getLogger(__name__)

class ConfigGeneratorFactory(object):
	def __init__(self, cfg):
		self.cfg = cfg
		self._gen = {}

	@reify
	def outdir(self):
		if 'netprofile.confgen.output' not in self.cfg:
			raise RuntimeError('Output directory for configuration generator not defined in INI file.')
		outdir = self.cfg['netprofile.confgen.output']
		if not os.path.isdir(outdir):
			if os.path.exists(outdir):
				raise RuntimeError('Output path exists but is not a directory.')
			os.mkdir(outdir, 0o700)
			logger.warn('Created confgen output directory: %s', outdir)
		return outdir

	def srvdir(self, srv):
		host_name = str(srv.host)
		srvdir = os.path.join(self.outdir, host_name)
		if not os.path.isdir(srvdir):
			if os.path.exists(srvdir):
				raise RuntimeError('Output path for host "%s" exists but is not a directory.' % (host_name,))
			os.mkdir(srvdir, 0o700)
		srvdir = os.path.join(self.outdir, host_name, srv.type.generator_name)
		if not os.path.isdir(srvdir):
			if os.path.exists(srvdir):
				raise RuntimeError('Output path for host "%s" module "%s" exists but is not a directory.' % (host_name, srv.type.generator_name))
			os.mkdir(srvdir, 0o700)
		return srvdir

	def get(self, gen_name):
		if gen_name not in self._gen:
			eps = list(pkg_resources.iter_entry_points('netprofile.confgen.generators', gen_name))
			if len(eps) < 1:
				raise RuntimeError('Unable to find configuration generator class "%s".' % (gen_name,))
			if len(eps) > 1:
				logger.warn('Multiple registrations found for configuration generator class "%s".', gen_name)
			gen_class = eps[0].load()

			gen = gen_class(self, gen_name)

			self._gen[gen_name] = gen_class(self)
		return self._gen[gen_name]

class ConfigGenerator(object):
	def __init__(self, factory, name):
		self.confgen = factory
		self.name = name

	def generate(self, srv):
		pass

class BIND9Generator(ConfigGenerator):
	def generate(self, srv):
		# TODO: determine what modules are available
		srvdir = self.confgen.srvdir(srv)

class ISCDHCPGenerator(ConfigGenerator):
	pass

