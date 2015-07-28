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

import collections
import datetime
import logging
import os
import pkg_resources
import pyramid_mako
import shutil

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
	contains_eager,
	joinedload
)

from netprofile.db.connection import DBSession
from netprofile.db.clauses import Binary16ToDecimal
from netprofile.db.util import populate_related_list
from netprofile_confgen.models import (
	Server,
	ServerType
)

logger = logging.getLogger(__name__)

class DeploymentTemplateLanguage(object):
	pass

class ERBTemplateLanguage(DeploymentTemplateLanguage):
	def var(self, tname):
		return '<%%= @%s %%>' % (tname,)

	def loop_var(self, lname):
		return '<%%= %s %%>' % (lname,)

	def if_var(self, tname):
		return '<%% if @%s -%%>' % (tname,)

	def for_in(self, iname, tname):
		return '<%% @%s.each do |%s| -%%>' % (tname, iname)

	@property
	def endif(self):
		return '<% end -%>'

	@property
	def endfor(self):
		return '<% end -%>'

	@property
	def file_suffix(self):
		return '.erb'

class ConfigGeneratorFactory(object):
	def __init__(self, cfg, mmgr):
		self.cfg = cfg
		self._gen = {}
		self.mm = mmgr
		self.deploy_files = set()
		self.deploy_templates = set()
		self.orig_umask = os.umask(0o027)

	@reify
	def outdir_files(self):
		if 'netprofile.confgen.files_output_dir' not in self.cfg:
			raise RuntimeError('File output directory for configuration generator not defined in INI file.')
		outdir = self.cfg['netprofile.confgen.files_output_dir']
		if not os.path.isdir(outdir):
			if os.path.exists(outdir):
				raise RuntimeError('File output path exists but is not a directory.')
			os.mkdir(outdir, 0o750)
			logger.warn('Created confgen file output directory: %s', outdir)
		return outdir

	@reify
	def outdir_templates(self):
		if 'netprofile.confgen.templates_output_dir' not in self.cfg:
			raise RuntimeError('Template output directory for configuration generator not defined in INI file.')
		outdir = self.cfg['netprofile.confgen.templates_output_dir']
		if not os.path.isdir(outdir):
			if os.path.exists(outdir):
				raise RuntimeError('Template output path exists but is not a directory.')
			os.mkdir(outdir, 0o750)
			logger.warn('Created confgen template output directory: %s', outdir)
		return outdir

	@reify
	def depdir_files(self):
		deptype = self.cfg.get('netprofile.confgen.deployment_type', 'puppet')
		if deptype == 'puppet':
			return self.cfg.get('netprofile.confgen.puppet.files_dir', '/etc/puppet/modules/npconfgen/files/generated')

	@reify
	def depdir_templates(self):
		deptype = self.cfg.get('netprofile.confgen.deployment_type', 'puppet')
		if deptype == 'puppet':
			return self.cfg.get('netprofile.confgen.puppet.templates_dir', '/etc/puppet/modules/npconfgen/templates/generated')

	def deptpl(self):
		deptype = self.cfg.get('netprofile.confgen.deployment_type', 'puppet')
		if deptype == 'puppet':
			return ERBTemplateLanguage()

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

	def restore_umask(self):
		os.umask(self.orig_umask)

	def srvdir_files(self, srv, xdir=None):
		host_name = str(srv.host)
		srvdir = os.path.join(self.outdir_files, host_name)
		if not os.path.isdir(srvdir):
			if os.path.exists(srvdir):
				raise RuntimeError('File output path for host "%s" exists but is not a directory.' % (host_name,))
			os.mkdir(srvdir, 0o750)
		srvdir = os.path.join(srvdir, srv.type.generator_name)
		if not os.path.isdir(srvdir):
			if os.path.exists(srvdir):
				raise RuntimeError('File output path for host "%s" module "%s" exists but is not a directory.' % (host_name, srv.type.generator_name))
			os.mkdir(srvdir, 0o750)
		if xdir is not None:
			srvdir = os.path.join(srvdir, xdir)
			if not os.path.isdir(srvdir):
				if os.path.exists(srvdir):
					raise RuntimeError('File output path for host "%s" module "%s" directory "%s" exists but is not a directory.' % (host_name, srv.type.generator_name, xdir))
				os.mkdir(srvdir, 0o750)
		self.deploy_files.add(host_name)
		return srvdir

	def srvdir_templates(self, srv, xdir=None):
		host_name = str(srv.host)
		srvdir = os.path.join(self.outdir_templates, host_name)
		if not os.path.isdir(srvdir):
			if os.path.exists(srvdir):
				raise RuntimeError('Template output path for host "%s" exists but is not a directory.' % (host_name,))
			os.mkdir(srvdir, 0o750)
		srvdir = os.path.join(srvdir, srv.type.generator_name)
		if not os.path.isdir(srvdir):
			if os.path.exists(srvdir):
				raise RuntimeError('Template output path for host "%s" module "%s" exists but is not a directory.' % (host_name, srv.type.generator_name))
			os.mkdir(srvdir, 0o750)
		if xdir is not None:
			srvdir = os.path.join(srvdir, xdir)
			if not os.path.isdir(srvdir):
				if os.path.exists(srvdir):
					raise RuntimeError('Template output path for host "%s" module "%s" directory "%s" exists but is not a directory.' % (host_name, srv.type.generator_name, xdir))
				os.mkdir(srvdir, 0o750)
		self.deploy_templates.add(host_name)
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

	def deploy(self):
		for host_name in self.deploy_files:
			src_path = os.path.join(self.outdir_files, host_name)
			dep_path = os.path.join(self.depdir_files, host_name)
			dep_path_old = dep_path + '.confgen_old'
			dep_path_new = dep_path + '.confgen_new'
			if os.path.exists(dep_path_new):
				shutil.rmtree(dep_path_new)
			shutil.move(src_path, dep_path_new)
			if os.path.exists(dep_path):
				if os.path.exists(dep_path_old):
					shutil.rmtree(dep_path_old)
				shutil.move(dep_path, dep_path_old)
			shutil.move(dep_path_new, dep_path)
		for host_name in self.deploy_templates:
			src_path = os.path.join(self.outdir_templates, host_name)
			dep_path = os.path.join(self.depdir_templates, host_name)
			dep_path_old = dep_path + '.confgen_old'
			dep_path_new = dep_path + '.confgen_new'
			if os.path.exists(dep_path_new):
				shutil.rmtree(dep_path_new)
			shutil.move(src_path, dep_path_new)
			if os.path.exists(dep_path):
				if os.path.exists(dep_path_old):
					shutil.rmtree(dep_path_old)
				shutil.move(dep_path, dep_path_old)
			shutil.move(dep_path_new, dep_path)
		ret = self.deploy_files.union(self.deploy_templates)
		self.deploy_files = set()
		self.deploy_templates = set()
		return ret

