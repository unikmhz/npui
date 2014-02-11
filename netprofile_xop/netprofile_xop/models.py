#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: XOP module - Models
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
	'ExternalOperation',
	'ExternalOperationProvider'
]

from sqlalchemy import (
	Column,
	FetchedValue,
	ForeignKey,
	Index,
	Numeric,
	Sequence,
	TIMESTAMP,
	Unicode,
	UnicodeText,
	func,
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
	DeclEnum,
	NPBoolean,
	UInt8,
	UInt16,
	UInt32,
	UInt64,
	npbool
)
from netprofile.db.ddl import Comment
from netprofile.ext.columns import MarkupColumn
from netprofile.ext.wizards import SimpleWizard
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

#from netprofile_entities.models import Entity
#from netprofile_stashes.models import Stash


_ = TranslationStringFactory('netprofile_xop')

class ExternalOperationState(DeclEnum):
	"""
	Enumeration of xop state codes
	"""
	new			= 'NEW',	_('New'),		10
	checked		= 'CHK',	_('Checked'),	20
	pending		= 'PND',	_('Pending'),	30
	confirmed	= 'CNF',	_('Confirmed'), 40
	cleared		= 'CLR',	_('Cleared'),	50
	canceled	= 'CNC',	_('Canceled'),	60

class ExternalOperationProviderAuthMethod(DeclEnum):
	"""
	Enumeration of xop provider auth methods
	"""
	http		= 'http',		_('HTTP'),			10
	md5			= 'req-md5',	_('Request MD5'),	20
	sha1		= 'req-sha1',	_('Request SHA1'),	30

