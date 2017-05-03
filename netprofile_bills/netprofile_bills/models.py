#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Bills module - Models
# © Copyright 2017 Alex 'Unik' Unigovsky
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
	'Bill',
	'BillType',
	'BillSerial'
]

from sqlalchemy import (
	Column,
	ForeignKey,
	Index,
	Sequence,
	TIMESTAMP,
	Unicode,
	UnicodeText,
	text
)

from sqlalchemy.orm import (
	backref,
	relationship
)

from netprofile.db.connection import (
	Base,
	DBSession
)
from netprofile.db.fields import (
	ASCIIString,
	DeclEnum,
	JSONData,
	NPBoolean,
	UInt32,
	npbool
)
from netprofile.db.ddl import (
	Comment,
	CurrentTimestampDefault,
	Trigger
)
from netprofile.ext.wizards import SimpleWizard

class BillSerial(Base):
	"""
	Bill serial number counter object.
	"""
	__tablename__ = 'bills_serials'
	__table_args__ = (
		Comment('Bill serial counters'),
		Index('bills_serials_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_BILLS',
				'cap_read'      : 'BILLS_LIST',
				'cap_create'    : 'BILLS_TYPES_EDIT',
				'cap_edit'      : 'BILLS_TYPES_EDIT',
				'cap_delete'    : 'BILLS_TYPES_EDIT',

				'menu_name'     : _('Serial Numbers'),
				'show_in_menu'  : 'admin',
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('bsid', 'name', 'value'),
				'grid_hidden'   : ('bsid',),
				'form_view'     : ('name', 'value'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new serial counter'))
			}
		}
	)
	id = Column(
		'bsid',
		UInt32(),
		Sequence('bills_serials_bsid_seq'),
		Comment('Bill serial counter ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Bill serial counter name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 2
		}
	)
	value = Column(
		UInt32(),
		Comment('Bill serial counter value'),
		nullable=False,
		info={
			'header_string' : _('Value'),
			'column_flex'   : 1
		}
	)

	def __str__(self):
		return str(self.name)

class BillType(Base):
	"""
	Bill type object.
	"""
	__tablename__ = 'bills_types'
	__table_args__ = (
		Comment('Bill types'),
		Index('bills_types_u_name', 'name', unique=True),
		Index('bills_types_i_bsid', 'bsid'),
		Index('bills_types_i_cap', 'cap'),
		Index('bills_types_i_issuer', 'issuer'),
		Index('bills_types_i_siotypeid', 'siotypeid'),
		Index('bills_types_i_docid', 'docid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_BILLS',
				'cap_read'      : 'BILLS_LIST',
				'cap_create'    : 'BILLS_TYPES_CREATE',
				'cap_edit'      : 'BILLS_TYPES_EDIT',
				'cap_delete'    : 'BILLS_TYPES_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Bill Types'),
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('btypeid', 'serial', 'name', 'prefix', 'issuer', 'document'),
				'grid_hidden'   : ('btypeid', 'issuer', 'document'),
			}
		}
	)
	id = Column(
		'btypeid',
		UInt32(),
		Sequence('bills_types_btypeid_seq'),
		Comment('Bill type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	serial_id = Column(
		'bsid',
		UInt32(),
		ForeignKey('bills_serials.bsid', name='bills_types_fk_bsid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Bill serial counter ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Serial Counter'),
			'filter_type'   : 'nplist',
			'column_flex'   : 3
		}
	)
	name = Column(
		Unicode(255),
		Comment('Bill type name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)
	prefix = Column(
		Unicode(48),
		Comment('Bill number prefix'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Prefix'),
			'column_flex'   : 1
		}
	)
	privilege_code = Column(
		'cap',
		ASCIIString(48),
		ForeignKey('privileges.code', name='bills_types_fk_cap', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Capability to create bills of this type'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Privilege'),
			'column_flex'   : 1
		}
	)
	issuer = Column(
		UInt32(),
		ForeignKey('entities_def.entityid', name='bills_types_fk_issuer', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Issuer entity ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Issuer'),
			'filter_type'   : 'nplist',
			'column_flex'   : 2
		}
	)
	io_type_id = Column(
		'siotypeid',
		UInt32(),
		ForeignKey('stashes_io_types.siotypeid', name='bills_types_fk_siotypeid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Stash I/O type generated when paid'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Type'),
			'filter_type'   : 'nplist',
			'editor_xtype'  : 'simplemodelselect',
			'column_flex'   : 2
		}
	)
	document_id = Column(
		'docid',
		UInt32(),
		ForeignKey('docs_def.docid', name='bills_types_fk_docid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Bill document ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Document'),
			'filter_type'   : 'nplist',
			'column_flex'   : 2
		}
	)
	template = Column(
		JSONData(),
		Comment('Bill parts template'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Parts')
		}
	)
	mutable = Column(
		NPBoolean(),
		Comment('Is template mutable?'),
		nullable=False,
		default=True,
		server_default=npbool(True),
		info={
			'header_string' : _('Mutable')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Bill type description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	privilege = relationship(
		'Privilege',
		backref=backref(
			'bill_types',
			passive_deletes=True
		)
	)
	io_type = relationship(
		'StashIOType',
		backref=backref(
			'bill_types',
			passive_deletes=True
		)
	)
	document = relationship(
		'Document',
		backref=backref(
			'bill_types',
			passive_deletes=True
		)
	)

	def __str__(self):
		return str(self.name)

class Bill(Base):
	"""
	Bill object.
	"""
	__tablename__ = 'bills_def'
	__table_args__ = (
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
			}
		}
	)

