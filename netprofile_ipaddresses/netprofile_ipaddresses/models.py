#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: IP addresses module - Models
# © Copyright 2013-2015 Alex 'Unik' Unigovsky
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

__all__ = [
	'IPv4Address',
	'IPv6Address',
	'IPv4ReverseZoneSerial',
	'IPv6ReverseZoneSerial',

	'IPAddrGetDotStrFunction',
	'IPAddrGetOffsetGenFunction',
	'IPAddrGetOffsetHGFunction',
	'IP6AddrGetOffsetGenFunction',
	'IP6AddrGetOffsetHGFunction'
]

from sqlalchemy import (
	Column,
	Date,
	ForeignKey,
	Index,
	Sequence,
	Unicode,
	text
)

from sqlalchemy.orm import (
	backref,
	relationship
)

from sqlalchemy.ext.associationproxy import association_proxy

from netprofile.common import ipaddr
from netprofile.db.connection import Base
from netprofile.db import fields
from netprofile.db.fields import (
	DeclEnum,
	IPv6Offset,
	MACAddress,
	NPBoolean,
	UInt8,
	UInt32,
	UInt64,
	npbool
)

from netprofile.db.ddl import (
	Comment,
	SQLFunction,
	SQLFunctionArgument,
	Trigger
)
from netprofile.ext.columns import MarkupColumn
from netprofile.ext.wizards import (
	SimpleWizard,
	Step,
	Wizard
)

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

from netprofile_domains.models import ObjectVisibility

_ = TranslationStringFactory('netprofile_ipaddresses')

