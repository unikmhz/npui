#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Stashes module - Models
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
	'FuturePayment',
	'Stash',
	'StashIO',
	'StashIOType',
	'StashOperation',

	'FuturesPollProcedure',

	'FuturesPollEvent'
]

from sqlalchemy import (
	Column,
	FetchedValue,
	ForeignKey,
	Index,
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
	Money,
	NPBoolean,
	Traffic,
	UInt32,
	UInt64,
	npbool
)
from netprofile.ext.data import ExtModel
from netprofile.db.ddl import (
	Comment,
	CurrentTimestampDefault,
	SQLEvent,
	SQLFunction,
	Trigger
)

from netprofile.ext.wizards import (
	SimpleWizard,
	Step,
	Wizard
)
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile_stashes')

class OperationClass(DeclEnum):
	"""
	Stash I/O class enumeration.
	"""
	system = 'system', _('System'), 10
	user   = 'user',   _('User'),   20

class IOOperationType(DeclEnum):
	"""
	Stash I/O type enumeration.
	"""
	bidirectional = 'inout', _('Bidirectional'), 10
	incoming      = 'in',    _('Incoming'),      20
	outgoing      = 'out',   _('Outgoing'),      30

class StashOperationType(DeclEnum):
	"""
	Stash operation type enumeration.
	"""
	sub_qin_qeg   = 'sub_qin_qeg',   _('Subtract (under quota ingress / under quota egress)'), 10
	sub_min_qeg   = 'sub_min_qeg',   _('Subtract (mixed ingress / under quota egress)'),       20
	sub_oqin_qeg  = 'sub_oqin_qeg',  _('Subtract (over quota ingress / under quota egress)'),  30
	sub_qin_meg   = 'sub_qin_meg',   _('Subtract (under quota ingress / mixed egress)'),       40
	sub_qin_oqeg  = 'sub_qin_oqeg',  _('Subtract (under quota ingress / over quota egress)'),  50
	sub_min_meg   = 'sub_min_meg',   _('Subtract (mixed ingress / mixed egress)'),             60
	sub_oqin_meg  = 'sub_oqin_meg',  _('Subtract (over quota ingress / mixed egress)'),        70
	sub_min_oqeg  = 'sub_min_oqeg',  _('Subtract (mixed ingress / over quota egress)'),        80
	sub_oqin_oqeg = 'sub_oqin_oqeg', _('Subtract (over quota ingress / over quota egress)'),   90
	add_cash      = 'add_cash',      _('Add cash'),                                            100
	add_auto      = 'add_auto',      _('Automatic add'),                                       110
	oper          = 'oper',          _('Operator'),                                            120
	rollback      = 'rollback',      _('Rollback'),                                            130

class FuturePaymentState(DeclEnum):
	"""
	Future payment state enumeration.
	"""
	active    = 'A', _('Active'),    10
	paid      = 'P', _('Paid'),      20
	cancelled = 'C', _('Cancelled'), 30

class FuturePaymentOrigin(DeclEnum):
	"""
	Future payment origin enumeration.
	"""
	operator = 'oper', _('Operator'), 10
	user     = 'user', _('User'),     20

