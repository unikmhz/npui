#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Config Generation module - Models
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

__all__ = [
	'Server',
	'ServerParameter',
	'ServerType'
]

from sqlalchemy import (
	Column,
	ForeignKey,
	Index,
	PickleType,
	Sequence,
	Unicode,
	UnicodeText,
	text
)
from sqlalchemy.orm import (
	backref,
	relationship
)
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

from netprofile.db.connection import (
	Base,
	DBSession
)
from netprofile.db.fields import (
	ASCIIString,
	UInt32
)
from netprofile.tpl import TemplateObject
from netprofile.ext.wizards import SimpleWizard
from netprofile.db.ddl import Comment
from netprofile.ext.columns import MarkupColumn

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
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('srvtypeid', 'name'),
				'grid_hidden'   : ('srvtypeid',),
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
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	generator_name = Column(
		'gen',
		ASCIIString(64),
		Comment('Registered generator class name'),
		nullable=False,
		info={
			'header_string' : _('Class')
		}
	)
	parameter_defaults = Column(
		'paramdef',
		PickleType(),
		Comment('Dictionary of parameter defaults'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Defaults')
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
				'grid_view'     : ('srvid', 'host', 'type'),
				'grid_hidden'   : ('srvid',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new server')),

				'extra_actions' : [{
					'iconCls' : 'ico-redo',
					'tooltip' : _('Generate server configuration'),
					'itemId'  : 'srvgen'
				}]
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
	parameters = relationship(
		'ServerParameter',
		collection_class=attribute_mapped_collection('name'),
		backref=backref('server', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def __str__(self):
		return '%s: %s' % (
			str(self.type),
			str(self.host)
		)

	def get_param(self, name, default=None):
		# TODO: Maybe fix to be more DB-friendly?
		if name in self.parameters:
			return self.parameters[name].value
		srvt = self.type
		try:
			if name in srvt.parameter_defaults:
				return srvt.parameter_defaults[name]
		except (TypeError, IndexError):
			pass
		return default

	def get_bool_param(self, name, default=False):
		ret = self.get_param(name, default)
		if isinstance(ret, bool):
			return ret
		if not isinstance(ret, str):
			raise ValueError('Invalid parameter type')
		ret = ret.lower()
		if ret in ('t', 'true', 'y', 'yes', 'on', '1', 'enabled'):
			return True
		if ret in ('f', 'false', 'n', 'no', 'off', '0', 'disabled'):
			return False
		return default

	def has_param(self, name):
		ret = self.get_param(name)
		return ret not in (None, False, '')

class ServerParameter(Base):
	"""
	Parameter of a server instance object.
	"""
	__tablename__ = 'srv_params'
	__table_args__ = (
		Comment('Server parameters'),
		Index('srv_params_u_param', 'srvid', 'name', unique=True),
		Index('srv_params_i_name', 'name'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'SRV_LIST',
				'cap_create'    : 'SRV_EDIT',
				'cap_edit'      : 'SRV_EDIT',
				'cap_delete'    : 'SRV_EDIT',

				'menu_name'     : _('Server Parameters'),
				'grid_view'     : ('srvparamid', 'server', 'name', 'value'),
				'grid_hidden'   : ('srvparamid',),

				'create_wizard' : SimpleWizard(title=_('Add new parameter'))
			}
		}
	)
	id = Column(
		'srvparamid',
		UInt32(),
		Sequence('srv_params_srvparamid_seq'),
		Comment('Server parameter ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	server_id = Column(
		'srvid',
		UInt32(),
		ForeignKey('srv_def.srvid', name='srv_params_fk_srvid', onupdate='CASCADE', ondelete='CASCADE'),
		Comment('Server ID'),
		nullable=False,
		info={
			'header_string' : _('Server'),
			'column_flex'   : 1,
			'filter_type'   : 'none'
		}
	)
	name = Column(
		ASCIIString(64),
		Comment('Server parameter name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	value = Column(
		Unicode(255),
		Comment('Server parameter value'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Value'),
			'column_flex'   : 1
		}
	)

	def __str__(self):
		return '%s: %s' % (
			str(self.server),
			str(self.name)
		)