class ConfigGenerator(object):
	def __init__(self, factory, name):
		self.confgen = factory
		self.name = name

	def generate(self, srv):
		pass

class BIND9Generator(ConfigGenerator):
	@reify
	def dns_srvs(self):
		return DBSession().query(Server).join(Server.type).filter(ServerType.generator_name.startswith('iscbind')).all()

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
		if host.original:
			return self.host_iplist(host.original)
		ips = []
		ips.extend(host.ipv4_addresses)
		ips.extend(host.ipv6_addresses)
		return ''.join(str(ip) + '; ' for ip in ips)

	def domain_srv_rr(self, domain):
		from netprofile_hosts.models import (
			Host,
			Service
		)
		return DBSession().query(Service).join(Host).filter(or_(
			Service.domain_id == domain.id,
			and_(Service.domain_id == None, Host.domain_id == domain.id)
		))

	def revzone_ipv4(self, rz):
		from netprofile_networks.models import Network
		from netprofile_ipaddresses.models import IPv4Address
		return DBSession().query(IPv4Address).join(IPv4Address.host).join(IPv4Address.network).options(
			contains_eager(IPv4Address.host),
			contains_eager(IPv4Address.network)
		).filter(
			(Network.ipv4_address + IPv4Address.offset) >= int(rz.ipv4_network.network),
			(Network.ipv4_address + IPv4Address.offset) <= int(rz.ipv4_network.broadcast)
		)

	def revzone_ipv6(self, rz):
		from netprofile_networks.models import Network
		from netprofile_ipaddresses.models import IPv6Address
		return DBSession().query(IPv6Address).join(IPv6Address.host).join(IPv6Address.network).options(
			contains_eager(IPv6Address.host),
			contains_eager(IPv6Address.network)
		).filter(
			(Binary16ToDecimal(Network.ipv6_address) + IPv6Address.offset) >= int(rz.ipv6_network.network),
			(Binary16ToDecimal(Network.ipv6_address) + IPv6Address.offset) <= int(rz.ipv6_network.broadcast)
		)

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

	def generate_zone(self, param, ds, dname, outdir, tpl, split_dns=False, is_root=False):
		if is_root:
			param['hosts'] = self.domain_hosts(ds.domain)
		if split_dns:
			param.update({
				'domain'   : ds.domain,
				'dname'    : dname,
				'service'  : ds,
				'zonetype' : 'internal'
			})
			with open(os.path.join(outdir, dname + '.internal.zone'), 'wb') as fd:
				fd.write(tpl.render(**param))
			param['zonetype'] = 'external'
			with open(os.path.join(outdir, dname + '.external.zone'), 'wb') as fd:
				fd.write(tpl.render(**param))
		else:
			param.update({
				'domain'   : ds.domain,
				'dname'    : dname,
				'service'  : ds,
				'zonetype' : 'generic'
			})
			with open(os.path.join(outdir, dname + '.generic.zone'), 'wb') as fd:
				fd.write(tpl.render(**param))

		if is_root:
			for alias in ds.domain.aliases:
				self.generate_zone(param, ds, str(alias), outdir, tpl, split_dns)

	def generate_revzone(self, param, rz, outdir, tpl, split_dns=False):
		from netprofile_ipaddresses.models import IPv4ReverseZoneSerial
		param['rz'] = rz
		if isinstance(rz, IPv4ReverseZoneSerial):
			param['rztype'] = 4
			net = rz.ipv4_network
		else:
			param['rztype'] = 6
			net = rz.ipv6_network

		if split_dns:
			param['zonetype'] = 'internal'
			with open(os.path.join(outdir, rz.zone_filename + '.internal.zone'), 'wb') as fd:
				fd.write(tpl.render(**param))
			if (not net.is_private) and (not net.is_link_local) and (not net.is_loopback) and (not net.is_reserved):
				param['zonetype'] = 'external'
				with open(os.path.join(outdir, rz.zone_filename + '.external.zone'), 'wb') as fd:
					fd.write(tpl.render(**param))
		else:
			param['zonetype'] = 'generic'
			with open(os.path.join(outdir, rz.zone_filename + '.generic.zone'), 'wb') as fd:
				fd.write(tpl.render(**param))

	def generate(self, srv):
		self.confgen.mm.assert_loaded('ipaddresses')
		deptpl = self.confgen.deptpl()
		files_dir = self.confgen.srvdir_files(srv)
		tpl_dir = self.confgen.srvdir_templates(srv)

		param = {
			'now'     : datetime.datetime.now().replace(microsecond=0),
			'gen'     : self,
			'srv'     : srv,
			'deptype' : self.confgen.cfg.get('netprofile.confgen.deployment_type', 'puppet'),
			'dtpl'    : deptpl
		}
		conf_tpl = self.confgen.mako_lookup.get_template('netprofile_confgen:templates/confgen/named.conf.mak')
		zone_tpl = self.confgen.mako_lookup.get_template('netprofile_confgen:templates/confgen/named.zone.mak')

		with open(os.path.join(tpl_dir, 'named.conf' + deptpl.file_suffix), 'wb') as fd:
			fd.write(conf_tpl.render(**param))

		pridir = self.confgen.srvdir_files(srv, 'pri')
		splitdns = srv.get_bool_param('split_dns', False)
		for ds in srv.host.domain_services:
			if ds.type_id != 1:
				continue
			self.generate_zone(param, ds, str(ds.domain), pridir, zone_tpl, splitdns, True)

		if srv.get_bool_param('gen_revzones', True):
			param = {
				'now' : datetime.datetime.now().replace(microsecond=0),
				'gen' : self,
				'srv' : srv
			}
			revdir = self.confgen.srvdir_files(srv, 'rev')
			rev_tpl = self.confgen.mako_lookup.get_template('netprofile_confgen:templates/confgen/named.revzone.mak')

			for rz in self.all_ipv4_revzones:
				self.generate_revzone(param, rz, revdir, rev_tpl, splitdns)
			for rz in self.all_ipv6_revzones:
				self.generate_revzone(param, rz, revdir, rev_tpl, splitdns)