class Stash(Base):
	"""
	Stash object.
	"""
	__tablename__ = 'stashes_def'
	__table_args__ = (
		Comment('Stashes of money'),
		Index('stashes_def_i_entityid', 'entityid'),
		Trigger('before', 'insert', 't_stashes_def_bi'),
		Trigger('before', 'update', 't_stashes_def_bu'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_STASHES',
				'cap_read'      : 'STASHES_LIST',
				'cap_create'    : 'STASHES_CREATE',
				'cap_edit'      : 'STASHES_EDIT',
				'cap_delete'    : 'STASHES_DELETE',
				'menu_name'     : _('Stashes'),
				'menu_main'     : True,
				'show_in_menu'  : 'modules',
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('entity', 'name', 'amount', 'credit'),
				'form_view'     : ('entity', 'name', 'amount', 'credit', 'alltime_min', 'alltime_max'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new stash'))
			}
		}
	)
	id = Column(
		'stashid',
		UInt32(),
		Sequence('stashes_def_stashid_seq'),
		Comment('Stash ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		Comment('Owner entity ID'),
		ForeignKey('entities_def.entityid', name='stashes_def_fk_entityid', onupdate='CASCADE', ondelete='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Entity'),
			'filter_type'   : 'none',
			'column_flex'   : 2
		}
	)
	name = Column(
		Unicode(255),
		Comment('Stash name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)
	amount = Column(
		Money(),
		Comment('Stash balance'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Balance'),
			'column_flex'   : 1
		}
	)
	credit = Column(
		Money(),
		Comment('Stash credit'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Credit'),
			'column_flex'   : 1
		}
	)
	alltime_max = Column(
		Money(),
		Comment('All-time maximum balance'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Max. Balance'),
			'read_only'     : True
		}
	)
	alltime_min = Column(
		Money(),
		Comment('All-time minimum balance'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Min. Balance'),
			'read_only'     : True
		}
	)

	entity = relationship(
		'Entity',
		innerjoin=True,
		backref=backref(
			'stashes',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)

	def __str__(self):
		return '%s: %s' % (
			self.entity.nick,
			str(self.name)
		)

class StashIOType(Base):
	"""
	Stash I/O operation type object.
	"""
	__tablename__ = 'stashes_io_types'
	__table_args__ = (
		Comment('Stashes input/output operation types'),
		Index('stashes_io_types_i_type', 'type'),
		Index('stashes_io_types_i_oper_visible', 'oper_visible'),
		Index('stashes_io_types_i_user_visible', 'user_visible'),
		Index('stashes_io_types_i_oper_cap', 'oper_cap'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_STASHES',
				'cap_read'      : 'STASHES_IO',
				'cap_create'    : 'STASHES_IOTYPES_CREATE',
				'cap_edit'      : 'STASHES_IOTYPES_EDIT',
				'cap_delete'    : 'STASHES_IOTYPES_DELETE',
				'menu_name'     : _('Operation Types'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ('name', 'class', 'type'),
				'form_view'     : ('name', 'class', 'type', 'user_visible', 'oper_visible', 'oper_capability', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new operation type'))
			}
		}
	)
	id = Column(
		'siotypeid',
		UInt32(),
		Sequence('stashes_io_types_siotypeid_seq', start=101, increment=1),
		Comment('Stash I/O ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name  = Column(
		Unicode(255),
		Comment('Stash I/O name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	io_class = Column(
		'class',
		OperationClass.db_type(),
		Comment('Stash I/O class'),
		nullable=False,
		default=OperationClass.system,
		server_default=OperationClass.system,
		info={
			'header_string' : _('Class')
		}
	)
	type = Column(
		IOOperationType.db_type(),
		Comment('Stash I/O type'),
		nullable=False,
		default=IOOperationType.bidirectional,
		server_default=IOOperationType.bidirectional,
		info={
			'header_string' : _('Type')
		}
	)
	oper_visible = Column(
		NPBoolean(),
		Comment('Visibility in operator interface'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Visible to Operator')
		}
	)
	user_visible = Column(
		NPBoolean(),
		Comment('Visibility in user interface'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Visible to User')
		}
	)
	oper_capability_code = Column(
		'oper_cap',
		ASCIIString(48),
		Comment('Stash I/O required operator capability'),
		ForeignKey('privileges.code', name='stashes_io_types_fk_oper_cap', onupdate='CASCADE', ondelete='SET NULL'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Required Operator Capability')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Stash I/O description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	oper_capability = relationship(
		'Privilege',
		backref='stash_io_types',
		lazy='joined'
	)

	def __str__(self):
		return str(self.name)

def _wizcb_stashio_submit(wiz, step, act, val, req):
	sess = DBSession()
	em = ExtModel(StashIO)
	obj = StashIO()
	em.set_values(obj, val, req, True)
	sess.add(obj)
	if obj.difference:
		stash = sess.query(Stash).get(obj.stash_id)
		if stash:
			stash.amount += obj.difference
	return {
		'do'     : 'close',
		'reload' : True
	}

def _wizcb_future_submit(wiz, step, act, val, req):
	sess = DBSession()
	em = ExtModel(FuturePayment)
	obj = FuturePayment()
	em.set_values(obj, val, req, True)
	sess.add(obj)
	return {
		'do'     : 'close',
		'reload' : True
	}

class StashIO(Base):
	"""
	Stash I/O operation object.
	"""
	__tablename__ = 'stashes_io_def'
	__table_args__ = (
		Comment('Stashes input/output operations'),
		Index('stashes_io_i_siotypeid', 'siotypeid'),
		Index('stashes_io_i_stashid', 'stashid'),
		Index('stashes_io_i_uid', 'uid'),
		Index('stashes_io_i_entityid', 'entityid'),
		Index('stashes_io_i_ts', 'ts'),
		Trigger('before', 'insert', 't_stashes_io_def_bi'),
		Trigger('after', 'insert', 't_stashes_io_def_ai'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_STASHES',
				'cap_read'      : 'STASHES_IO',
				'cap_create'    : 'STASHES_IO',
				'cap_edit'      : '__NOPRIV__',
				'cap_delete'    : '__NOPRIV__',
				'menu_name'     : _('Operations'),
				'show_in_menu'  : 'modules',
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'ts', 'direction': 'DESC' },),
				'grid_view' : ('type', 'stash', 'entity', 'user', 'ts', 'diff'),
				'form_view' : ('type', 'stash', 'entity', 'user', 'ts', 'diff', 'descr'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : Wizard(
					Step(
						'stash', 'type', 'diff', 'descr',
						id='generic',
						on_submit=_wizcb_stashio_submit
					),
					title=_('Add new operation')
				)
			}
		}
	)
	id = Column(
		'sioid',
		UInt32(),
		Sequence('stashes_io_def_sioid_seq'),
		Comment('Stash I/O ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	type_id = Column(
		'siotypeid',
		UInt32(),
		Comment('Stash I/O type ID'),
		ForeignKey('stashes_io_types.siotypeid', name='stashes_io_def_fk_siotypeid', ondelete='CASCADE', onupdate='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Type'),
			'filter_type'   : 'list',
			'editor_xtype'  : 'simplemodelselect',
			'editor_config' : {
				'extraParams' : { '__ffilter' : { 'oper_visible' : { 'eq' : True } } }
			},
			'column_flex'   : 2
		}
	)
	stash_id = Column(
		'stashid',
		UInt32(),
		Comment('Stash ID'),
		ForeignKey('stashes_def.stashid', name='stashes_io_def_fk_stashid', ondelete='CASCADE', onupdate='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Stash'),
			'filter_type'   : 'none',
			'column_flex'   : 2
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		Comment('User ID'),
		ForeignKey('users.uid', name='stashes_io_def_fk_uid', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Operator'),
			'filter_type'   : 'list'
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		Comment('Related entity ID'),
		ForeignKey('entities_def.entityid', name='stashes_io_def_fk_entityid', ondelete='SET NULL', onupdate='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Entity'),
			'filter_type'   : 'none',
			'column_flex'   : 1
		}
	)
	timestamp = Column(
		'ts',
		TIMESTAMP(),
		Comment('Time stamp of operation'),
		CurrentTimestampDefault(),
		nullable=False,
		info={
			'header_string' : _('Date'),
			'column_flex'   : 1
		}
	)
	difference = Column(
		'diff',
		Money(),
		Comment('Operation result'),
		nullable=False,
		info={
			'header_string' : _('Change')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	type = relationship(
		'StashIOType',
		innerjoin=True,
		lazy='joined',
		backref=backref(
			'ios',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	stash = relationship(
		'Stash',
		innerjoin=True,
		backref=backref(
			'ios',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	user = relationship(
		'User',
		backref='stash_ios'
	)
	entity = relationship(
		'Entity',
		backref='stash_ios'
	)

	def __str__(self):
		return '%s: %s' % (
			str(self.stash),
			str(self.type)
		)

class StashOperation(Base):
	"""
	Low-level stash operation object.
	"""
	__tablename__ = 'stashes_ops'
	__table_args__ = (
		Comment('Operations on stashes'),
		Index('stashes_ops_i_stashid', 'stashid'),
		Index('stashes_ops_i_type', 'type'),
		Index('stashes_ops_i_ts', 'ts'),
		Index('stashes_ops_i_operator', 'operator'),
		Index('stashes_ops_i_entityid', 'entityid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_STASHES',
				'cap_read'      : 'STASHES_IO',
				'cap_create'    : '__NOPRIV__',
				'cap_edit'      : '__NOPRIV__',
				'cap_delete'    : '__NOPRIV__',
				'menu_name'    : _('Operations'),
				'default_sort'  : ({ 'property': 'ts', 'direction': 'DESC' },),
				'grid_view' : ('type', 'stash', 'entity', 'operator_user', 'ts', 'diff', 'acct_ingress', 'acct_egress'),
				'form_view' : ('type', 'stash', 'entity', 'operator_user', 'ts', 'diff', 'acct_ingress', 'acct_egress')
			}
		}
	)
	id = Column(
		'stashopid',
		UInt64(),
		Sequence('stashes_ops_stashopid_seq'),
		Comment('Stash operation ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string': _('ID')
		}
	)
	stash_id = Column(
		'stashid',
		UInt32(),
		ForeignKey('stashes_def.stashid', name='stashes_ops_fk_stashid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Stash ID'),
		nullable=False,
		info={
			'header_string': _('Stash'),
			'filter_type'   : 'none'
		}
	)
	type = Column(
		StashOperationType.db_type(),
		Comment('Type of operation'),
		nullable=False,
		default=StashOperationType.oper,
		server_default=StashOperationType.oper,
		info={
			'header_string': _('Type')
		}
	)
	timestamp = Column(
		'ts',
		TIMESTAMP(),
		Comment('Time stamp of operation'),
		CurrentTimestampDefault(),
		nullable=False,
		info={
			'header_string' : _('Date')
		}
	)
	operator_id = Column(
		'operator',
		UInt32(),
		ForeignKey('users.uid', name='stashes_ops_fk_operator', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Optional operator ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Operator'),
			'filter_type'   : 'list'
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='stashes_ops_fk_entityid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Optional entity ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Entity'),
			'filter_type'   : 'none'
		}
	)
	difference = Column(
		'diff',
		Money(),
		Comment('Changes made to stash'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Change')
		}
	)
	accounted_ingress = Column(
		'acct_ingress',
		Traffic(),
		Comment('Accounted ingress traffic'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Ingress Traffic')
		}
	)
	accounted_egress = Column(
		'acct_egress',
		Traffic(),
		Comment('Accounted egress traffic'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Egress Traffic')
		}
	)
	comments = Column(
		UnicodeText(),
		Comment('Optional Comments'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Comments')
		}
	)

	stash = relationship(
		'Stash',
		innerjoin=True,
		backref=backref(
			'operations',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	operator_user = relationship(
		'User',
		backref='stash_operations'
	)
	entity = relationship(
		'Entity',
		backref='stash_operations'
	)

	def __str__(self):
		return '%s: %s' % (
			str(self.stash),
			str(self.timestamp)
		)

class FuturePayment(Base):
	"""
	Future payment object.
	"""
	__tablename__ = 'futures_def'
	__table_args__ = (
		Comment('Future payments'),
		Index('futures_def_i_futures', 'state', 'ptime'),
		Index('futures_def_i_entityid', 'entityid'),
		Index('futures_def_i_stashid', 'stashid'),
		Index('futures_def_i_cby', 'cby'),
		Index('futures_def_i_mby', 'mby'),
		Index('futures_def_i_pby', 'pby'),
		Trigger('before', 'insert', 't_futures_def_bi'),
		Trigger('before', 'update', 't_futures_def_bu'),
		Trigger('after', 'insert', 't_futures_def_ai'),
		Trigger('after', 'update', 't_futures_def_au'),
		Trigger('after', 'delete', 't_futures_def_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_FUTURES',
				'cap_read'      : 'FUTURES_LIST',
				'cap_create'    : 'FUTURES_CREATE',
				'cap_edit'      : 'FUTURES_EDIT',
				'cap_delete'    : '__NOPRIV__',
				# TODO: APPROVE/CANCEL
				'menu_name'     : _('Promised Payments'),
				'default_sort'  : ({ 'property': 'ctime', 'direction': 'DESC' },),
				'grid_view' : ('entity', 'stash', 'diff', 'state', 'ctime'),
				'form_view' : (
					'entity', 'stash', 'diff',
					'state', 'origin',
					'ctime', 'cby',
					'mtime', 'mby',
					'ptime', 'pby'
				),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : Wizard(
					Step(
						'entity', 'stash', 'diff', 'descr',
						id='generic',
						on_submit=_wizcb_future_submit
					),
					title=_('Add new promised payment')
				)
			}
		}
	)
	id = Column(
		'futureid',
		UInt32(),
		Sequence('futures_def_futureid_seq'),
		Comment('Future payment ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string': _('ID')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		Comment('Entity ID'),
		ForeignKey('entities_def.entityid', name='futures_def_fk_entityid', onupdate='CASCADE', ondelete='SET NULL'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Entity'),
			'filter_type'   : 'none',
			'column_flex'   : 2
		}
	)
	stash_id = Column(
		'stashid',
		UInt32(),
		Comment('Stash ID'),
		ForeignKey('stashes_def.stashid', name='futures_def_fk_stashid', ondelete='CASCADE', onupdate='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Stash'),
			'filter_type'   : 'none',
			'column_flex'   : 2
		}
	)
	difference = Column(
		'diff',
		Money(),
		Comment('Payment result'),
		nullable=False,
		default=0.0,
		server_default=text('0.0'),
		info={
			'header_string' : _('Change')
		}
	)
	state = Column(
		FuturePaymentState.db_type(),
		Comment('Active / Paid / Cancelled'),
		nullable=False,
		default=FuturePaymentState.active,
		server_default=FuturePaymentState.active,
		info={
			'header_string' : _('State')
		}
	)
	origin = Column(
		FuturePaymentOrigin.db_type(),
		Comment('Origin of payment'),
		nullable=False,
		default=FuturePaymentOrigin.operator,
		server_default=FuturePaymentOrigin.operator,
		info={
			'header_string' : _('Origin')
		}
	)
	creation_time = Column(
		'ctime',
		TIMESTAMP(),
		Comment('Creation timestamp'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Created'),
			'read_only'     : True
		}
	)
	modification_time = Column(
		'mtime',
		TIMESTAMP(),
		Comment('Last modification timestamp'),
		CurrentTimestampDefault(on_update=True),
		nullable=False,
#		default=zzz,
		info={
			'header_string' : _('Modified'),
			'read_only'     : True
		}
	)
	payment_time = Column(
		'ptime',
		TIMESTAMP(),
		Comment('Payment timestamp'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Paid'),
			'read_only'     : True
		}
	)
	created_by_id = Column(
		'cby',
		UInt32(),
		ForeignKey('users.uid', name='futures_def_fk_cby', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Created by'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Created'),
			'read_only'     : True
		}
	)
	modified_by_id = Column(
		'mby',
		UInt32(),
		ForeignKey('users.uid', name='futures_def_fk_mby', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Modified by'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Modified'),
			'read_only'     : True
		}
	)
	paid_by_id = Column(
		'pby',
		UInt32(),
		ForeignKey('users.uid', name='futures_def_fk_pby', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Payment confirmed by'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Confirmed'),
			'read_only'     : True
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)
	stash = relationship(
		'Stash',
		innerjoin=True,
		backref=backref(
			'futures',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	entity = relationship(
		'Entity',
		backref='stash_futures'
	)

	def __str__(self):
		return '%s: %s' % (
			str(self.stash),
			str(self.difference)
		)

FuturesPollProcedure = SQLFunction(
	'futures_poll',
	comment='Poll for expired futures',
	is_procedure=True
)

FuturesPollEvent = SQLEvent(
	'ev_futures_poll',
	sched_unit='hour',
	sched_interval=1,
	comment='Poll for expired promised payments'
)

