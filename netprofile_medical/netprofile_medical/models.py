#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
	'ICDBlock',
	'ICDClass',
	'ICDEntry',
	'ICDHistory',
	'ICDMapping',
	'MedicalTestType',
	'MedicalTest'
#	'MedicalCase'
]

from sqlalchemy import (
	Column,
	Date,
	FetchedValue,
	ForeignKey,
	func,
	Index,
	Sequence,
	Unicode,
	UnicodeText,
	text,
	Text,
	TIMESTAMP
)

from sqlalchemy.orm import (
	backref,
	relationship,
	validates
)

from sqlalchemy.ext.associationproxy import association_proxy

from netprofile.db.connection import (
	Base,
	DBSession
)

from netprofile.db.fields import (
	DeclEnum,
	UInt32
)
from netprofile.db.ddl import Comment
from netprofile.ext.data import ExtModel
from netprofile.ext.wizards import (
	CompositeWizardField,
	ExternalWizardField,
	ExtJSWizardField,
	SimpleWizard,
	Step,
	Wizard
)

from pyramid.threadlocal import get_current_request
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

from netprofile_entities.models import (
	Entity,
	EntityHistory,
	EntityHistoryPart
)
from netprofile_tickets.models import (
	Ticket,
	TicketDependency
)

_ = TranslationStringFactory('netprofile_medical')

def _wizcb_ticket_test_submit(wiz, step, act, val, req):
	sess = DBSession()
	em = ExtModel(Ticket)
	if ('medttid' not in val) or ('medttid' not in val):
		raise ValueError
	medtt = sess.query(MedicalTestType).get(int(val['medttid']))
	ent = sess.query(Entity).get(int(val['entityid']))
	if (medtt is None) or (ent is None):
		raise KeyError
	tpl = medtt.template
	obj = tpl.create_ticket(req, ent)
	em.set_values(obj, val, req, True)
	sess.add(obj)
	mt = MedicalTest(
		type=medtt,
		ticket=obj
	)
	if 'sample' in val:
		mt.sample = val['sample']
	sess.add(mt)
	if 'parentid' in val:
		td = TicketDependency(
			parent_id=int(val['parentid']),
			child=obj
		)
		sess.add(td)
	return {
		'do'     : 'close',
		'reload' : True
	}

def _wizfld_ticket_testtype(fld, model, req, **kwargs):
	sess = DBSession()
	loc = get_localizer(req)
	data = []
	for medtt in sess.query(MedicalTestType).order_by('name'):
		data.append({
			'id'    : medtt.id,
			'value' : str(medtt)
		})
	return {
		'xtype'          : 'combobox',
		'allowBlank'     : False,
		'name'           : 'medttid',
		'format'         : 'string',
		'displayField'   : 'value',
		'valueField'     : 'id',
		'hiddenName'     : 'medttid',
		'queryMode'      : 'local',
		'editable'       : False,
		'forceSelection' : True,
		'store'          : {
			'xtype'  : 'simplestore',
			'fields' : ('id', 'value'),
			'data'   : data
		},
		'fieldLabel'     : loc.translate(_('Scheduled Test'))
	}

Ticket.__table__.info['wizards']['medtest'] = Wizard(
	Step(
		'entity',
		ExtJSWizardField(_wizfld_ticket_testtype),
		ExternalWizardField('MedicalTest', 'sample'),
		'flags', 'descr',
		id='generic',
		on_submit=_wizcb_ticket_test_submit
	),
	title=_('Add medical test')
)

