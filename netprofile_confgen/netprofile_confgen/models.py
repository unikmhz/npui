#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Config Generation module - Models
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
	'Server',
	'ServerType'
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
from netprofile.db.fields import UInt32
from netprofile.ext.wizards import SimpleWizard
from netprofile.db.ddl import Comment

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile_confgen')

class ServerType(Base):
	"""
	Server type definition.
	"""
	__tablename__ = 'srv_types'
	__table_args__ = (
		Comment('Server types'),
		Index('srv_types_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'SRV_LIST',
				'cap_create'    : 'SRVTYPES_CREATE',
				'cap_edit'      : 'SRVTYPES_EDIT',
				'cap_delete'    : 'SRVTYPES_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Server Types'),
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('name',),
				'form_view'     : ('name', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new server type'))
			}
		}
	)
	id = Column(
		'srvtypeid',
		UInt32(),
		Sequence('srv_types_srvtypeid_seq', start=101, increment=1),
		Comment('Server type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Server type name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Server type description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	servers = relationship(
		'Server',
		backref=backref('type', innerjoin=True)
	)

	hosts = association_proxy(
		'servers',
		'host',
		creator=lambda v: Server(host=v)
	)

	def __str__(self):
		return '%s' % str(self.name)

class Server(Base):
	"""
	Server instance object.
	"""
	__tablename__ = 'srv_def'
	__table_args__ = (
		Comment('Servers'),
		Index('srv_def_u_srv', 'hostid', 'srvtypeid', unique=True),
		Index('srv_def_i_srvtypeid', 'srvtypeid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'SRV_LIST',
				'cap_create'    : 'SRV_CREATE',
				'cap_edit'      : 'SRV_EDIT',
				'cap_delete'    : 'SRV_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Servers'),
				'menu_order'    : 20,
				'grid_view'     : ('host', 'type'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new server'))
			}
		}
	)
	id = Column(
		'srvid',
		UInt32(),
		Sequence('srv_def_srvid_seq'),
		Comment('Server ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	host_id = Column(
		'hostid',
		UInt32(),
		ForeignKey('hosts_def.hostid', name='srv_def_fk_hostid', onupdate='CASCADE'),
		Comment('Host ID'),
		nullable=False,
		info={
			'header_string' : _('Host'),
			'column_flex'   : 1,
			'filter_type'   : 'none'
		}
	)
	type_id = Column(
		'srvtypeid',
		UInt32(),
		ForeignKey('srv_types.srvtypeid', name='srv_def_fk_srvtypeid', onupdate='CASCADE'),
		Comment('Server type ID'),
		nullable=False,
		info={
			'header_string' : _('Type'),
			'column_flex'   : 1,
			'filter_type'   : 'list'
		}
	)

	host = relationship(
		'Host',
		innerjoin=True,
		backref='servers'
	)

	def __str__(self):
		return '%s: %s' % (
			str(self.type),
			str(self.host)
		)

