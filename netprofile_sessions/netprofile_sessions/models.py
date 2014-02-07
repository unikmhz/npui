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
	Unicode,
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
	UInt8,
	UInt32,
	UInt64
)
from netprofile.db.ddl import Comment

from netprofile.ext.wizards import SimpleWizard

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
				#'cap_create'    : 'SESSIONS_EDIT',
				#'cap_edit'      : 'SESSIONS_EDIT',
				#'cap_delete'    : 'SESSIONS_EDIT',
				'menu_name'     : _('Sessions'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 4,
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('name', 'entity', 'ipaddr', 'destination', 'startts'),
				'form_view'     : (
					'name',
					#'stationid',
					#'entity',
					#'ipaddr',
					#'ip6addr',
					#'destination',
					#'csid',
					#'called',
					#'startts',
					#'updatets',
					#'ut_ingress',
					#'ut_egress'
				),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new session'))
			}
		}
	)
	sessid = Column(
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
		'name',
		Unicode(255),
		Comment('Session name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
		}
	)
	stationid = Column(
		'stationid',
		UInt8(),
		Comment('Station ID'),
		nullable=False,
		default=1,
		info={
			'header_string' : _('Station')
		}
	)
	entityid = Column(
		'entityid',
		UInt8(),
		Comment('Access Entity ID'),
		ForeignKey('entities_access.entityid', name='sessions_def_ibfk_1', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Access Entity')
		}
	)
	ipaddrid = Column(
		'ipaddrid',
		UInt8(),
		Comment('IP Address ID'),
		ForeignKey('ipaddr_def.ipaddrid', name='sessions_def_ibfk_2', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IP Address')
		}
	)
	ip6addrid = Column(
		'ip6addrid',
		UInt32(),
		Comment('IPv6 Address ID'),
		ForeignKey('ip6addr_def.ip6addrid', name='sessions_def_ibfk_3', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv6 Address')
		}
	)
	destid = Column(
		'destid',
		UInt8(),
		Comment('Accounting Destination ID'),
		ForeignKey('dest_def.dsid', name='sessions_def_ibfk_4', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Destination')
		}
	)
	calling = Column(
		'csid',
		Unicode(255),
		Comment('Calling Station ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Calling Station')
		}
	)
	called = Column(
		'called',
		Unicode(255),
		Comment('Called Station ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Called Station')
		}
	)
	startts = Column(
		'startts',
		TIMESTAMP(),
		Comment('Session Start Time'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Session Start Time')
		}
	)
	updatets = Column(
		'updatets',
		TIMESTAMP(),
		Comment('Accounting Update Time'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Accounting Update Time')
		}
	)
	ut_ingress = Column(
		'ut_ingress',
		Numeric(16, 0),
		Comment('Used Ingress Traffic'),
		nullable=False,
		default=0,
		info={
			'header_string' : _('Used Ingress Traffic')
		}
	)
	ut_egress = Column(
		'ut_egress',
		Numeric(16, 0),
		Comment('Used Egress Traffic'),
		nullable=False,
		default=0,
		info={
			'header_string' : _('Used Egress Traffic')
		}
	)

	entity = relationship(
		'AccessEntity',
		backref='session',
		innerjoin=True,
		#primaryjoin='Session.entityid==AccessEntity.id'
	)
	ipaddr = relationship(
		'IPv4Address',
		innerjoin=True,
		backref='ipaddr'
	)
	ip6addr = relationship(
		'IPv6Address',
		innerjoin=True,
		backref='ip6addr'
	)
	destination = relationship(
		'Destination',
		innerjoin=True,
		backref='destination'
	)

	def __str__(self):
		return '%s' % str(self.name)

class AccessSessionHistory(Base):
	"""
	Closed sessions log
	"""
	__tablename__ = 'sessions_history'
	__table_args__ = (
		Comment('Log of closed sessions'),
		Index('session_history_i_entityid', 'entityid'),
		Index('session_history_i_ipaddrid', 'ipaddrid'),
		Index('session_history_i_ip6addrid', 'ip6addrid'),
		Index('session_history_i_destid', 'destid'),
		Index('session_history_i_endts', 'endts'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_SESSIONS',
				'cap_read'      : 'SESSIONS_LIST',
				#'cap_create'    : 'SESSIONS_HISTORY_CREATE',
				#'cap_edit'      : 'SESSIONS_HISTORY_EDIT',
				#'cap_delete'    : 'SESSIONS_HISTORY_DELETE',
				'menu_name'    : _('Session History'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 4,
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('name', 'entityid', 'ipaddrid', 'destid', 'startts', 'endts'),
				'form_view'     : (
					'name',
					#'stationid',
					#'entityid',
					#'ipaddrid',
					#'ip6addrid',
					#'destid',
					#'csid',
					#'called',
					#'startts',
					#'endts',
					#'ut_ingress',
					#'ut_egress'
				),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new entry to sessions history'))
			}
		}
	)
	sessid = Column(
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
		'name',
		Unicode(255),
		Comment('Session name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
		}
	)
	stationid = Column(
		'stationid',
		UInt8(),
		Comment('Station ID'),
		nullable=False,
		default=1,
		info={
			'header_string' : _('Station')
		}
	)
	entityid = Column(
		'entityid',
		UInt8(),
		Comment('Access Entity ID'),
		#ForeignKey('entities_access.entityid', name='sessions_def_ibfk_1', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Access Entity')
		}
	)
	ipaddrid = Column(
		'ipaddrid',
		UInt8(),
		Comment('IP Address ID'),
		#ForeignKey('ipaddr_def.ipaddrid', name='sessions_def_ibfk_2', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IP Address')
		}
	)
	ip6addrid = Column(
		'ip6addrid',
		UInt32(),
		Comment('IPv6 Address ID'),
		#ForeignKey('ip6addr_def.ip6addrid', name='sessions_def_ibfk_3', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv6 Address')
		}
	)
	destid = Column(
		'destid',
		UInt8(),
		Comment('Accounting Destination ID'),
		ForeignKey('dest_sets.dsid', name='sessions_history_ibfk_1', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Destination')
		}
	)
	calling = Column(
		'csid',
		Unicode(255),
		Comment('Calling Station ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Calling Station')
		}
	)
	called = Column(
		'called',
		Unicode(255),
		Comment('Called Station ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Called Station')
		}
	)
	startts = Column(
		'startts',
		TIMESTAMP(),
		Comment('Session Start Time'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Session Start Time')
		}
	)
	endts = Column(
		'endts',
		TIMESTAMP(),
		Comment('Session End Time'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Accounting Update Time')
		}
	)
	ut_ingress = Column(
		'ut_ingress',
		Numeric(16, 0),
		Comment('Used Ingress Traffic'),
		nullable=False,
		default=0,
		info={
			'header_string' : _('Used Ingress Traffic')
		}
	)
	ut_egress = Column(
		'ut_egress',
		Numeric(16, 0),
		Comment('Used Egress Traffic'),
		nullable=False,
		default=0,
		info={
			'header_string' : _('Used Egress Traffic')
		}
	)
	#entity = relationship(
	#    'AccessEntity',
	#    innerjoin=True,
	#    backref='entity'
	#)
	#ipaddr = relationship(
	#    'IPv4Address',
	#    innerjoin=True,
	#    backref='ipaddr'
	#)
	#ip6addr = relationship(
	#    'IPv6Address',
	#    innerjoin=True,
	#    backref='ip6addr'
	#)
	#destination = relationship(
	#'Destination',
	#    innerjoin=True,
	#    backref='destination'
	#)
	#[1
	def __str__(self):
		return '%s' % str(self.name)