class ExternalOperation(Base):
	"""
	External operation object.
	"""

	__tablename__ = 'xop_def'
	__table_args__ = (
		Comment('External operations'),
		Index('xop_def_i_extid', 'extid'),
		Index('xop_def_i_xoppid', 'xoppid'),
		Index('xop_def_i_ts', 'ts'),
		Index('xop_def_i_entityid', 'entityid'),
		Index('xop_def_i_stashid', 'stashid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_XOP',
				'cap_read'     : 'STASHES_IO',
				'cap_create'   : 'STASHES_IOTYPES_CREATE',
				'cap_edit'     : '__NOPRIV__',
				'cap_delete'   : '__NOPRIV__',

				'menu_name'    : _('External Operations'),
				'menu_main'	   : True,
				'show_in_menu' : 'modules',
				'menu_order'   : 50,
				'default_sort' : ({ 'property': 'ts' ,'direction': 'DESC' },),
				'grid_view'    : ( 'provider', 'ts', 'entity', 'diff', 'state'),
				'form_view'    : (
					'provider', 'ts', 'entity', 'diff', 'state',
					'stash', 'extid', 'eacct', 'stash'
				),
				'easy_search'  : ('extid', 'eacct'),
				'detail_pane'  : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'xopid',
		UInt32(),
		Sequence('xop_def_xopid_seq'),
		Comment('External Operation ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	external_id = Column(
		'extid',
		ASCIIString(255),
		Comment('Remote Provider Operation ID'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('External ID'),
		}
	)
	external_account = Column(
		'eacct',
		Unicode(255),
		Comment('External Account Name'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('External account'),
		}
	)
	provider_id = Column(
		'xoppid',
		UInt32(),
		ForeignKey('xop_providers.xoppid', name='xop_def_fk_xoppid', onupdate='CASCADE'),
		Comment('External Operation Provider ID'),
		nullable=False,
		info={
			'header_string' : _('Provider'),
			'column_flex'   : 3
		}
	)
	timestamp = Column(
		'ts',
		TIMESTAMP(),
		Comment('Timestamp of Operation'),
		nullable=False,
		default=None,
		server_default=func.current_timestamp(),
		info={
			'header_string' : _('Ends')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='xop_def_fk_entityid', onupdate='CASCADE', ondelete="SET NULL"),
		Comment('Used entity ID'),
		nullable=False,
		info={
			'header_string' : _('Entity'),
			'column_flex'   : 3
		}
	)
	stash_id = Column(
		'stashid',
		UInt32(),
		ForeignKey('stashes_def.stashid', name='xop_def_fk_stashid', onupdate='CASCADE', ondelete="SET NULL"),
		Comment('Used stash ID'),
		nullable=False,
		info={
			'header_string' : _('Stash'),
			'column_flex'   : 3
		}
	)
	difference = Column(
		'diff',
		Numeric(20, 8),
		Comment('Stash Amount Changes'),
		nullable=False,
		default=0,
		server_default=text('0.00000000'),
		info={
			'header_string' : _('Amount')
		}
	)
	state = Column(
		ExternalOperationState.db_type(),
		Comment('Operation State'),
		nullable=False,
		default=ExternalOperationState.new,
		server_default=ExternalOperationState.new,
		info={
			'header_string': _('State')
		}
	)
	provider = relationship(
		'ExternalOperationProvider',
		innerjoin=True,
		backref='external_operations'
	)
	entity = relationship(
		'Entity',
		innerjoin=True,
		backref='external_operations'
	)
	stash = relationship(
		'Stash',
		innerjoin=True,
		backref='external_operations'
	)

class ExternalOperationProvider(Base):
	"""
	External Operation Providers object
	"""
	__tablename__ = 'xop_providers'
	__table_args__ = (
		Comment('External operation providers'),
		Index('xop_providers_u_name', 'name', unique=True),
		Index('xop_providers_u_uri', 'uri', unique=True),
		Index('xop_providers_u_sname', 'sname', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'     : 'BASE_XOP',
				'cap_read'     : 'STASHES_IO',
				'cap_create'   : 'STASHES_IOTYPES_CREATE',
				'cap_edit'     : 'STASHES_IOTYPES_EDIT',
				'cap_delete'   : 'STASHES_IOTYPES_DELETE',
				'menu_name'     : _('XOP Providers'),
				'show_in_menu' : 'admin',
				'menu_order'   : 50,
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('name', 'sname', 'gwclass', 'enabled'),
				'form_view'    : (
					'uri', 'name', 'sname', 'gwclass', 'enabled',
					'accesslist', 'siotype', 'mindiff', 'maxdiff', 'authmethod',
					'authopts', 'authuser', 'authpass', 'description'
				),
				'create_wizard' : SimpleWizard(title=_('Add new XOP Provider'))
			}
		}
	)
	id = Column(
		'xoppid',
		UInt32(),
		Sequence('xop_providers_xoppid_seq'),
		Comment('External Operation Provider ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	uri = Column(
		'uri',
		ASCIIString(64),
		Comment('URI used in XOP interface'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('URI'),
		}
	)
	name = Column(
		'name',
		Unicode(255),
		Comment('External Account Name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
		}
	)
	sname = Column(
		'sname',
		Unicode(32),
		Comment('External Account Short Name'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Short name'),
		}
	)
	enabled = Column(
		NPBoolean(),
		Comment('Is modifier enabled?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Enabled')
		}
	)
	accesslist = Column(
		'accesslist',
		ASCIIString(255),
		Comment('Allowed Access Rules'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Access List'),
		}
	)
	gwclass = Column(
		'gwclass',
		ASCIIString(255),
		Comment('Provider Gateway Class Name'),
		nullable=False,
		info={
			'header_string' : _('GW Class'),
		}
	)
	siotype_id = Column(
		'siotypeid',
		UInt32(),
		Comment('Stash I/O type generated in Transaction'),
		ForeignKey('stashes_io_types.siotypeid', name='xop_providers_fk_soitypeid', onupdate='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Type'),
			'filter_type'   : 'list'
		}
	)
	mindiff = Column(
		'mindiff',
		Numeric(20, 8),
		Comment('Minimum Operation Result'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Minimum amount')
		}
	)
	maxdiff = Column(
		'maxdiff',
		Numeric(20, 8),
		Comment('Maxmum Operation Result'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Maximum amount')
		}
	)
	authmethod = Column(
		'authmethod',
		ExternalOperationProviderAuthMethod.db_type(),
		Comment('Authentication Method'),
		nullable=True,
		default=None,
		info={
			'header_string': _('Auth type')
		}
	)
	authopts = Column(
		'authopts',
		Unicode(255),
		Comment('Authentication Options'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Auth options'),
		}
	)
	authuser = Column(
		'authuser',
		Unicode(255),
		Comment('Authentication User'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Auth user'),
		}
	)
	authpass= Column(
		'authpass',
		Unicode(255),
		Comment('Authentication Password'),
		nullable=True,
		default=None,
		info={
			'header_string' : _('Auth password'),
		}
	)
	siotype = relationship(
		'StashIOType',
		innerjoin=True,
		backref='xop_providers'
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Link type description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	def __str__(self):
		return '%s' % self.name

