#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Paid Service module - Models
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
	'PaidService',
	'PaidServiceType',

	'PSCallbackProcedure',
	'PSExecuteProcedure',
	'PSPollProcedure',

	'PSPollEvent'
]

from sqlalchemy import (
	Column,
	DateTime,
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
	Money,
	NPBoolean,
	UInt8,
	UInt16,
	UInt32,
	UInt64,
	npbool
)
from netprofile.ext.data import ExtModel
from netprofile.db.ddl import (
	Comment,
	InArgument,
	InOutArgument,
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

from netprofile_rates.models import QuotaPeriodUnit

_ = TranslationStringFactory('netprofile_paidservices')

class PaidServiceQPType(DeclEnum):
	"""
	Paid Service type enumeration.
	"""
	independent = 'I',	_('Independent'),	10
	linked      = 'L',	_('Linked'),		20
	onetime		= 'O',	_('One Time'),		30

class PaidServiceType(Base):
	"""
	Paid service type object.
	"""
	__tablename__ = 'paid_types'
	__table_args__ = (
		Comment('Paid service types'),
		Index('paid_types_i_qp_type', 'qp_type'),
		Index('paid_types_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_PAIDSERVICES',
				'cap_read'      : 'PAIDSERVICES_LIST',
				'cap_create'    : 'PAIDSERVICETYPES_CREATE',
				'cap_edit'      : 'PAIDSERVICETYPES_EDIT',
				'cap_delete'    : 'PAIDSERVICETYPES_DELETE',
				'menu_main'     : True,
				'menu_name'     : _('Paid Services'),
				'show_in_menu'  : 'modules',
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'name', 'direction': 'ASC' },),
				'grid_view'     : ( 'name', 'isum', 'qsum', 'qp_amount', 'qp_unit', 'qp_type'),
				'form_view'     : (
					'name', 'isum', 'qsum',
					'qp_amount', 'qp_unit', 'qp_type', 'qp_order', 'sp_amount',
					'cb_before', 'cb_success', 'cb_failure', 'cb_ratemod',
					'descr'
				),
				'easy_search'   : ('name', 'descr'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new type'))
			}
		}
	)
	id = Column(
		'paidid',
		UInt32(),
		Sequence('paid_types_paidid_seq'),
		Comment('Paid service ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Paid service name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)
	initial_sum = Column(
		'isum',
		Money(),
		Comment('Initial payment sum'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Initial Payment'),
			'column_flex'   : 1
		}
	)
	quota_sum = Column(
		'qsum',
		Money(),
		Comment('Quota sum'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Quota Payment'),
			'column_flex'   : 1
		}
	)
	quota_period_type = Column(
		'qp_type',
		PaidServiceQPType.db_type(),
		Comment('Quota period type'),
		nullable=False,
		default=PaidServiceQPType.independent,
		server_default=PaidServiceQPType.independent,
		info={
			'header_string' : _('Type')
		}
	)
	pay_order = Column(
		'qp_order',
		UInt8(),
		Comment('Pay order for linked services'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Pay Order')
		}
	)
	skipped_periods = Column(
		'sp_amount',
		UInt16(),
		Comment('Number of skipped periods'),
		nullable=False,
		default=0,
		server_default=text('0'),
		info={
			'header_string' : _('Skipped Periods')
		}
	)
	quota_period_amount = Column(
		'qp_amount',
		UInt16(),
		Comment('Quota period amount'),
		nullable=False,
		default=1,
		server_default=text('1'),
		info={
			'header_string' : _('Quota Period Amount')
		}
	)
	quota_period_unit = Column(
		'qp_unit',
		QuotaPeriodUnit.db_type(),
		Comment('Quota period unit'),
		nullable=False,
		default=QuotaPeriodUnit.calendar_month,
		server_default=QuotaPeriodUnit.calendar_month,
		info={
			'header_string' : _('Quota Period Unit')
		}
	)
	cb_before = Column(
		ASCIIString(255),
		Comment('Callback before charging'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Callback Before Charging')
		}
	)
	cb_success= Column(
		ASCIIString(255),
		Comment('Callback on success'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Callback on Success')
		}
	)
	cb_failure = Column(
		ASCIIString(255),
		Comment('Callback on failure'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Callback on Failure')
		}
	)
	cb_ratemod = Column(
		ASCIIString(255),
		Comment('Callback on linked rate'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Callback on Linked Rate')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Paid service description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	def __str__(self):
		return '%s' % (
			str(self.name),
		)

class PaidService(Base):
	"""
	Paid service mapping object.
	"""
	__tablename__ = 'paid_def'
	__table_args__ = (
		Comment('Paid service mappings'),
		Index('paid_def_i_entityid', 'entityid'),
		Index('paid_def_i_aeid', 'aeid'),
		Index('paid_def_i_hostid', 'hostid'),
		Index('paid_def_i_stashid', 'stashid'),
		Index('paid_def_i_paidid', 'paidid'),
		Index('paid_def_i_active', 'active'),
		Index('paid_def_i_qpend', 'qpend'),
		Trigger('before', 'insert', 't_paid_def_bi'),
		Trigger('before', 'update', 't_paid_def_bu'),
		Trigger('after', 'insert', 't_paid_def_ai'),
		Trigger('after', 'update', 't_paid_def_au'),
		Trigger('after', 'delete', 't_paid_def_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_PAIDSERVICES',
				'cap_read'      : 'PAIDSERVICES_LIST',
				'cap_create'    : 'PAIDSERVICES_CREATE',
				'cap_edit'      : 'PAIDSERVICES_EDIT',
				'cap_delete'    : 'PAIDSERVICES_DELETE',
				'default_sort'  : ({ 'property': 'qpend', 'direction': 'DESC' },),
				'grid_view'     : ('entity', 'stash', 'type', 'active', 'qpend'),
				'form_view'     : (
				),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple')
			}
		}
	)
	id = Column(
		'epid',
		UInt32(),
		Sequence('paid_def_epid_seq'),
		Comment('Paid service mapping ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		Comment('Entity ID'),
		ForeignKey('entities_def.entityid', name='paid_def_fk_entityid', onupdate='CASCADE', ondelete='CASCADE'),
		nullable=False,
		info={
			'header_string' : _('Entity'),
			'filter_type'   : 'none',
			'column_flex'   : 2
		}
	)
	access_entity_id = Column(
		'aeid',
		UInt32(),
		Comment('Access entity ID'),
		ForeignKey('entities_access.entityid', name='paid_def_fk_aeid', onupdate='CASCADE', ondelete='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Access Entity'),
			'filter_type'   : 'none',
			'column_flex'   : 2
		}
	)
	host_id = Column(
		'hostid',
		UInt32(),
		Comment('Host ID'),
		ForeignKey('hosts_def.hostid', name='paid_def_fk_hostid', onupdate='CASCADE', ondelete='CASCADE'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Host'),
			'filter_type'   : 'none',
			'column_flex'   : 2
		}
	)
	stash_id = Column(
		'stashid',
		UInt32(),
		ForeignKey('stashes_def.stashid', name='paid_def_fk_stashid', onupdate='CASCADE', ondelete='CASCADE'),
		Comment('Used stash ID'),
		nullable=False,
		info={
			'header_string' : _('Stash'),
			'column_flex'   : 3
		}
	)
	paid_id = Column(
		'paidid',
		UInt32(),
		ForeignKey('paid_types.paidid', name='paid_def_fk_paidid', onupdate='CASCADE'),
		Comment('Type ID'),
		nullable=False,
		info={
			'header_string' : _('Stash'),
			'column_flex'   : 3
		}
	)
	active = Column(
		NPBoolean(),
		Comment('Is service active'),
		nullable=False,
		default=True,
		server_default=npbool(True),
		info={
			'header_string' : _('Active')
		}
	)
	quota_period_end = Column(
		'qpend',
		TIMESTAMP(),
		Comment('End of quota period'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Ends')
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
		'PaidServiceType',
		innerjoin=True,
		lazy='joined',
		backref='paid_services'
	)
	entity = relationship(
		'Entity',
		foreign_keys=entity_id,
		innerjoin=True,
		backref=backref(
			'paid_services',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	access_entity = relationship(
		'AccessEntity',
		foreign_keys=access_entity_id,
		backref=backref(
			'paid_services_access',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	host = relationship(
		'Host',
		backref=backref(
			'paid_services',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	stash = relationship(
		'Stash',
		innerjoin=True,
		backref=backref(
			'paid_services',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)

	def __str__(self):
		return '%s: %s' % (
			str(self.stash),
			str(self.type)
		)

PSCallbackProcedure = SQLFunction(
	'ps_callback',
	args=(
		InArgument('cbname', Unicode(255)),
		InArgument('xepid', UInt32()),
		InArgument('ts', DateTime()),
		InArgument('ps_aeid', UInt32()),
		InArgument('ps_hostid', UInt32()),
		InArgument('ps_paidid', UInt32()),
		InOutArgument('ps_entityid', UInt32()),
		InOutArgument('ps_stashid', UInt32()),
		InOutArgument('ps_qpend', DateTime()),
		InOutArgument('pay', Money())
	),
	comment='Callback helper for paid services',
	is_procedure=True
)

PSExecuteProcedure = SQLFunction(
	'ps_execute',
	args=(
		InArgument('xepid', UInt32()),
		InArgument('ts', DateTime())
	),
	comment='Execute paid service handler',
	label='psefunc',
	is_procedure=True
)

PSPollProcedure = SQLFunction(
	'ps_poll',
	args=(
		InArgument('ts', DateTime()),
	),
	comment='Poll paid services',
	is_procedure=True
)

PSPollEvent = SQLEvent(
	'ev_ps_poll',
	sched_unit='minute',
	sched_interval=15,
	comment='Poll for independent paid services'
)