class MedicalTestType(Base):
	"""
	"""
	__tablename__ = 'med_tests_types'
	__table_args__ = (
		Comment('Medical test types'),
		Index('med_tests_types_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				# FIXME
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'TICKETS_LIST',
				'cap_edit'      : 'TICKETS_LIST',
				'cap_delete'    : 'TICKETS_LIST',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Test Types'),
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('name',),
				'form_view'     : ('name', 'template'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new test type'))
			}
		}
	)
	id = Column(
		'medttid',
		UInt32(),
		Sequence('medttid_seq'),
		Comment('Medical test type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Medical test type name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	template_id = Column(
		'ttplid',
		UInt32(),
		ForeignKey('tickets_templates.ttplid', name='med_tests_types_fk_ttplid', onupdate='CASCADE'), #ondelete=RESTRICT? or allow NULLs?
		Comment('Ticket template ID'),
		nullable=False,
		info={
			'header_string' : _('Template')
		}
	)

	template = relationship('TicketTemplate', innerjoin=True)

	def __str__(self):
		return '%s' % str(self.name)

class MedicalTest(Base):
	"""
	"""
	__tablename__ = 'med_tests_def'
	__table_args__ = (
		Comment('Medical test types'),
		Index('med_tests_def_i_medttid', 'medttid'),
		Index('med_tests_def_i_ticketid', 'ticketid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				# FIXME
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'TICKETS_LIST',
				'cap_edit'      : 'TICKETS_LIST',
				'cap_delete'    : 'TICKETS_LIST',

#				'show_in_menu'  : 'admin',
				'menu_name'     : _('Tests'),
#				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'sample' ,'direction': 'ASC' },),
				'grid_view'     : ('ticket', 'sample'),
				'form_view'     : ('type', 'ticket', 'sample', 'descr', 'res'),
				'easy_search'   : ('sample', 'descr', 'res'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new test'))
			}
		}
	)
	id = Column(
		'medtestid',
		UInt32(),
		Sequence('medtestid_seq'),
		Comment('Medical test ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	type_id = Column(
		'medttid',
		UInt32(),
		ForeignKey('med_tests_types.medttid', name='med_tests_def_fk_medttid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Medical test type ID'),
		nullable=False,
		info={
			'header_string' : _('Type')
		}
	)
	ticket_id = Column(
		'ticketid',
		UInt32(),
		ForeignKey('tickets_def.ticketid', name='med_tests_def_fk_ticketid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Ticket ID'),
		nullable=False,
		info={
			'header_string' : _('Ticket')
		}
	)
	sample = Column(
		Unicode(255),
		Comment('Physical sample description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Sample')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Sample description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)
	results = Column(
		'res',
		UnicodeText(),
		Comment('Sample description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Results')
		}
	)

	type = relationship(
		'MedicalTestType',
		innerjoin=True,
		backref='medical_tests'
	)
	ticket = relationship(
		'Ticket',
		innerjoin=True,
		backref='medical_tests'
	)

	def __str__(self):
		return '%s: #%s' % (
			str(self.type),
			str(self.sample)
		)

class ICDClass(Base):
	"""
	"""
	__tablename__ = 'med_icd_classes'
	__table_args__ = (
		Comment('Disease classes'),
		Index('med_icd_classes_u_code', 'code', unique=True),
		Index('med_icd_classes_i_name', 'name'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				# FIXME
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'TICKETS_LIST',
				'cap_edit'      : 'TICKETS_LIST',
				'cap_delete'    : 'TICKETS_LIST',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('ICD Classes'),
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'code' ,'direction': 'ASC' },),
				'grid_view'     : ('code', 'name'),
				'form_view'     : ('code', 'name'),
				'easy_search'   : ('code', 'name'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new ICD class'))
			}
		}
	)
	id = Column(
		'icdcid',
		UInt32(),
		Sequence('med_icd_classes_icdcid_seq'),
		Comment('ICD class ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	code = Column(
		Unicode(48),
		Comment('ICD class code'),
		nullable=False,
		info={
			'header_string' : _('Code')
		}
	)
	name = Column(
		Unicode(255),
		Comment('ICD class name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)

	blocks = relationship(
		'ICDBlock',
		backref=backref('cls', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def __str__(self):
		return '%s: %s' % (
			str(self.code),
			str(self.name)
		)

class ICDBlock(Base):
	"""
	"""
	__tablename__ = 'med_icd_blocks'
	__table_args__ = (
		Comment('Disease blocks'),
		Index('med_icd_blocks_u_code', 'code', unique=True),
		Index('med_icd_blocks_i_name', 'name'),
		Index('med_icd_blocks_i_icdcid', 'icdcid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				# FIXME
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'TICKETS_LIST',
				'cap_edit'      : 'TICKETS_LIST',
				'cap_delete'    : 'TICKETS_LIST',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('ICD Blocks'),
				'menu_order'    : 20,
				'default_sort'  : ({ 'property': 'code' ,'direction': 'ASC' },),
				'grid_view'     : ('cls', 'code', 'name'),
				'form_view'     : ('cls', 'code', 'name'),
				'easy_search'   : ('code', 'name'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new ICD block'))
			}
		}
	)
	id = Column(
		'icdbid',
		UInt32(),
		Sequence('med_icd_blocks_icdbid_seq'),
		Comment('ICD block ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	cls_id = Column(
		'icdcid',
		UInt32(),
		ForeignKey('med_icd_classes.icdcid', name='med_icd_blocks_fk_icdcid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('ICD class ID'),
		nullable=False,
		info={
			'header_string' : _('Class'),
			'filter_type'   : 'list',
			'column_flex'   : 1
		}
	)
	code = Column(
		Unicode(48),
		Comment('ICD block code'),
		nullable=False,
		info={
			'header_string' : _('Code')
		}
	)
	name = Column(
		Unicode(255),
		Comment('ICD block name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)

	entries = relationship(
		'ICDEntry',
		backref=backref('block', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def __str__(self):
		return '%s: %s' % (
			str(self.code),
			str(self.name)
		)

class ICDEntry(Base):
	"""
	"""
	__tablename__ = 'med_icd_entries'
	__table_args__ = (
		Comment('Disease entries'),
		Index('med_icd_entries_u_code', 'code', unique=True),
		Index('med_icd_entries_i_name', 'name'),
		Index('med_icd_entries_i_icdbid', 'icdbid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				# FIXME
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'TICKETS_LIST',
				'cap_edit'      : 'TICKETS_LIST',
				'cap_delete'    : 'TICKETS_LIST',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('ICD Entries'),
				'menu_order'    : 30,
				'default_sort'  : ({ 'property': 'code' ,'direction': 'ASC' },),
				'grid_view'     : ('block', 'code', 'name'),
				'form_view'     : ('block', 'code', 'name'),
				'easy_search'   : ('code', 'name'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new ICD entry'))
			}
		}
	)
	id = Column(
		'icdeid',
		UInt32(),
		Sequence('med_icd_entries_icdeid_seq'),
		Comment('ICD entry ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	block_id = Column(
		'icdbid',
		UInt32(),
		ForeignKey('med_icd_blocks.icdbid', name='med_icd_entries_fk_icdbid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('ICD block ID'),
		nullable=False,
		info={
			'header_string' : _('Block'),
			'filter_type'   : 'list',
			'column_flex'   : 2
		}
	)
	code = Column(
		Unicode(48),
		Comment('ICD entry code'),
		nullable=False,
		info={
			'header_string' : _('Code')
		}
	)
	name = Column(
		Unicode(255),
		Comment('ICD entry name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)

	mappings = relationship(
		'ICDMapping',
		backref=backref('entry', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	def __str__(self):
		return '%s: %s' % (
			str(self.code),
			str(self.name)
		)

class ICDMappingType(DeclEnum):
	"""
	"""
	suspicion = 'susp', _('Suspicion'), 10
	history   = 'hist', _('History'),   20
	diagnosis = 'diag', _('Diagnosis'), 30

class ICDMapping(Base):
	"""
	"""
	__tablename__ = 'med_icd_mappings'
	__table_args__ = (
		Comment('Disease entry mappings'),
		Index('med_icd_mappings_i_icdeid', 'icdeid'),
		Index('med_icd_mappings_i_entityid', 'entityid'),
		Index('med_icd_mappings_i_ticketid', 'ticketid'),
		Index('med_icd_mappings_i_uid', 'uid'),
		Index('med_icd_mappings_i_ctime', 'ctime'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				# FIXME
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : 'TICKETS_LIST',
				'cap_edit'      : 'TICKETS_LIST',
				'cap_delete'    : 'TICKETS_LIST',

				'menu_name'     : _('Diseases'),
				'default_sort'  : ({ 'property': 'ctime' ,'direction': 'DESC' },),
				'grid_view'     : ('entity', 'ticket', 'type', 'entry', 'ctime'),
				'form_view'     : ('entity', 'ticket', 'type', 'entry', 'user', 'ctime', 'comment'),
				'easy_search'   : ('comment',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : Wizard(
					Step(
						'ticket', 'entry', 'type',
						title=_('Enter classification and type')
					),
					title=_('Add new disease')
				)
#				'create_wizard' : SimpleWizard(title=_('Add new ICD mapping'))
			}
		}
	)
	id = Column(
		'icdmid',
		UInt32(),
		Sequence('med_icd_mappings_icdmid_seq'),
		Comment('ICD entry mapping ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	entry_id = Column(
		'icdeid',
		UInt32(),
		ForeignKey('med_icd_entries.icdeid', name='med_icd_mappings_fk_icdeid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('ICD entry ID'),
		nullable=False,
		info={
			'header_string' : _('Entry'),
			'filter_type'   : 'none',
			'column_flex'   : 1
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='med_icd_mappings_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		nullable=False,
		info={
			'header_string' : _('Entity'),
			'filter_type'   : 'none'
		}
	)
	ticket_id = Column(
		'ticketid',
		UInt32(),
		ForeignKey('tickets_def.ticketid', name='med_icd_mappings_fk_ticketid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Ticket ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Ticket'),
			'filter_type'   : 'none'
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='med_icd_mappings_fk_uid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('User'),
			'filter_type'   : 'none',
			'read_only'     : True
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
	type = Column(
		ICDMappingType.db_type(),
		Comment('ICD mapping type'),
		nullable=False,
		default=ICDMappingType.suspicion,
		server_default=ICDMappingType.suspicion,
		info={
			'header_string' : _('Type')
		}
	)
	comment = Column(
		UnicodeText(),
		Comment('ICD mapping comment'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Comment')
		}
	)

	entity = relationship(
		'Entity',
		innerjoin=True,
		foreign_keys=(entity_id,),
		backref=backref(
			'diseases',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	ticket = relationship(
		'Ticket',
		foreign_keys=(ticket_id,),
		backref=backref(
			'diseases',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	user = relationship('User')

	def __str__(self):
		req = get_current_request()
		loc = get_localizer(req)
		td = _('Disease')
		if self.type is not None:
			td = self.type.description
		return '%s: %s' % (
			loc.translate(td),
			str(self.entry)
		)

	@validates('ticket_id')
	def _set_ticket(self, k, v):
		if v:
			sess = DBSession()
			tkt = sess.query(Ticket).get(int(v))
			if isinstance(tkt, Ticket):
				self.entity = tkt.entity
		return v

class ICDHistoryEventType(DeclEnum):
	"""
	"""
	created  = 'C', _('Created'),  10
	modified = 'M', _('Modified'), 20
	deleted  = 'D', _('Deleted'),  30

class ICDHistory(Base):
	"""
	"""
	__tablename__ = 'med_icd_history'
	__table_args__ = (
		Comment('Disease mapping history'),
		Index('med_icd_history_i_icdmid', 'icdmid'),
		Index('med_icd_history_i_icdeid_old', 'icdeid_old'),
		Index('med_icd_history_i_icdeid_new', 'icdeid_new'),
		Index('med_icd_history_i_entityid', 'entityid'),
		Index('med_icd_history_i_ticketid', 'ticketid'),
		Index('med_icd_history_i_uid', 'uid'),
		Index('med_icd_history_i_ts', 'ts'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				# FIXME
				'cap_menu'      : 'BASE_ADMIN',
				'cap_read'      : 'TICKETS_LIST',
				'cap_create'    : '__NOPRIV__',
				'cap_edit'      : '__NOPRIV__',
				'cap_delete'    : '__NOPRIV__',

				'menu_name'     : _('Disease History'),
				'default_sort'  : ({ 'property': 'ts' ,'direction': 'DESC' },),
				'grid_view'     : ('entity', 'ticket', 'event', 'ts', 'comment'),
				'form_view'     : (
					'entity', 'ticket',
					'event', 'ts',
					'type_old', 'type_new',
					'icdeid_old', 'icdeid_new',
					'comment'
				),
				'easy_search'   : ('comment',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
			}
		}
	)
	id = Column(
		'icdhid',
		UInt32(),
		Sequence('med_icd_history_icdhid_seq'),
		Comment('ICD mapping history ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	mapping_id = Column(
		'icdmid',
		UInt32(),
		ForeignKey('med_icd_mappings.icdmid', name='med_icd_history_fk_icdmid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('ICD entry mapping ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Mapping')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='med_icd_history_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		nullable=False,
		info={
			'header_string' : _('Entity')
		}
	)
	ticket_id = Column(
		'ticketid',
		UInt32(),
		ForeignKey('tickets_def.ticketid', name='med_icd_history_fk_ticketid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Ticket ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Ticket')
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='med_icd_history_fk_uid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('User'),
			'filter_type'   : 'none',
			'read_only'     : True
		}
	)
	event = Column(
		ICDHistoryEventType.db_type(),
		Comment('ICD history event type'),
		nullable=False,
		default=ICDHistoryEventType.created,
		server_default=ICDHistoryEventType.created,
		info={
			'header_string' : _('Event')
		}
	)
	timestamp = Column(
		'ts',
		TIMESTAMP(),
		Comment('ICD history event timestamp'),
		nullable=False,
		server_default=func.current_timestamp(),
		info={
			'header_string' : _('Time'),
			'read_only'     : True
		}
	)
	old_type = Column(
		'type_old',
		ICDMappingType.db_type(),
		Comment('Old ICD mapping type'),
		nullable=False,
		default=ICDMappingType.suspicion,
		server_default=ICDMappingType.suspicion,
		info={
			'header_string' : _('Old Type')
		}
	)
	new_type = Column(
		'type_new',
		ICDMappingType.db_type(),
		Comment('New ICD mapping type'),
		nullable=False,
		default=ICDMappingType.suspicion,
		server_default=ICDMappingType.suspicion,
		info={
			'header_string' : _('New Type')
		}
	)
	old_entry_id = Column(
		'icdeid_old',
		UInt32(),
		ForeignKey('med_icd_entries.icdeid', name='med_icd_history_fk_icdeid_old', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Old ICD entry ID'),
		nullable=False,
		info={
			'header_string' : _('Old Entry')
		}
	)
	new_entry_id = Column(
		'icdeid_new',
		UInt32(),
		ForeignKey('med_icd_entries.icdeid', name='med_icd_history_fk_icdeid_new', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('New ICD entry ID'),
		nullable=False,
		info={
			'header_string' : _('New Entry')
		}
	)
	comment = Column(
		UnicodeText(),
		Comment('New ICD mapping comment'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Comment')
		}
	)

	entity = relationship(
		'Entity',
		innerjoin=True,
		foreign_keys=(entity_id,),
		backref=backref(
			'disease_history',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	ticket = relationship(
		'Ticket',
		foreign_keys=(ticket_id,),
		backref=backref(
			'disease_history',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)
	user = relationship('User')
	old_entry = relationship(
		'ICDEntry',
		innerjoin=True,
		foreign_keys=(old_entry_id,)
	)
	new_entry = relationship(
		'ICDEntry',
		innerjoin=True,
		foreign_keys=(new_entry_id,)
	)

	def get_entity_history(self, req):
		sess = DBSession()
		loc = get_localizer(req)
		title = _('%s %s: %s')
		part1 = part2 = ''
		part3 = str(self.new_entry)

		if self.old_type == ICDMappingType.suspicion:
			part2 = _('probable diagnosis')
		elif self.old_type == ICDMappingType.history:
			part2 = _('past history')
		elif self.old_type == ICDMappingType.diagnosis:
			part2 = _('diagnosis')

		if self.old_type == self.new_type:
			if self.event == ICDHistoryEventType.created:
				part1 = _('Added')
			elif self.event == ICDHistoryEventType.modified:
				part1 = _('Changed')
			elif self.event == ICDHistoryEventType.deleted:
				part1 = _('Erased')
		else:
			if (self.old_type == ICDMappingType.suspicion) and (self.new_type == ICDMappingType.diagnosis):
				part1 = _('Confirmed')
			elif (self.old_type == ICDMappingType.diagnosis) and (self.new_type == ICDMappingType.suspicion):
				part1 = _('Contested')
			else:
				part1 = _('Changed')

		title = loc.translate(title) % (
			loc.translate(part1),
			loc.translate(part2),
			part3
		)
		eh = EntityHistory(
			self.entity,
			title,
			self.timestamp,
			None if (self.user is None) else str(self.user)
		)
		# ADD PARTS HERE
		if self.comment:
			eh.parts.append(EntityHistoryPart('tickets:comment', self.comment))
		return eh