class ISCDHCPGenerator(ConfigGenerator):
	@reify
	def all_nets(self):
		from netprofile_networks.models import Network
		return DBSession().query(Network).all()

	@reify
	def all_netgroups(self):
		from netprofile_networks.models import NetworkGroup
		return DBSession().query(NetworkGroup).all()

	def host_iplist(self, host, ipv=4):
		if isinstance(host, collections.Iterable):
			return ','.join(self.host_iplist(h, ipv) for h in host)
		if host.original:
			return self.host_iplist(host.original)
		if ipv == 4:
			ips = host.ipv4_addresses
		else:
			ips = host.ipv6_addresses
		return ','.join(str(ip) for ip in ips)

	@property
	def all_hosts_ipv4(self):
		from netprofile_hosts.models import Host
		return DBSession().query(Host).options(joinedload(Host.ipv4_addresses))

	def generate(self, srv):
		self.confgen.mm.assert_loaded('ipaddresses')
		srvdir = self.confgen.srvdir_files(srv)

		dhcpv6 = srv.get_bool_param('dhcpv6', False)
		param = {
			'now'    : datetime.datetime.now().replace(microsecond=0),
			'gen'    : self,
			'srv'    : srv,
			'dhcpv6' : dhcpv6
		}
		if dhcpv6:
			conf_tpl = self.confgen.mako_lookup.get_template('netprofile_confgen:templates/confgen/dhcpd.ipv6.conf.mak')
		else:
			conf_tpl = self.confgen.mako_lookup.get_template('netprofile_confgen:templates/confgen/dhcpd.ipv4.conf.mak')

		with open(os.path.join(srvdir, 'dhcpd.conf'), 'wb') as fd:
			fd.write(conf_tpl.render(**param))