class IPv4Address(Base):
	"""
	IPv4 address object.
	"""
	__tablename__ = 'ipaddr_def'
	__table_args__ = (
		Comment('IPv4 addresses'),
		Index('ipaddr_def_u_address', 'netid', 'offset', unique=True),
		Index('ipaddr_def_i_hostid', 'hostid'),
		Index('ipaddr_def_i_poolid', 'poolid'),
		Index('ipaddr_def_i_inuse', 'inuse'),
		Trigger('before', 'insert', 't_ipaddr_def_bi'),
		Trigger('before', 'update', 't_ipaddr_def_bu'),
		Trigger('after', 'insert', 't_ipaddr_def_ai'),
		Trigger('after', 'update', 't_ipaddr_def_au'),
		Trigger('after', 'delete', 't_ipaddr_def_ad'),
		{
			'mysql_engine'      : 'InnoDB',
			'mysql_charset'     : 'utf8',
			'info'              : {
				'cap_menu'      : 'BASE_IPADDR',
				'cap_read'      : 'IPADDR_LIST',
				'cap_create'    : 'IPADDR_CREATE',
				'cap_edit'      : 'IPADDR_EDIT',
				'cap_delete'    : 'IPADDR_DELETE',
				'menu_name'     : _('IPv4 Addresses'),
				'show_in_menu'  : 'modules',
				'grid_view'     : (
					'ipaddrid',
					'host',
					MarkupColumn(
						name='offset',
						header_string=_('Address'),
						template='{__str__}',
						column_flex=1,
						sortable=True
					),
					'hwaddr', 'vis', 'owned', 'inuse'
				),
				'grid_hidden'   : ('ipaddrid',),
				'form_view'     : (
					'host', 'network', 'offset',
					'hwaddr', 'ttl', 'pool',
					'vis', 'owned', 'inuse'
				),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new IPv4 address'))
			}
		}
	)
	id = Column(
		'ipaddrid',
		UInt32(),
		Sequence('ipaddr_def_ipaddrid_seq'),
		Comment('IPv4 address ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	host_id = Column(
		'hostid',
		UInt32(),
		ForeignKey('hosts_def.hostid', name='ipaddr_def_fk_hostid', onupdate='CASCADE', ondelete='CASCADE'),
		Comment('Host ID'),
		nullable=False,
		info={
			'header_string' : _('Host'),
			'filter_type'   : 'none',
			'column_flex'   : 1
		}
	)
	pool_id = Column(
		'poolid',
		UInt32(),
		ForeignKey('ippool_def.poolid', name='ipaddr_def_fk_poolid', onupdate='CASCADE', ondelete='SET NULL'),
		Comment('IP address pool ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Pool'),
			'filter_type'   : 'list'
		}
	)
	network_id = Column(
		'netid',
		UInt32(),
		ForeignKey('nets_def.netid', name='ipaddr_def_fk_netid', onupdate='CASCADE', ondelete='CASCADE'),
		Comment('Network ID'),
		nullable=False,
		info={
			'header_string' : _('Network'),
			'filter_type'   : 'list'
		}
	)
	offset = Column(
		UInt32(),
		Comment('Offset from network start'),
		nullable=False,
		info={
			'header_string' : _('Offset')
		}
	)
	hardware_address = Column(
		'hwaddr',
		MACAddress(),
		Comment('Hardware address'),
		nullable=False,
		info={
			'header_string' : _('Hardware Address'),
			'column_flex'   : 1
		}
	)
	ttl = Column(
		UInt32(),
		Comment('RR time to live'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('RR Time To Live')
		}
	)
	visibility = Column(
		'vis',
		ObjectVisibility.db_type(),
		Comment('IPv4 address visibility'),
		nullable=False,
		default=ObjectVisibility.both,
		server_default=ObjectVisibility.both,
		info={
			'header_string' : _('Visibility')
		}
	)
	owned = Column(
		NPBoolean(),
		Comment('Is statically assigned?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Assigned')
		}
	)
	in_use = Column(
		'inuse',
		NPBoolean(),
		Comment('Is this IPv4 address in use?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('In Use')
		}
	)

	host = relationship(
		'Host',
		innerjoin=True,
		lazy='joined',
		backref=backref(
			'ipv4_addresses',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	pool = relationship(
		'IPPool',
		backref='ipv4_addresses'
	)
	network = relationship(
		'Network',
		innerjoin=True,
		backref=backref(
			'ipv4_addresses',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)

	@property
	def address(self):
		if self.network and self.network.ipv4_address:
			return self.network.ipv4_address + self.offset

	@property
	def ptr_name(self):
		addr = self.address
		if addr:
			return int(addr) % 256

	def __str__(self):
		if self.network and self.network.ipv4_address:
			return str(self.network.ipv4_address + self.offset)

class IPv6Address(Base):
	"""
	IPv6 address object.
	"""
	__tablename__ = 'ip6addr_def'
	__table_args__ = (
		Comment('IPv6 addresses'),
		Index('ip6addr_def_u_address', 'netid', 'offset', unique=True),
		Index('ip6addr_def_i_hostid', 'hostid'),
		Index('ip6addr_def_i_poolid', 'poolid'),
		Index('ip6addr_def_i_inuse', 'inuse'),
		Trigger('before', 'insert', 't_ip6addr_def_bi'),
		Trigger('before', 'update', 't_ip6addr_def_bu'),
		Trigger('after', 'insert', 't_ip6addr_def_ai'),
		Trigger('after', 'update', 't_ip6addr_def_au'),
		Trigger('after', 'delete', 't_ip6addr_def_ad'),
		{
			'mysql_engine'      : 'InnoDB',
			'mysql_charset'     : 'utf8',
			'info'              : {
				'cap_menu'      : 'BASE_IPADDR',
				'cap_read'      : 'IPADDR_LIST',
				'cap_create'    : 'IPADDR_CREATE',
				'cap_edit'      : 'IPADDR_EDIT',
				'cap_delete'    : 'IPADDR_DELETE',
				'menu_name'     : _('IPv6 Addresses'),
				'show_in_menu'  : 'modules',
				'grid_view'     : (
					'ip6addrid',
					'host',
					MarkupColumn(
						name='offset',
						header_string=_('Address'),
						template='{__str__}',
						column_flex=1,
						sortable=True
					),
					'hwaddr', 'vis', 'owned', 'inuse'
				),
				'grid_hidden'   : ('ip6addrid',),
				'form_view'     : (
					'host', 'network', 'offset',
					'hwaddr', 'ttl', 'pool',
					'vis', 'owned', 'inuse'
				),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new IPv6 address'))
			}
		}
	)
	id = Column(
		'ip6addrid',
		UInt64(),
		Sequence('ip6addr_def_ip6addrid_seq'),
		Comment('IPv6 address ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	host_id = Column(
		'hostid',
		UInt32(),
		ForeignKey('hosts_def.hostid', name='ip6addr_def_fk_hostid', onupdate='CASCADE', ondelete='CASCADE'),
		Comment('Host ID'),
		nullable=False,
		info={
			'header_string' : _('Host'),
			'filter_type'   : 'none',
			'column_flex'   : 1
		}
	)
	pool_id = Column(
		'poolid',
		UInt32(),
		ForeignKey('ippool_def.poolid', name='ip6addr_def_fk_poolid', onupdate='CASCADE', ondelete='SET NULL'),
		Comment('IP address pool ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Pool'),
			'filter_type'   : 'list'
		}
	)
	network_id = Column(
		'netid',
		UInt32(),
		ForeignKey('nets_def.netid', name='ip6addr_def_fk_netid', onupdate='CASCADE', ondelete='CASCADE'),
		Comment('Network ID'),
		nullable=False,
		info={
			'header_string' : _('Network'),
			'filter_type'   : 'list'
		}
	)
	offset = Column(
		IPv6Offset(),
		Comment('Offset from network start'),
		nullable=False,
		info={
			'header_string' : _('Offset')
		}
	)
	hardware_address = Column(
		'hwaddr',
		MACAddress(),
		Comment('Hardware address'),
		nullable=False,
		info={
			'header_string' : _('Hardware Address'),
			'column_flex'   : 1
		}
	)
	ttl = Column(
		UInt32(),
		Comment('RR time to live'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('RR Time To Live')
		}
	)
	visibility = Column(
		'vis',
		ObjectVisibility.db_type(),
		Comment('IPv6 address visibility'),
		nullable=False,
		default=ObjectVisibility.both,
		server_default=ObjectVisibility.both,
		info={
			'header_string' : _('Visibility')
		}
	)
	owned = Column(
		NPBoolean(),
		Comment('Is statically assigned?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Assigned')
		}
	)
	in_use = Column(
		'inuse',
		NPBoolean(),
		Comment('Is this IPv6 address in use?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('In Use')
		}
	)

	host = relationship(
		'Host',
		innerjoin=True,
		lazy='joined',
		backref=backref(
			'ipv6_addresses',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	pool = relationship(
		'IPPool',
		backref='ipv6_addresses'
	)
	network = relationship(
		'Network',
		innerjoin=True,
		backref=backref(
			'ipv6_addresses',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)

	@property
	def address(self):
		if self.network and self.network.ipv6_address:
			return self.network.ipv6_address + self.offset

	@property
	def ptr_name(self):
		addr = self.address
		if addr:
			return '%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x' % tuple(
				item
				for b in addr.packed[-1:7:-1]
				for item in (b % 16, (b >> 4) % 16)
			)

	def __str__(self):
		if self.network and self.network.ipv6_address:
			return str(self.network.ipv6_address + self.offset)

class IPv4ReverseZoneSerial(Base):
	"""
	IPv4 reverse zone serial object.
	"""
	__tablename__ = 'revzone_serials'
	__table_args__ = (
		Comment('IPv4 reverse zone DNS serial numbers'),
		Index('revzone_serials_u_ipaddr', 'ipaddr', unique=True),
		{
			'mysql_engine'      : 'InnoDB',
			'mysql_charset'     : 'utf8',
			'info'              : {
				'cap_read'      : 'IPADDR_LIST',
				'cap_create'    : 'IPADDR_EDIT',
				'cap_edit'      : 'IPADDR_EDIT',
				'cap_delete'    : 'IPADDR_EDIT',
				'menu_name'     : _('IPv4 Serials'),
				'grid_view'     : ('ipaddr', 'date', 'rev'),
				'form_view'     : ('ipaddr', 'date', 'rev'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'rsid',
		UInt32(),
		Sequence('revzone_serials_rsid_seq'),
		Comment('IPv4 reverse zone serial ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	ipv4_address = Column(
		'ipaddr',
		fields.IPv4Address(),
		Comment('IPv4 reverse zone address'),
		nullable=False,
		info={
			'header_string' : _('Address')
		}
	)
	date = Column(
		Date(),
		Comment('IPv4 reverse zone serial date'),
		nullable=False,
		info={
			'header_string' : _('Date')
		}
	)
	revision = Column(
		'rev',
		UInt8(),
		Comment('IPv4 reverse zone serial revision'),
		nullable=False,
		default=1,
		server_default=text('1'),
		info={
			'header_string' : _('Revision')
		}
	)

	def __str__(self):
		return '%s%02d' % (
			self.date.strftime('%Y%m%d'),
			(self.revision % 100)
		)

	@property
	def ipv4_network(self):
		return ipaddr.IPv4Network(str(self.ipv4_address) + '/24')

	@property
	def zone_name(self):
		ipint = int(self.ipv4_address)
		return '%d.%d.%d.in-addr.arpa' % (
			(ipint >> 8) % 256,
			(ipint >> 16) % 256,
			(ipint >> 24) % 256
		)

	@property
	def zone_filename(self):
		ipint = int(self.ipv4_address)
		return '%d.%d.%d' % (
			(ipint >> 24) % 256,
			(ipint >> 16) % 256,
			(ipint >> 8) % 256
		)

class IPv6ReverseZoneSerial(Base):
	"""
	IPv6 reverse zone serial object.
	"""
	__tablename__ = 'revzone_serials6'
	__table_args__ = (
		Comment('IPv6 reverse zone DNS serial numbers'),
		Index('revzone_serials6_u_ip6addr', 'ip6addr', unique=True),
		{
			'mysql_engine'      : 'InnoDB',
			'mysql_charset'     : 'utf8',
			'info'              : {
				'cap_read'      : 'IPADDR_LIST',
				'cap_create'    : 'IPADDR_EDIT',
				'cap_edit'      : 'IPADDR_EDIT',
				'cap_delete'    : 'IPADDR_EDIT',
				'menu_name'     : _('IPv6 Serials'),
				'grid_view'     : ('ip6addr', 'date', 'rev'),
				'form_view'     : ('ip6addr', 'date', 'rev'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'rsid',
		UInt32(),
		Sequence('revzone_serials6_rsid_seq'),
		Comment('IPv6 reverse zone serial ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	ipv6_address = Column(
		'ip6addr',
		fields.IPv6Address(),
		Comment('IPv6 reverse zone address'),
		nullable=False,
		info={
			'header_string' : _('Address')
		}
	)
	date = Column(
		Date(),
		Comment('IPv6 reverse zone serial date'),
		nullable=False,
		info={
			'header_string' : _('Date')
		}
	)
	revision = Column(
		'rev',
		UInt8(),
		Comment('IPv6 reverse zone serial revision'),
		nullable=False,
		default=1,
		server_default=text('1'),
		info={
			'header_string' : _('Revision')
		}
	)

	def __str__(self):
		return '%s%02d' % (
			self.date.strftime('%Y%m%d'),
			(self.revision % 100)
		)

	@property
	def ipv6_network(self):
		return ipaddr.IPv6Network(str(self.ipv6_address) + '/64')

	@property
	def zone_name(self):
		return '%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.ip6.arpa' % tuple(
			item
			for b in self.ipv6_address.packed[7::-1]
			for item in (b % 16, (b >> 4) % 16)
		)

	@property
	def zone_filename(self):
		return '%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x.%1x' % tuple(
			item
			for b in self.ipv6_address.packed[:8]
			for item in [(b >> 4) % 16, b % 16]
		)

IPAddrGetDotStrFunction = SQLFunction(
	'ipaddr_get_dotstr',
	args=(
		SQLFunctionArgument('ip', UInt32()),
	),
	returns=Unicode(15),
	comment='Get dotted-decimal format string of IPv4 address ID',
	writes_sql=False
)

IPAddrGetOffsetGenFunction = SQLFunction(
	'ipaddr_get_offset_gen',
	args=(
		SQLFunctionArgument('net', UInt32()),
	),
	returns=UInt32(),
	comment='Get IPv4 offset for a new host (generic version)',
	writes_sql=False
)

IPAddrGetOffsetHGFunction = SQLFunction(
	'ipaddr_get_offset_hg',
	args=(
		SQLFunctionArgument('net', UInt32()),
		SQLFunctionArgument('hg', UInt32())
	),
	returns=UInt32(),
	comment='Get IPv4 offset for a new host (limits version)',
	writes_sql=False
)

IP6AddrGetOffsetGenFunction = SQLFunction(
	'ip6addr_get_offset_gen',
	args=(
		SQLFunctionArgument('net', UInt32()),
	),
	returns=IPv6Offset(),
	comment='Get IPv6 offset for a new host (generic version)',
	writes_sql=False
)

IP6AddrGetOffsetHGFunction = SQLFunction(
	'ip6addr_get_offset_hg',
	args=(
		SQLFunctionArgument('net', UInt32()),
		SQLFunctionArgument('hg', UInt32())
	),
	returns=IPv6Offset(),
	comment='Get IPv6 offset for a new host (limits version)',
	writes_sql=False
)

