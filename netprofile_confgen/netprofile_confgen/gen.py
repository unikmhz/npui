#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Config Generation module - Generator classes
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

import datetime
import os
import logging
import pkg_resources
import pyramid_mako

from itertools import groupby
from pyramid.decorator import reify
from pyramid.path import DottedNameResolver
from mako.template import Template
from sqlalchemy import (
	and_,
	or_
)
from sqlalchemy.orm import (
	attributes,
	joinedload
)

from netprofile.db.connection import DBSession
from netprofile.db.util import populate_related_list
from netprofile_confgen.models import (
	Server,
	ServerType
)

logger = logging.getLogger(__name__)

class ConfigGeneratorFactory(object):
	def __init__(self, cfg, mmgr):
		self.cfg = cfg
		self._gen = {}
		self.mm = mmgr

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

	@reify
	def mako_lookup(self):
		name_resolver = DottedNameResolver()
		lookup_opts = pyramid_mako.parse_options_from_settings(
			self.cfg,
			'mako.',
			name_resolver.maybe_resolve
		)

		lookup_opts.update({
			'output_encoding' : 'utf8',
			'default_filters' : ['str']
		})
		return pyramid_mako.PkgResourceTemplateLookup(**lookup_opts)

	def srvdir(self, srv, xdir=None):
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
		if xdir is not None:
			srvdir = os.path.join(self.outdir, host_name, srv.type.generator_name, xdir)
			if not os.path.isdir(srvdir):
				if os.path.exists(srvdir):
					raise RuntimeError('Output path for host "%s" module "%s" directory "%s" exists but is not a directory.' % (host_name, srv.type.generator_name, xdir))
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
			self._gen[gen_name] = gen
		return self._gen[gen_name]

class ConfigGenerator(object):
	def __init__(self, factory, name):
		self.confgen = factory
		self.name = name

	def generate(self, srv):
		pass

class BIND9Generator(ConfigGenerator):
	@reify
	def dns_srvs(self):
		return DBSession().query(Server).join(ServerType).filter(ServerType.generator_name.startswith('iscbind')).all()

	@reify
	def all_nets(self):
		from netprofile_networks.models import Network
		return DBSession().query(Network).all()

	@reify
	def all_ipv4_revzones(self):
		from netprofile_ipaddresses.models import IPv4ReverseZoneSerial
		return DBSession().query(IPv4ReverseZoneSerial).all()

	@reify
	def all_ipv6_revzones(self):
		from netprofile_ipaddresses.models import IPv6ReverseZoneSerial
		return DBSession().query(IPv6ReverseZoneSerial).all()

	@reify
	def dns_domain_services(self):
		from netprofile_hosts.models import DomainService
		return DBSession().query(DomainService).options(joinedload(DomainService.domain)).filter(DomainService.type_id.in_((1, 2))).all()

	def check_vis(self, ztype, vis):
		from netprofile_domains.models import ObjectVisibility
		if ztype in ('internal', 'generic'):
			return vis in (ObjectVisibility.both, ObjectVisibility.internal)
		return vis in (ObjectVisibility.both, ObjectVisibility.external)

	def host_iplist(self, host):
		from netprofile_hosts.models import HostAliasType
		if host.original:
			return self.host_iplist(host.original)
		ips = []
		ips.extend(host.ipv4_addresses)
		ips.extend(host.ipv6_addresses)
		return ''.join([str(ip) + '; ' for ip in ips])

	def domain_srv_rr(self, domain):
		from netprofile_hosts.models import (
			Host,
			Service
		)
		return DBSession().query(Service).join(Host).filter(or_(
			Service.domain_id == domain.id,
			and_(Service.domain_id == None, Host.domain_id == domain.id)
		))

	def domain_hosts(self, domain):
		from netprofile_hosts.models import Host
		from netprofile_ipaddresses.models import (
			IPv4Address,
			IPv6Address
		)

		# XXX: this is a hack, but it reduces poor ol' MySQL's crunch time by a factor of 10
		sess = DBSession()

		hipv4 = dict((k, list(v)) for k, v in groupby(
			sess.query(IPv4Address).join(IPv4Address.host).filter(Host.domain_id == domain.id),
			lambda ip: ip.host_id
		))
		hipv6 = dict((k, list(v)) for k, v in groupby(
			sess.query(IPv6Address).join(IPv6Address.host).filter(Host.domain_id == domain.id),
			lambda ip: ip.host_id
		))

		for host in domain.hosts:
			attributes.set_committed_value(host, 'ipv4_addresses', hipv4.get(host.id, ()))
			attributes.set_committed_value(host, 'ipv6_addresses', hipv6.get(host.id, ()))
		return domain.hosts

	def dkim_flags(self, domain):
		flags = []
		if domain.dkim_test:
			flags.append('y')
		if not domain.dkim_subdomains:
			flags.append('s')
		if len(flags) > 0:
			return ';t=' + ':'.join(flags)
		return ''

	def all_ipv4(self, host):
		pass

	def generate(self, srv):
		self.confgen.mm.assert_loaded('ipaddresses')
		srvdir = self.confgen.srvdir(srv)

		param = {
			'now' : datetime.datetime.now().replace(microsecond=0),
			'gen' : self,
			'srv' : srv
		}

		conf_tpl = self.confgen.mako_lookup.get_template('netprofile_confgen:templates/confgen/named.conf.mak')
		zone_tpl = self.confgen.mako_lookup.get_template('netprofile_confgen:templates/confgen/named.zone.mak')

		with open(os.path.join(srvdir, 'named.conf'), 'wb') as fd:
			fd.write(conf_tpl.render(**param))

		pridir = self.confgen.srvdir(srv, srv.get_param('dir_bind_pri', 'pri'))
		#secdir = self.confgen.srvdir(srv, srv.get_param('dir_bind_sec', 'sec'))
		revdir = self.confgen.srvdir(srv, srv.get_param('dir_bind_rev', 'rev'))

		splitdns = srv.get_bool_param('split_dns', False)
		for ds in srv.host.domain_services:
			if ds.type_id != 1:
				continue
			hosts = self.domain_hosts(ds.domain)
			if splitdns:
				param.update({
					'domain'   : ds.domain,
					'dname'    : str(ds.domain),
					'service'  : ds,
					'hosts'    : hosts,
					'zonetype' : 'internal'
				})
				with open(os.path.join(pridir, str(ds.domain) + '.internal.zone'), 'wb') as fd:
					fd.write(zone_tpl.render(**param))
				param['zonetype'] = 'external'
				with open(os.path.join(pridir, str(ds.domain) + '.external.zone'), 'wb') as fd:
					fd.write(zone_tpl.render(**param))
			else:
				param.update({
					'domain'   : ds.domain,
					'dname'    : str(ds.domain),
					'service'  : ds,
					'zonetype' : 'generic'
				})

class ISCDHCPGenerator(ConfigGenerator):
	pass

