#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
	'Ticket',
	'TicketChange',
	'TicketChangeBit',
	'TicketChangeField',
	'TicketChangeFlagMod',
	'TicketDependency',
	'TicketFile',
	'TicketFlag',
	'TicketFlagType',
	'TicketOrigin',
	'TicketState',
	'TicketStateTransition'
]

from sqlalchemy import (
	Column,
	Date,
	FetchedValue,
	ForeignKey,
	Index,
	Numeric,
	Sequence,
	TIMESTAMP,
	Unicode,
	UnicodeText,
	func,
	text,
	or_
)

from sqlalchemy.orm import (
	backref,
	contains_eager,
	joinedload,
	relationship
)

from sqlalchemy.ext.associationproxy import association_proxy

#from colanderalchemy import (
#	Column,
#	relationship
#)

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
from netprofile.db.util import (
	populate_related,
	populate_related_list
)
from netprofile.ext.data import ExtModel
from netprofile.ext.columns import (
	HybridColumn,
	MarkupColumn
)
from netprofile.ext.wizards import (
	SimpleWizard,
	Step,
	Wizard,
	ExtJSWizardField
)
from netprofile_geo.models import (
	District,
	House,
	Street
)
from netprofile_geo.filters import AddressFilter

from pyramid.threadlocal import get_current_request
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile_tickets')

