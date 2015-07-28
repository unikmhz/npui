#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Dial-Up module - Models
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
	'IPPool',
	'NAS',
	'NASPool'
]

from sqlalchemy import (
	Column,
	ForeignKey,
	Index,
	Sequence,
	Unicode,
	UnicodeText,
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
	IPv6Address,
	UInt32,
	UInt8
)
from netprofile.db.ddl import Comment

from netprofile.ext.wizards import SimpleWizard

from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('netprofile_dialup')


class NAS(Base):
	"""
	NetProfile Network Access Server definition
	"""
	__tablename__ = 'nas_def'
	__table_args__ = (
		Comment('Network access servers'),
		Index('nas_def_i_idstr', 'idstr'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'NAS_LIST',
				'cap_create'    : 'NAS_CREATE',
				'cap_edit'      : 'NAS_EDIT',
				'cap_delete'    : 'NAS_DELETE',
				'menu_name'     : _('Network Access Servers'),
				'show_in_menu'  : 'admin',
				'default_sort'  : ({ 'property': 'idstr', 'direction': 'ASC' },),
				'grid_view'     : ('nasid', 'idstr'),
				'grid_hidden'   : ('nasid',),
				'form_view'     : ('idstr', 'descr'),
				'easy_search'   : ('idstr',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new NAS'))
			}
		}
	)

	id = Column(
		'nasid',
		UInt32(),
		Sequence('nas_def_nasid_seq'),
		Comment('Network access server ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	id_string = Column(
		'idstr',
		ASCIIString(255),
		Comment('Network access server identification string'),
		nullable=False,
		info={
			'header_string' : _('ID String'),
			'column_flex'   : 1
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Network access server description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	poolmap = relationship(
		'NASPool',
		backref=backref('nas', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	pools = association_proxy(
		'poolmap',
		'pool',
		creator=lambda v: NASPool(pool=v)
	)

	def __str__(self):
		return '%s' % str(self.id_string)


class IPPool(Base):
	"""
	IP Address Pools
	"""

	__tablename__ = 'ippool_def'
	__table_args__ = (
		Comment('IP address pools'),
		Index('ippool_def_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'IPPOOLS_LIST',
				'cap_create'    : 'IPPOOLS_CREATE',
				'cap_edit'      : 'IPPOOLS_EDIT',
				'cap_delete'    : 'IPPOOLS_DELETE',
				'menu_name'     : _('IP Address Pools'),
				'show_in_menu'  : 'admin',
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('poolid', 'name'),
				'grid_hidden'   : ('poolid',),
				'form_view'     : ('name', 'ip6prefix', 'ip6plen', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new IP address pool'))
			}
		}
	)

	id = Column(
		'poolid',
		UInt32(),
		Sequence('ippool_def_poolid_seq'),
		Comment('IP address pool ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		'name',
		Unicode(255),
		Comment('IP address pool name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	ipv6_prefix = Column(
		'ip6prefix',
		IPv6Address(),
		Comment('IPv6 prefix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('IPv6 Prefix')
		}
	)
	ipv6_prefix_length = Column(
		'ip6plen',
		UInt8(),
		Comment('IPv6 prefix length'),
		nullable=False,
		info={
			'header_string' : _('IPv6 Prefix Len.')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('IP address pool description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	nasmap = relationship(
		'NASPool',
		backref=backref('pool', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	nases = association_proxy(
		'nasmap',
		'nas',
		creator=lambda v: NASPool(nas=v)
	)

	def __str__(self):
		return '%s' % str(self.name)

class NASPool(Base):
	"""
	NAS IP Pools
	"""

	__tablename__ = 'nas_pools'
	__table_args__ = (
		Comment('NAS IP pools'),
		Index('nas_pools_u_linkage', 'nasid', 'poolid', unique=True),
		Index('nas_pools_i_poolid', 'poolid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'NAS_EDIT',
				'cap_create'    : 'NAS_EDIT',
				'cap_edit'      : 'NAS_EDIT',
				'cap_delete'    : 'NAS_EDIT',
				'menu_name'     : _('NAS IP Pools'),
				'default_sort'  : ({ 'property': 'nasid', 'direction': 'ASC' },),
				'grid_view'     : ('npid', 'nas', 'pool'),
				'grid_hidden'   : ('npid',),
				'form_view'     : ('nas', 'pool'),
				'create_wizard' : SimpleWizard(title=_('Add new NAS IP pool'))
			}
		}
	)

	id = Column(
		'npid',
		UInt32(),
		Sequence('nas_pools_npid_seq'),
		Comment('NAS IP pool ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	nas_id = Column(
		'nasid',
		UInt32(),
		ForeignKey('nas_def.nasid', name='nas_pools_fk_nasid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Network access server ID'),
		nullable=False,
		info={
			'header_string' : _('NAS'),
			'column_flex'   : 1
		}
	)
	pool_id = Column(
		'poolid',
		UInt32(),
		ForeignKey('ippool_def.poolid', name='nas_pools_fk_poolid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('IP address pool ID'),
		nullable=False,
		info={
			'header_string' : _('Pool'),
			'column_flex'   : 1
		}
	)

