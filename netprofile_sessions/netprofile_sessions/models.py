#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Sessions module - Models
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

__all__ = [
	'AccessSession',
	'AccessSessionHistory'
]

from sqlalchemy import (
	Column,
	ForeignKey,
	Index,
	Numeric,
	Sequence,
	TIMESTAMP,
	text
)

from sqlalchemy.orm import (
	backref,
	relationship
)

from sqlalchemy.ext.associationproxy import association_proxy

from netprofile.db.connection import (
	Base,
	DBSession
)
from netprofile.db.fields import (
	ASCIIString,
	UInt8,
	UInt32,
	UInt64
)
from netprofile.db.ddl import Comment

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_sessions')

class AccessSession(Base):
	"""
	Session definition
	"""
	__tablename__ = 'sessions_def'
	__table_args__ = (
		Comment('Access sessions'),
		Index('sessions_def_u_session', 'stationid', 'name', unique=True),
		Index('sessions_def_i_entityid', 'entityid'),
		Index('sessions_def_i_updatets', 'updatets'),
		Index('sessions_def_i_destid', 'destid'),
		Index('sessions_def_i_ipaddrid', 'ipaddrid'),
		Index('sessions_def_i_ip6addrid', 'ip6addrid'),
		Index('sessions_def_i_nasid', 'nasid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_SESSIONS',
				'cap_read'      : 'SESSIONS_LIST',
				'cap_create'    : '__NOPRIV__',
				'cap_edit'      : '__NOPRIV__',
				'cap_delete'    : 'SESSIONS_DISCONNECT',
				'menu_name'     : _('Sessions'),
				'show_in_menu'  : 'modules',
				'menu_main'     : True,
				'menu_order'    : 40,
				'default_sort'  : ({ 'property': 'updatets', 'direction': 'DESC' },),
				'grid_view'     : (
					'nas', 'name',
					'entity', 'csid',
					'ut_ingress', 'ut_egress',
					'startts', 'updatets'
				),
				'form_view'     : (
					'stationid', 'nas', 'called', 'name',
					'entity', 'csid',
					'ipv4_address', 'ipv6_address',
					'ut_ingress', 'ut_egress',
					'destination',
					'startts', 'updatets',
					'pol_ingress', 'pol_egress'
				),
				'easy_search'   : ('name', 'csid'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'sessid',
		UInt64(),
		Sequence('sessions_def_sessid_seq'),
		Comment('Session ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		ASCIIString(255),
		Comment('Session name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	station_id = Column(
		'stationid',
		UInt32(),
		Comment('Station ID'),
		nullable=False,
		default=1,
		server_default=text('1'),
		info={
			'header_string' : _('Station')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		Comment('Access entity ID'),
		ForeignKey('entities_access.entityid', name='sessions_def_fk_entityid', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Entity'),
			'filter_type'   : 'none',
			'column_flex'   : 1
		}
	)
	ipv4_address_id = Column(
		'ipaddrid',
		UInt32(),
		Comment('IPv4 address ID'),
		ForeignKey('ipaddr_def.ipaddrid', name='sessions_def_fk_ipaddrid', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv4 Address'),
			'filter_type'   : 'none'
		}
	)
	ipv6_address_id = Column(
		'ip6addrid',
		UInt64(),
		Comment('IPv6 address ID'),
		ForeignKey('ip6addr_def.ip6addrid', name='sessions_def_fk_ip6addrid', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv6 Address'),
			'filter_type'   : 'none'
		}
	)
	destination_id = Column(
		'destid',
		UInt32(),
		Comment('Accounting destination ID'),
		ForeignKey('dest_def.destid', name='sessions_def_fk_destid', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Destination'),
			'filter_type'   : 'none'
		}
	)
	nas_id = Column(
		'nasid',
		UInt32(),
		Comment('Network access server ID'),
		ForeignKey('nas_def.nasid', name='sessions_def_fk_nasid', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('NAS'),
			'filter_type'   : 'list'
		}
	)
	calling_station_id = Column(
		'csid',
		ASCIIString(255),
		Comment('Calling station ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Calling Station')
		}
	)
	called_station_id = Column(
		'called',
		ASCIIString(255),
		Comment('Called station ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Called Station')
		}
	)
	start_timestamp = Column(
		'startts',
		TIMESTAMP(),
		Comment('Session start time'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Started')
		}
	)
	update_timestamp = Column(
		'updatets',
		TIMESTAMP(),
		Comment('Accounting update time'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Updated')
		}
	)
	used_ingress_traffic = Column(
		'ut_ingress',
		Numeric(16, 0),
		Comment('Used ingress traffic'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Used Ingress')
		}
	)
	used_egress_traffic = Column(
		'ut_egress',
		Numeric(16, 0),
		Comment('Used egress traffic'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Used Egress')
		}
	)
	ingress_policy = Column(
		'pol_ingress',
		ASCIIString(255),
		Comment('Ingress traffic policy'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Ingress Policy')
		}
	)
	egress_policy = Column(
		'pol_egress',
		ASCIIString(255),
		Comment('Egress traffic policy'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Egress Policy')
		}
	)

	entity = relationship(
		'AccessEntity',
		backref='sessions'
	)
	ipv4_address = relationship(
		'IPv4Address',
		backref='sessions'
	)
	ipv6_address = relationship(
		'IPv6Address',
		backref='sessions'
	)
	destination = relationship(
		'Destination',
		backref='sessions'
	)
	nas = relationship(
		'NAS',
		backref='sessions'
	)

	def __str__(self):
		return '%s' % str(self.name)

class AccessSessionHistory(Base):
	"""
	Closed session definition
	"""
	__tablename__ = 'sessions_history'
	__table_args__ = (
		Comment('Log of closed sessions'),
		Index('sessions_history_i_entityid', 'entityid'),
		Index('sessions_history_i_ipaddrid', 'ipaddrid'),
		Index('sessions_history_i_ip6addrid', 'ip6addrid'),
		Index('sessions_history_i_destid', 'destid'),
		Index('sessions_history_i_endts', 'endts'),
		Index('sessions_history_i_nasid', 'nasid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'SESSIONS_LIST_ARCHIVED',
				'cap_read'      : 'SESSIONS_LIST_ARCHIVED',
				'cap_create'    : '__NOPRIV__',
				'cap_edit'      : '__NOPRIV__',
				'cap_delete'    : '__NOPRIV__',
				'menu_name'     : _('History'),
				'show_in_menu'  : 'modules',
				'menu_order'    : 40,
				'default_sort'  : ({ 'property': 'endts', 'direction': 'DESC' },),
				'grid_view'     : (
					'nas', 'name',
					'entity', 'csid',
					'ut_ingress', 'ut_egress',
					'startts', 'endts'
				),
				'form_view'     : (
					'stationid', 'nas', 'called', 'name',
					'entity', 'csid',
					'ipv4_address', 'ipv6_address',
					'ut_ingress', 'ut_egress',
					'destination',
					'startts', 'endts',
					'pol_ingress', 'pol_egress'
				),
				'easy_search'   : ('name', 'csid'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'sessid',
		UInt64(),
		Sequence('sessions_history_sessid_seq'),
		Comment('Session ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		ASCIIString(255),
		Comment('Session name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	station_id = Column(
		'stationid',
		UInt32(),
		Comment('Station ID'),
		nullable=False,
		info={
			'header_string' : _('Station')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		Comment('Access entity ID'),
		ForeignKey('entities_access.entityid', name='sessions_history_fk_entityid', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Entity'),
			'filter_type'   : 'none',
			'column_flex'   : 1
		}
	)
	ipv4_address_id = Column(
		'ipaddrid',
		UInt32(),
		Comment('IPv4 address ID'),
		ForeignKey('ipaddr_def.ipaddrid', name='sessions_history_fk_ipaddrid', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv4 Address'),
			'filter_type'   : 'none'
		}
	)
	ipv6_address_id = Column(
		'ip6addrid',
		UInt64(),
		Comment('IPv6 address ID'),
		ForeignKey('ip6addr_def.ip6addrid', name='sessions_history_fk_ip6addrid', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv6 Address'),
			'filter_type'   : 'none'
		}
	)
	destination_id = Column(
		'destid',
		UInt32(),
		Comment('Accounting destination ID'),
		ForeignKey('dest_def.destid', name='sessions_history_fk_destid', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Destination'),
			'filter_type'   : 'none'
		}
	)
	nas_id = Column(
		'nasid',
		UInt32(),
		Comment('Network access server ID'),
		ForeignKey('nas_def.nasid', name='sessions_history_fk_nasid', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('NAS'),
			'filter_type'   : 'list'
		}
	)
	calling_station_id = Column(
		'csid',
		ASCIIString(255),
		Comment('Calling station ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Calling Station')
		}
	)
	called_station_id = Column(
		'called',
		ASCIIString(255),
		Comment('Called station ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Called Station')
		}
	)
	start_timestamp = Column(
		'startts',
		TIMESTAMP(),
		Comment('Session start time'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Started')
		}
	)
	end_timestamp = Column(
		'endts',
		TIMESTAMP(),
		Comment('Session end time'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Ended')
		}
	)
	used_ingress_traffic = Column(
		'ut_ingress',
		Numeric(16, 0),
		Comment('Used ingress traffic'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Used Ingress')
		}
	)
	used_egress_traffic = Column(
		'ut_egress',
		Numeric(16, 0),
		Comment('Used egress traffic'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Used Egress')
		}
	)
	ingress_policy = Column(
		'pol_ingress',
		ASCIIString(255),
		Comment('Ingress traffic policy'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Ingress Policy')
		}
	)
	egress_policy = Column(
		'pol_egress',
		ASCIIString(255),
		Comment('Egress traffic policy'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Egress Policy')
		}
	)

	entity = relationship(
		'AccessEntity',
		backref='closed_sessions'
	)
	ipv4_address = relationship(
		'IPv4Address',
		backref='closed_sessions'
	)
	ipv6_address = relationship(
		'IPv6Address',
		backref='closed_sessions'
	)
	destination = relationship(
		'Destination',
		backref='closed_sessions'
	)
	nas = relationship(
		'NAS',
		backref='closed_sessions'
	)

	def __str__(self):
		return '%s' % str(self.name)