class TicketOrigin(Base):
	"""
	Ticket origin type.
	"""

	__tablename__ = 'tickets_origins'
	__table_args__ = (
		Comment('Origins of tickets'),
		Index('tickets_origins_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_TICKETS',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'TICKETS_ORIGINS_CREATE',
				'cap_edit'      : 'TICKETS_ORIGINS_EDIT',
				'cap_delete'    : 'TICKETS_ORIGINS_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Ticket Origins'),
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('name',),
				'form_view'     : ('name', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new ticket origin'))
			}
		}
	)
	id = Column(
		'toid',
		UInt32(),
		Sequence('toid_seq'),
		Comment('Ticket origin ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Ticket origin name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Ticket origin description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	def __str__(self):
		return '%s' % str(self.name)

class TicketState(Base):
	"""
	Ticket state type.
	"""

	__tablename__ = 'tickets_states_types'
	__table_args__ = (
		Comment('Ticket state types'),
		Index('tickets_states_types_u_tst', 'title', 'subtitle', unique=True),
		Index('tickets_states_types_i_is_start', 'is_start'),
		Index('tickets_states_types_i_is_end', 'is_end'),
		Index('tickets_states_types_i_flow', 'flow'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_TICKETS',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'TICKETS_STATES_CREATE',
				'cap_edit'      : 'TICKETS_STATES_EDIT',
				'cap_delete'    : 'TICKETS_STATES_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Ticket States'),
				'menu_order'    : 20,
				'default_sort'  : (
					{ 'property': 'title' ,'direction': 'ASC' },
					{ 'property': 'subtitle' ,'direction': 'ASC' }
				),
				'grid_view'     : (
					'title', 'subtitle',
					'flow', 'is_start', 'is_end'
				),
				'form_view'     : (
					'title', 'subtitle',
					'flow', 'is_start', 'is_end',
					'dur', 'style', 'image', 'descr'
				),
				'easy_search'   : ('title', 'subtitle'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new ticket state'))
			}
		}
	)
	id = Column(
		'tstid',
		UInt32(),
		Sequence('tstid_seq'),
		Comment('Ticket state ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	title = Column(
		Unicode(48),
		Comment('Ticket state title'),
		nullable=False,
		info={
			'header_string' : _('Title')
		}
	)
	subtitle = Column(
		Unicode(48),
		Comment('Ticket state subtitle'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Subtitle')
		}
	)
	flow = Column(
		UInt8(),
		Comment('Process flow index'),
		nullable=False,
		default=1,
		server_default=text('1'),
		info={
			'header_string' : _('Flow')
		}
	)
	is_start = Column(
		NPBoolean(),
		Comment('Can be starting state'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Start')
		}
	)
	is_end = Column(
		NPBoolean(),
		Comment('Can be ending state'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('End')
		}
	)
	duration = Column(
		'dur',
		UInt32(),
		Comment('Default ticket duration (in sec)'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Duration')
		}
	)
	style = Column(
		ASCIIString(16),
		Comment('Ticket state style'),
		nullable=False,
		default='grey',
		server_default='grey'
	)
	image = Column(
		ASCIIString(16),
		Comment('Ticket state image'),
		nullable=False,
		default='gears',
		server_default='gears'
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Ticket state description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	transition_to = association_proxy(
		'transitionmap_to',
		'to_state'
	)
	transition_from = association_proxy(
		'transitionmap_from',
		'from_state'
	)

	def __str__(self):
		j = []
		if self.title:
			j.append(self.title)
		if self.subtitle:
			j.append(self.subtitle)
		return ': '.join(j)

class TicketStateTransition(Base):
	"""
	Describes a transition between two distinct ticket states.
	"""

	__tablename__ = 'tickets_states_trans'
	__table_args__ = (
		Comment('Ticket state transitions'),
		Index('tickets_states_trans_u_trans', 'tstid_from', 'tstid_to', unique=True),
		Index('tickets_states_trans_i_tstid_to', 'tstid_to'),
		Index('tickets_states_trans_i_reassign_gid', 'reassign_gid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_TICKETS',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'TICKETS_TRANSITIONS_CREATE',
				'cap_edit'      : 'TICKETS_TRANSITIONS_EDIT',
				'cap_delete'    : 'TICKETS_TRANSITIONS_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Ticket Transitions'),
				'menu_order'    : 30,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('name', 'from_state', 'to_state'),
				'form_view'     : ('name', 'from_state', 'to_state', 'reassign_to', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new ticket transition'))
			}
		}
	)
	id = Column(
		'ttrid',
		UInt32(),
		Sequence('ttrid_seq'),
		Comment('Ticket transition ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(48),
		Comment('Ticket transition name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	from_state_id = Column(
		'tstid_from',
		UInt32(),
		ForeignKey('tickets_states_types.tstid', name='tickets_states_trans_fk_tstid_from', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('From state'),
		nullable=False,
		info={
			'header_string' : _('From')
		}
	)
	to_state_id = Column(
		'tstid_to',
		UInt32(),
		ForeignKey('tickets_states_types.tstid', name='tickets_states_trans_fk_tstid_to', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('To state'),
		nullable=False,
		info={
			'header_string' : _('To')
		}
	)
	reassign_to_id = Column(
		'reassign_gid',
		UInt32(),
		ForeignKey('groups.gid', name='tickets_states_trans_fk_reassign_gid', onupdate='CASCADE'), # ondelete=RESTRICT
		Comment('Reassign to group ID'),
		nullable=True,
		default=None,
		server_default=text('NULL')
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Ticket transition description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	from_state = relationship(
		'TicketState',
		foreign_keys=from_state_id,
		innerjoin=True,
		backref='transitionmap_to'
	)
	to_state = relationship(
		'TicketState',
		foreign_keys=to_state_id,
		innerjoin=True,
		backref='transitionmap_from'
	)
	reassign_to = relationship('Group')

	def __str__(self):
		return '%s' % self.name

	def apply(self, ticket):
		if ticket.state != self.from_state:
			raise ValueError('Invalid original state.')
		ticket.state = self.to_state
		if self.reassign_to:
			ticket.assigned_group = self.reassign_to

class TicketFlagType(Base):
	__tablename__ = 'tickets_flags_types'
	__table_args__ = (
		Comment('Ticket flag types'),
		Index('tickets_flags_types_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_TICKETS',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'TICKETS_FLAGTYPES_CREATE',
				'cap_edit'      : 'TICKETS_FLAGTYPES_EDIT',
				'cap_delete'    : 'TICKETS_FLAGTYPES_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Ticket Flags'),
				'menu_order'    : 40,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('name',),
				'form_view'     : ('name', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new ticket flag type'))
			}
		}
	)
	id = Column(
		'tftid',
		UInt32(),
		Sequence('tftid_seq'),
		Comment('Ticket flag type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Ticket flag type name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Ticket flag type description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	flagmap = relationship(
		'TicketFlag',
		backref=backref('type', innerjoin=True, lazy='joined'),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	flagmod = relationship(
		'TicketChangeFlagMod',
		backref=backref('flag_type', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	tickets = association_proxy(
		'flagmap',
		'ticket',
		creator=lambda v: TicketFlag(ticket=v)
	)

	def __str__(self):
		return '%s' % str(self.name)

class TicketFlag(Base):
	"""
	Many-to-many relationship object. Links tickets and ticket flags.
	"""
	__tablename__ = 'tickets_flags_def'
	__table_args__ = (
		Comment('Ticket flag mappings'),
		Index('tickets_flags_def_u_tf', 'ticketid', 'tftid', unique=True),
		Index('tickets_flags_def_i_tftid', 'tftid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_TICKETS',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'TICKETS_EDIT',
				'cap_edit'      : 'TICKETS_EDIT',
				'cap_delete'    : 'TICKETS_EDIT',

				'menu_name'     : _('Ticket Flags')
			}
		}
	)
	id = Column(
		'tfid',
		UInt32(),
		Sequence('tfid_seq'),
		Comment('Ticket flag ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	ticket_id = Column(
		'ticketid',
		UInt32(),
		ForeignKey('tickets_def.ticketid', name='tickets_flags_def_fk_ticketid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Ticket ID'),
		nullable=False,
		info={
			'header_string' : _('Ticket')
		}
	)
	type_id = Column(
		'tftid',
		UInt32(),
		ForeignKey('tickets_flags_types.tftid', name='tickets_flags_types_fk_tftid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Ticket flag type ID'),
		nullable=False,
		info={
			'header_string' : _('Type')
		}
	)

class TicketFile(Base):
	"""
	Many-to-many relationship object. Links tickets and files from VFS.
	"""
	__tablename__ = 'tickets_files'
	__table_args__ = (
		Comment('File mappings to tickets'),
		Index('tickets_files_u_tfl', 'ticketid', 'fileid', unique=True),
		Index('tickets_files_i_fileid', 'fileid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_TICKETS',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'FILES_ATTACH_2TICKETS',
				'cap_edit'      : 'FILES_ATTACH_2TICKETS',
				'cap_delete'    : 'FILES_ATTACH_2TICKETS',

				'menu_name'     : _('Files'),
				'grid_view'     : ('ticket', 'file'),

				'create_wizard' : SimpleWizard(title=_('Attach file'))
			}
		}
	)
	id = Column(
		'tfid',
		UInt32(),
		Sequence('file_tfid_seq'),
		Comment('Ticket-file mapping ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	ticket_id = Column(
		'ticketid',
		UInt32(),
		ForeignKey('tickets_def.ticketid', name='tickets_files_fk_ticketid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Ticket ID'),
		nullable=False,
		info={
			'header_string' : _('Ticket')
		}
	)
	file_id = Column(
		'fileid',
		UInt32(),
		ForeignKey('files_def.fileid', name='tickets_files_fk_fileid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('File ID'),
		nullable=False,
		info={
			'header_string' : _('File')
		}
	)

	file = relationship(
		'File',
		backref=backref(
			'linked_tickets',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)

	def __str__(self):
		return '%s' % str(self.file)

def _wizfld_ticket_state(fld, model, req, **kwargs):
	sess = DBSession()
	loc = get_localizer(req)
	data = []
	for ts in sess.query(TicketState).filter(TicketState.is_start == True).order_by('title', 'subtitle'):
		data.append({
			'id'    : ts.id,
			'value' : str(ts)
		})
	return {
		'xtype'          : 'combobox',
		'allowBlank'     : False,
		'name'           : 'tstid',
		'format'         : 'string',
		'displayField'   : 'value',
		'valueField'     : 'id',
		'hiddenName'     : 'tstid',
		'queryMode'      : 'local',
		'editable'       : False,
		'forceSelection' : True,
		'store'          : {
			'xtype'  : 'simplestore',
			'fields' : ('id', 'value'),
			'data'   : data
		},
		'fieldLabel'     : loc.translate(_('State'))
	}

def _wizcb_ticket_submit(wiz, step, act, val, req):
	sess = DBSession()
	em = ExtModel(Ticket)
	obj = Ticket(origin_id=1)
	em.set_values(obj, val, req, True)
	sess.add(obj)
	return {
		'do'     : 'close',
		'reload' : True
	}

class Ticket(Base):
	"""
	Main ticket object. Holds current ticket state.
	"""
	__tablename__ = 'tickets_def'
	__table_args__ = (
		Comment('Tickets'),
		Index('tickets_def_i_entityid', 'entityid'),
		Index('tickets_def_i_name', 'name'),
		Index('tickets_def_i_tstid', 'tstid'),
		Index('tickets_def_i_cby', 'cby'),
		Index('tickets_def_i_mby', 'mby'),
		Index('tickets_def_i_tby', 'tby'),
		Index('tickets_def_i_assigned_uid', 'assigned_uid'),
		Index('tickets_def_i_assigned_gid', 'assigned_gid'),
		Index('tickets_def_i_toid', 'toid'),
		Index('tickets_def_i_archived', 'archived'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_TICKETS',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'TICKETS_CREATE',
				'cap_edit'      : 'TICKETS_DIRECT',
				'cap_delete'    : 'TICKETS_DIRECT',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('Tickets'),
				'menu_main'     : True,
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'cby' ,'direction': 'DESC' },),
				'grid_view'     : (
					'ticketid', 'entity', 'state',
					'assigned_group', 'name'
				),
				'form_view'     : (
					'entity', 'name', 'state', 'flags', 'origin',
					'assigned_user', 'assigned_group', 'assigned_time',
					'archived', 'descr', 'ctime', 'created_by',
					'mtime', 'modified_by', 'ttime', 'transition_by'
				),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_tickets.views', 'dpane_tickets'),

#				'create_wizard' :
				'create_wizard' : Wizard(
					Step(
						'entity', 'name',
						ExtJSWizardField(_wizfld_ticket_state),
						'flags', 'descr',
						id='generic',
						on_submit=_wizcb_ticket_submit
					),
					title=_('Add new ticket')
				)
			}
		}
	)
	id = Column(
		'ticketid',
		UInt32(),
		Sequence('ticketid_seq'),
		Comment('Ticket ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='tickets_def_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		nullable=False,
		info={
			'header_string' : _('Entity'),
			'filter_type'   : 'none',
			'write_cap'     : 'TICKETS_CHANGE_ENTITY'
		}
	)
	state_id = Column(
		'tstid',
		UInt32(),
		ForeignKey('tickets_states_types.tstid', name='tickets_def_fk_tstid', onupdate='CASCADE'), # ondelete=RESTRICT
		Comment('Ticket state ID'),
		nullable=False,
		info={
			'header_string' : _('State'),
			'filter_type'   : 'list'
		}
	)
	origin_id = Column(
		'toid',
		UInt32(),
		ForeignKey('tickets_origins.toid', name='tickets_def_fk_toid', onupdate='CASCADE'), # ondelete=RESTRICT
		Comment('Ticket origin ID'),
		nullable=False,
		info={
			'header_string' : _('Origin'),
			'filter_type'   : 'list'
		}
	)
	assigned_user_id = Column(
		'assigned_uid',
		UInt32(),
		ForeignKey('users.uid', name='tickets_def_fk_assigned_uid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Assigned to user ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('User'),
			'filter_type'   : 'list',
			'write_cap'     : 'TICKETS_CHANGE_UID'
		}
	)
	assigned_group_id = Column(
		'assigned_gid',
		UInt32(),
		ForeignKey('groups.gid', name='tickets_def_fk_assigned_gid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Assigned to group ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Group'),
			'filter_type'   : 'list',
			'write_cap'     : 'TICKETS_CHANGE_GID'
		}
	)
	assigned_time = Column(
		TIMESTAMP(),
		Comment('Assigned to date'),
		nullable=True,
		default=None,
#		server_default=text('NULL'),
		info={
			'header_string' : _('Due'),
			'write_cap'     : 'TICKETS_CHANGE_DATE'
		}
	)
	duration = Column(
		'dur',
		UInt32(),
		Comment('Ticket duration (in sec)'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Duration'),
			'write_cap'     : 'TICKETS_CHANGE_DATE'
		}
	)
	archived = Column(
		NPBoolean(),
		Comment('Is archived'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Archived'),
			'write_cap'     : 'TICKETS_ARCHIVAL'
		}
	)
	name = Column(
		Unicode(255),
		Comment('Ticket name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Ticket description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
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
		nullable=False,
#		default=zzz,
		server_default=func.current_timestamp(),
		server_onupdate=func.current_timestamp(),
		info={
			'header_string' : _('Modified'),
			'read_only'     : True
		}
	)
	transition_time = Column(
		'ttime',
		TIMESTAMP(),
		Comment('Last state transition timestamp'),
		nullable=True,
		default=None,
#		server_default=text('NULL'),
		info={
			'header_string' : _('Transition'),
			'read_only'     : True
		}
	)
	created_by_id = Column(
		'cby',
		UInt32(),
		ForeignKey('users.uid', name='tickets_def_fk_cby', ondelete='SET NULL', onupdate='CASCADE'),
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
		ForeignKey('users.uid', name='tickets_def_fk_mby', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Modified by'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Modified'),
			'read_only'     : True
		}
	)
	transition_by_id = Column(
		'tby',
		UInt32(),
		ForeignKey('users.uid', name='tickets_def_fk_tby', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Transition by'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Transition'),
			'read_only'     : True
		}
	)

	entity = relationship(
		'Entity',
		innerjoin=True,
		lazy='joined',
		backref='tickets'
	)
	state = relationship(
		'TicketState',
		innerjoin=True,
		backref='tickets'
	)
	origin = relationship(
		'TicketOrigin',
		innerjoin=True,
		backref='tickets'
	)
	assigned_user = relationship(
		'User',
		foreign_keys=assigned_user_id,
		backref='assigned_tickets'
	)
	assigned_group = relationship(
		'Group',
		backref='assigned_tickets'
	)
	created_by = relationship(
		'User',
		foreign_keys=created_by_id,
		backref='created_tickets'
	)
	modified_by = relationship(
		'User',
		foreign_keys=modified_by_id,
		backref='modified_tickets'
	)
	transition_by = relationship(
		'User',
		foreign_keys=transition_by_id,
		backref='transitioned_tickets'
	)
	flagmap = relationship(
		'TicketFlag',
		backref=backref('ticket', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	filemap = relationship(
		'TicketFile',
		backref=backref('ticket', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	changes = relationship(
		'TicketChange',
		backref=backref('ticket', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	flags = association_proxy(
		'flagmap',
		'type',
		creator=lambda v: TicketFlag(type=v)
	)
	files = association_proxy(
		'filemap',
		'file',
		creator=lambda v: TicketFile(file=v)
	)
	parents = association_proxy(
		'parent_map',
		'parent',
		creator=lambda v: TicketDependency(parent=v)
	)
	children = association_proxy(
		'child_map',
		'child',
		creator=lambda v: TicketDependency(child=v)
	)

	def __str__(self):
		return '%s' % self.name

	@classmethod
	def __augment_result__(cls, sess, res, params):
		populate_related_list(
			res, 'id', 'flagmap', TicketFlag,
			sess.query(TicketFlag),
			None, 'ticket_id'
		)
		return res

class TicketChangeField(Base):
	"""
	Type of a ticket field change.
	"""
	__tablename__ = 'tickets_changes_fields'
	__table_args__ = (
		Comment('Ticket change fields'),
		Index('tickets_changes_fields_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				# FIXME: add proper capabilities
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'BASE_ADMIN',
				'cap_edit'      : 'BASE_ADMIN',
				'cap_delete'    : 'BASE_ADMIN',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Change Fields'),
				'menu_main'     : True,
				'menu_order'    : 30,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('name',),
				'easy_search'   : ('name',),

				'create_wizard' : SimpleWizard(title=_('Add new change field'))
			}
		}
	)
	id = Column(
		'tcfid',
		UInt32(),
		Sequence('tcfid_seq'),
		Comment('Ticket change field ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Ticket change field name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)

	bits = relationship(
		'TicketChangeBit',
		backref=backref('field', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

class TicketChange(Base):
	"""
	Describes an atomic ticket change.
	"""
	__tablename__ = 'tickets_changes_def'
	__table_args__ = (
		Comment('Ticket changes'),
		Index('tickets_changes_def_i_ticketid', 'ticketid'),
		Index('tickets_changes_def_i_uid', 'uid'),
		Index('tickets_changes_def_i_ts', 'ts'),
		Index('tickets_changes_def_i_ttrid', 'ttrid'),
		Index('tickets_changes_def_i_show_client', 'show_client'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_TICKETS',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : '__NOPRIV__',
				'cap_edit'      : '__NOPRIV__',
				'cap_delete'    : '__NOPRIV__',

				'menu_name'     : _('Changes'),
				'default_sort'  : ({ 'property': 'ts' ,'direction': 'DESC' },),
				'grid_view'     : (),
				'easy_search'   : ()
			}
		}
	)
	id = Column(
		'tcid',
		UInt32(),
		Sequence('tcid_seq'),
		Comment('Ticket change ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	ticket_id = Column(
		'ticketid',
		UInt32(),
		ForeignKey('tickets_def.ticketid', name='tickets_changes_def_fk_ticketid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Ticket ID'),
		nullable=False,
		info={
			'header_string' : _('Ticket'),
			'filter_type'   : 'none'
		}
	)
	transition_id = Column(
		'ttrid',
		UInt32(),
		ForeignKey('tickets_states_trans.ttrid', name='tickets_changes_def_fk_ttrid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Ticket transition ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Transition'),
			'filter_type'   : 'list'
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='tickets_changes_def_fk_uid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('User'),
			'filter_type'   : 'list'
		}
	)
	timestamp = Column(
		'ts',
		TIMESTAMP(),
		Comment('Ticket change timestamp'),
		nullable=False,
#		default=
		server_default=func.current_timestamp(),
		info={
			'header_string' : _('Time')
		}
	)
	show_client = Column(
		NPBoolean(),
		Comment('Show comment to client'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Show to Client')
		}
	)
	comments = Column(
		UnicodeText(),
		Comment('Ticket change comments'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Comments')
		}
	)

	transition = relationship(
		'TicketStateTransition',
		backref='ticket_changes'
	)
	user = relationship(
		'User',
		backref='ticket_changes'
	)
	bits = relationship(
		'TicketChangeBit',
		backref=backref('change', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	flagmod = relationship(
		'TicketChangeFlagMod',
		backref=backref('change', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

class TicketChangeBit(Base):
	"""
	Describes an single ticket property change.
	"""
	__tablename__ = 'tickets_changes_bits'
	__table_args__ = (
		Comment('Ticket change bits'),
		Index('tickets_changes_bits_u_tcf', 'tcid', 'tcfid', unique=True),
		Index('tickets_changes_bits_i_tcfid', 'tcfid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_TICKETS',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : '__NOPRIV__',
				'cap_edit'      : '__NOPRIV__',
				'cap_delete'    : '__NOPRIV__',

				'menu_name'     : _('Change Bits'),
				'default_sort'  : (),
				'grid_view'     : (),
				'easy_search'   : ()
			}
		}
	)
	id = Column(
		'tcbid',
		UInt32(),
		Sequence('tcbid_seq'),
		Comment('Ticket change bit ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	change_id = Column(
		'tcid',
		UInt32(),
		ForeignKey('tickets_changes_def.tcid', name='tickets_changes_bits_fk_tcid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Ticket change ID'),
		nullable=False,
		info={
			'header_string' : _('Change'),
			'filter_type'   : 'none'
		}
	)
	field_id = Column(
		'tcfid',
		UInt32(),
		ForeignKey('tickets_changes_fields.tcfid', name='tickets_changes_bits_fk_tcfid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Ticket change field ID'),
		nullable=False,
		info={
			'header_string' : _('Field'),
			'filter_type'   : 'list'
		}
	)
	old = Column(
		Unicode(255),
		Comment('Old value'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Old')
		}
	)
	new = Column(
		Unicode(255),
		Comment('New value'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('New')
		}
	)

class TicketChangeFlagMod(Base):
	"""
	Describes a single change in ticket flag state.
	"""
	__tablename__ = 'tickets_changes_flagmod'
	__table_args__ = (
		Comment('Ticket change bits modifying flags'),
		Index('tickets_changes_flagmod_u_tcflag', 'tcid', 'tftid', unique=True),
		Index('tickets_changes_flagmod_i_tftid', 'tftid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_TICKETS',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : '__NOPRIV__',
				'cap_edit'      : '__NOPRIV__',
				'cap_delete'    : '__NOPRIV__',

				'menu_name'     : _('Flag Bits'),
				'default_sort'  : (),
				'grid_view'     : (),
				'easy_search'   : ()
			}
		}
	)
	id = Column(
		'tcfmodid',
		UInt32(),
		Sequence('tcfmodid_seq'),
		Comment('Ticket change flag modification ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	change_id = Column(
		'tcid',
		UInt32(),
		ForeignKey('tickets_changes_def.tcid', name='tickets_changes_flagmod_fk_tcid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Ticket change ID'),
		nullable=False,
		info={
			'header_string' : _('Change')
		}
	)
	flag_type_id = Column(
		'tftid',
		UInt32(),
		ForeignKey('tickets_flags_types.tftid', name='tickets_changes_flagmod_fk_tftid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Ticket flag type ID'),
		nullable=False,
		info={
			'header_string' : _('Flag')
		}
	)
	new_state = Column(
		'newstate',
		NPBoolean(),
		Comment('Resulting flag state'),
		nullable=False,
		info={
			'header_string' : _('State')
		}
	)

class TicketDependency(Base):
	"""
	Describes a parent-child relationship between tickets.
	"""
	__tablename__ = 'tickets_dependencies'
	__table_args__ = (
		Comment('Ticket resolution dependencies'),
		Index('tickets_dependencies_i_ticketid_child', 'ticketid_child'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_TICKETS',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : '__NOPRIV__',
				'cap_edit'      : '__NOPRIV__',
				'cap_delete'    : '__NOPRIV__',

				'menu_name'     : _('Dependencies'),
				'default_sort'  : (),
				'grid_view'     : (),
				'easy_search'   : ()
			}
		}
	)
	ticket_id_parent = Column(
		'ticketid_parent',
		UInt32(),
		ForeignKey('tickets_def.ticketid', name='tickets_dependencies_fk_ticketid_parent', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Ticket which is dependent on'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('Parent'),
			'filter_type'   : 'none'
		}
	)
	ticket_id_child = Column(
		'ticketid_child',
		UInt32(),
		ForeignKey('tickets_def.ticketid', name='tickets_dependencies_fk_ticketid_child', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Ticket which depends on a parent'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('Child'),
			'filter_type'   : 'none'
		}
	)

	parent = relationship(
		'Ticket',
		foreign_keys=ticket_id_parent,
		innerjoin=True,
		backref=backref(
			'child_map',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	child = relationship(
		'Ticket',
		foreign_keys=ticket_id_child,
		innerjoin=True,
		backref=backref(
			'parent_map',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)

