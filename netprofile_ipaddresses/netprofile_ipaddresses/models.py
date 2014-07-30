#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: IP addresses module - Models
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

__all__ = [
	'IPv4Address',
	'IPv6Address',

	'IPAddrGetDotStrFunction',
	'IPAddrGetOffsetGenFunction',
	'IPAddrGetOffsetHGFunction',
	'IP6AddrGetOffsetGenFunction',
	'IP6AddrGetOffsetHGFunction'
]

from sqlalchemy import (
	Column,
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

from netprofile.db.connection import Base
from netprofile.db import fields
from netprofile.db.fields import (
	DeclEnum,
	IPv6Offset,
	MACAddress,
	NPBoolean,
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
				'menu_order'    : 10,
				'grid_view'     : (
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
				'menu_order'    : 20,
				'grid_view'     : (
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

	def __str__(self):
		if self.network and self.network.ipv6_address:
			return str(self.network.ipv6_address + self.offset)

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

