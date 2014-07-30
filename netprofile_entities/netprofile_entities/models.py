#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Entities module - Models
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
	'EntityType',
	'Entity',
	'EntityComment',
	'EntityFlag',
	'EntityFlagType',
	'Address',
	'PhoneType',
	'Phone',
	'EntityState',
	'EntityFile',
	'PhysicalEntity',
	'LegalEntity',
	'StructuralEntity',
	'ExternalEntity',

	'EntitiesBaseView'
]

import datetime as dt

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
	literal_column,
	func,
	select,
	text,
	or_
)

from sqlalchemy.orm import (
	backref,
	contains_eager,
	joinedload,
	relationship,
	validates
)

from sqlalchemy.ext.associationproxy import association_proxy

from netprofile.db.connection import (
	Base,
	DBSession
)
from netprofile.db.fields import (
	ASCIIString,
	DeclEnum,
	Int16,
	NPBoolean,
	UInt8,
	UInt16,
	UInt32,
	UInt64,
	npbool
)
from netprofile.db.ddl import (
	Comment,
	CurrentTimestampDefault,
	Trigger,
	View
)
from netprofile.db.util import (
	populate_related,
	populate_related_list
)
from netprofile.tpl import TemplateObject
from netprofile.ext.data import (
	ExtModel,
	_name_to_class
)
from netprofile.ext.columns import (
	HybridColumn,
	MarkupColumn
)
from netprofile.ext.filters import TextFilter
from netprofile_geo.models import (
	District,
	House,
	Street
)
from netprofile_geo.filters import AddressFilter
from netprofile.ext.wizards import (
	ExternalWizardField,
	SimpleWizard,
	Step,
	Wizard
)

from pyramid.threadlocal import get_current_request
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile_entities')

class EntityType(DeclEnum):
	"""
	Entity type ENUM.
	"""
	physical   = 'physical',   _('Physical'),   10
	legal      = 'legal',      _('Legal'),      20
	structural = 'structural', _('Structural'), 30
	external   = 'external',   _('External'),   40

def _wizcb_ent_generic_next(wiz, step, act, val, req):
	ret = {
		'do'      : 'goto',
		'goto'    : 'ent_physical1'
	}
	if 'etype' in val:
		ret.update({
			'goto'    : 'ent_%s1' % val['etype'],
			'enable'  : [
				st.id
				for st in wiz.steps
				if st.id.startswith('ent_' + val['etype'])
			],
			'disable' : [
				st.id
				for st in wiz.steps
				if st.id.startswith('ent_')
			]
		})
	return ret

def _wizcb_ent_submit(cls):
	def _wizcb_submit_hdl(wiz, step, act, val, req):
		xcls = cls
		if isinstance(xcls, str):
			xcls = _name_to_class(xcls)
		sess = DBSession()
		em = ExtModel(xcls)
		obj = xcls()
		em.set_values(obj, val, req, True)
		sess.add(obj)
		return {
			'do'     : 'close',
			'reload' : True
		}
	return _wizcb_submit_hdl

class Entity(Base):
	"""
	Base NetProfile entity type.
	"""

	DN_ATTR = 'cn'

	@classmethod
	def _filter_address(cls, query, value):
		if not isinstance(value, dict):
			return query
		if value.get('houseid'):
			val = int(value['houseid'])
			if val > 0:
				query = query.join(Address).filter(Address.house_id == val)
		elif value.get('streetid'):
			val = int(value['streetid'])
			if val > 0:
				query = query.join(Address).join(House).filter(House.street_id == val)
		elif value.get('districtid'):
			val = int(value['districtid'])
			if val > 0:
				query = query.join(Address).join(House).join(Street).filter(Street.district_id == val)
		elif value.get('cityid'):
			val = int(value['cityid'])
			if val > 0:
				query = query.join(Address).join(House).join(Street).filter(Street.city_id == val)
		return query

	@classmethod
	def _filter_phone(cls, query, value):
		if value:
			value = str(value)
			query = query.join(Phone).filter(Phone.number.contains(value))
		return query

	__tablename__ = 'entities_def'
	__table_args__ = (
		Comment('Entities'),
		Index('entities_def_i_parentid', 'parentid'),
		Index('entities_def_i_cby', 'cby'),
		Index('entities_def_i_mby', 'mby'),
		Index('entities_def_i_esid', 'esid'),
		Index('entities_def_i_nick', 'nick'),
		Index('entities_def_u_nt', 'etype', 'nick', unique=True),
		Trigger('after', 'insert', 't_entities_def_ai'),
		Trigger('after', 'update', 't_entities_def_au'),
		Trigger('after', 'delete', 't_entities_def_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES',
				'cap_read'      : 'ENTITIES_LIST',
				'cap_create'    : 'ENTITIES_CREATE',
				'cap_edit'      : 'ENTITIES_EDIT',
				'cap_delete'    : 'ENTITIES_DELETE',

				'tree_property' : 'children',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('Entities'),
				'menu_main'     : True,
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'nick' ,'direction': 'ASC' },),
				'grid_view'     : (
					MarkupColumn(
						name='icon',
						header_string='&nbsp;',
						help_text=_('Entity icon'),
						column_width=22,
						column_name=_('Icon'),
						column_resizable=False,
						cell_class='np-nopad',
						template='<img class="np-block-img" src="{grid_icon}" />'
					),
					'nick',
					MarkupColumn(
						name='object',
						header_string=_('Object'),
						column_flex=4,
						template=TemplateObject('netprofile_entities:templates/entity_nick.mak')
					),
					HybridColumn(
						'data',
						header_string=_('Information'),
						column_flex=5,
						template=TemplateObject('netprofile_entities:templates/entity_data.mak')
					),
					'state'
				),
				'easy_search'   : ('nick',),
				'extra_data'    : ('data', 'grid_icon'),
				'detail_pane'   : ('netprofile_entities.views', 'dpane_entities'),
				'extra_search'  : (
					TextFilter('phone', _filter_phone,
						title=_('Phone')
					),
					AddressFilter('address', _filter_address,
						title=_('Address')
					),
				),

				'create_wizard' : Wizard(
					Step(
						'nick', 'etype', 'parent',
						'state', 'flags', 'descr',
						id='generic', title=_('Generic entity properties'),
						on_next=_wizcb_ent_generic_next
					),
					Step(
						ExternalWizardField('PhysicalEntity', 'contractid'),
						ExternalWizardField('PhysicalEntity', 'name_family'),
						ExternalWizardField('PhysicalEntity', 'name_given'),
						ExternalWizardField('PhysicalEntity', 'name_middle'),
						id='ent_physical1', title=_('Physical entity properties'),
						on_prev='generic'
					),
					Step(
						ExternalWizardField('PhysicalEntity', 'pass_series'),
						ExternalWizardField('PhysicalEntity', 'pass_num'),
						ExternalWizardField('PhysicalEntity', 'pass_issuedby'),
						ExternalWizardField('PhysicalEntity', 'pass_issuedate'),
						ExternalWizardField('PhysicalEntity', 'email'),
						ExternalWizardField('PhysicalEntity', 'icq'),
						ExternalWizardField('PhysicalEntity', 'homepage'),
						ExternalWizardField('PhysicalEntity', 'birthdate'),
						id='ent_physical2', title=_('Physical entity properties'),
						on_submit=_wizcb_ent_submit('PhysicalEntity')
					),
					Step(
						ExternalWizardField('LegalEntity', 'contractid'),
						ExternalWizardField('LegalEntity', 'name'),
						ExternalWizardField('LegalEntity', 'homepage'),
						id='ent_legal1', title=_('Legal entity properties'),
						on_prev='generic'
					),
					Step(
						ExternalWizardField('LegalEntity', 'cp_name_family'),
						ExternalWizardField('LegalEntity', 'cp_name_given'),
						ExternalWizardField('LegalEntity', 'cp_name_middle'),
						ExternalWizardField('LegalEntity', 'cp_title'),
						ExternalWizardField('LegalEntity', 'cp_email'),
						ExternalWizardField('LegalEntity', 'cp_icq'),
						id='ent_legal2', title=_('Legal entity contact person')
					),
					Step(
						ExternalWizardField('LegalEntity', 'address_legal'),
						ExternalWizardField('LegalEntity', 'props_inn'),
						ExternalWizardField('LegalEntity', 'props_kpp'),
						ExternalWizardField('LegalEntity', 'props_bic'),
						ExternalWizardField('LegalEntity', 'props_rs'),
						ExternalWizardField('LegalEntity', 'props_cs'),
						ExternalWizardField('LegalEntity', 'props_bank'),
						id='ent_legal3', title=_('Legal entity details'),
						on_submit=_wizcb_ent_submit('LegalEntity')
					),
					Step(
						# FIXME?
						id='ent_structural1', title=_('Structural entity properties'),
						on_prev='generic',
						on_submit=_wizcb_ent_submit('StructuralEntity')
					),
					Step(
						ExternalWizardField('ExternalEntity', 'name'),
						ExternalWizardField('ExternalEntity', 'address'),
						id='ent_external1', title=_('External entity properties'),
						on_prev='generic',
						on_submit=_wizcb_ent_submit('ExternalEntity')
					),
					title=_('Add new entity'), validator='CreateEntity'
				)
			}
		}
	)
	id = Column(
		'entityid',
		UInt32(),
		Sequence('entities_def_entityid_seq'),
		Comment('Entity ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	parent_id = Column(
		'parentid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_def_fk_parentid', onupdate='CASCADE'),
		Comment('Parent entity ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Parent'),
			'filter_type'   : 'none'
		}
	)
	nick = Column(
		Unicode(255),
		Comment('Entity nickname'),
		nullable=False,
		info={
			'header_string' : _('Identifier'),
			'column_flex'   : 2
		}
	)
	state_id = Column(
		'esid',
		UInt32(),
		ForeignKey('entities_states.esid', name='entities_def_fk_esid', onupdate='CASCADE'),
		Comment('Entity state ID'),
		nullable=False,
		default=1,
		server_default=text('1'),
		info={
			'header_string' : _('State'),
			'filter_type'   : 'list'
		}
	)
	relative_dn = Column(
		'rdn',
		Unicode(255),
		Comment('Entity LDAP relative distinguished name'),
		nullable=False,
		info={
			'header_string' : _('LDAP RDN')
		}
	)
	type = Column(
		'etype',
		EntityType.db_type(),
		Comment('Entity type'),
		nullable=False,
		default=EntityType.physical,
		server_default=EntityType.physical,
		info={
			'header_string' : _('Type')
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
			'header_string' : _('Created')
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
			'header_string' : _('Modified')
		}
	)
	created_by_id = Column(
		'cby',
		UInt32(),
		ForeignKey('users.uid', name='entities_def_fk_cby', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Created by'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Created')
		}
	)
	modified_by_id = Column(
		'mby',
		UInt32(),
		ForeignKey('users.uid', name='entities_def_fk_mby', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Modified by'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Modified')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Entity description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : 'entity',
		'polymorphic_on'       : type,
		'with_polymorphic'     : '*'
	}

	state = relationship(
		'EntityState',
		innerjoin=True,
		backref='entities'
	)
	children = relationship(
		'Entity',
		backref=backref('parent', remote_side=[id])
	)
	created_by = relationship(
		'User',
		foreign_keys=created_by_id,
		backref='created_entities'
	)
	modified_by = relationship(
		'User',
		foreign_keys=modified_by_id,
		backref='modified_entities'
	)
	flagmap = relationship(
		'EntityFlag',
		backref=backref('entity', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	filemap = relationship(
		'EntityFile',
		backref=backref('entity', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	comments = relationship(
		'EntityComment',
		backref=backref('entity', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	addresses = relationship(
		'Address',
		backref=backref('entity', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	phones = relationship(
		'Phone',
		backref=backref('entity', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	flags = association_proxy(
		'flagmap',
		'type',
		creator=lambda v: EntityFlag(type=v)
	)
	files = association_proxy(
		'filemap',
		'file',
		creator=lambda v: EntityFile(file=v)
	)

	@classmethod
	def __augment_result__(cls, sess, res, params, req):
		populate_related(
			res, 'state_id', 'state', EntityState,
			sess.query(EntityState)
		)
		populate_related_list(
			res, 'id', 'flagmap', EntityFlag,
			sess.query(EntityFlag),
			None, 'entity_id'
		)
		populate_related_list(
			res, 'id', 'addresses', Address,
			sess.query(Address),
			None, 'entity_id'
		)
		return res

	@property
	def data(self):
		return {
			'flags' : [(ft.id, ft.name) for ft in self.flags]
		}

	def template_vars(self, req):
		return {
			'id'          : self.id,
			'nick'        : self.nick,
			'type'        : self.type,
			'description' : self.description,
			'state'       : {
				'id'   : self.state_id,
				'name' : str(self.state)
			},
			'flags'       : [(ft.id, ft.name) for ft in self.flags],
			'addresses'   : [{
				'id'          : a.id,
				'str'         : str(a),
				'primary'     : a.primary,
				'house'       : {
					'id'  : a.house_id,
					'str' : str(a.house)
				},
				'entrance'    : a.entrance,
				'floor'       : a.floor,
				'flat'        : a.flat,
				'entry_code'  : a.entry_code,
				'description' : a.description
			} for a in self.addresses],
			'phones'          : [{
				'id'          : p.id,
				'primary'     : p.primary,
				'type'        : p.type,
				'number'      : p.number,
				'description' : p.description
			} for p in self.phones]
		}

	def grid_icon(self, req):
		return req.static_url('netprofile_entities:static/img/entity.png')

	@validates('nick')
	def _set_nick(self, k, v):
		self.relative_dn = '%s=%s' % (self.DN_ATTR, str(v))
		return v

	def __str__(self):
		return '%s' % str(self.nick)

	def get_history(self, req, begin=None, end=None, category=None, max_num=20, sort=None, sdir=None):
		hcat = 'entities.history.get.%s' % ('all' if category is None else category)
		hist = []
		req.run_hook(
			hcat,
			hist, self, req, begin, end, max_num
		)
		if sort == 'title':
			sort_lambda = lambda x: x.title
		elif sort == 'author':
			sort_lambda = lambda x: '' if (x.author is None) else x.author
		else:
			sort_lambda = lambda x: x.time
		if sdir == 'DESC':
			sort_reverse = True
		else:
			sort_reverse = False
		hist = sorted(hist, key=sort_lambda, reverse=sort_reverse)
		if max_num is not None:
			hist = hist[:max_num]
		return hist

class EntityState(Base):
	"""
	NetProfile entity state.
	"""
	__tablename__ = 'entities_states'
	__table_args__ = (
		Comment('Entity states'),
		Index('entities_states_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES',
				'cap_read'      : 'ENTITIES_LIST',
				'cap_create'    : 'ENTITIES_STATES_CREATE',
				'cap_edit'      : 'ENTITIES_STATES_EDIT',
				'cap_delete'    : 'ENTITIES_STATES_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Entity States'),
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('name',),
				'form_view'     : ('name', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new entity state'))
			}
		}
	)
	id = Column(
		'esid',
		UInt32(),
		Sequence('entities_states_esid_seq'),
		Comment('Entity state ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Entity state name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Entity state description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	def __str__(self):
		return '%s' % str(self.name)

class EntityFlagType(Base):
	__tablename__ = 'entities_flags_types'
	__table_args__ = (
		Comment('Entity flag types'),
		Index('entities_flags_types_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES',
				'cap_read'      : 'ENTITIES_LIST',
				'cap_create'    : 'ENTITIES_FLAGTYPES_CREATE',
				'cap_edit'      : 'ENTITIES_FLAGTYPES_EDIT',
				'cap_delete'    : 'ENTITIES_FLAGTYPES_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Entity Flags'),
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('name',),
				'form_view'     : ('name', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new entity flag type'))
			}
		}
	)
	id = Column(
		'flagid',
		UInt32(),
		Sequence('entities_flags_types_flagid_seq'),
		Comment('Entity flag type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Entity flag type name'),
		nullable=False,
		info={
			'header_string' : _('Name')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Entity flag type description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	flagmap = relationship(
		'EntityFlag',
		backref=backref('type', innerjoin=True, lazy='joined'),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	entities = association_proxy(
		'flagmap',
		'entity',
		creator=lambda v: EntityFlag(entity=v)
	)

	def __str__(self):
		return '%s' % str(self.name)

class EntityFlag(Base):
	"""
	Many-to-many relationship object. Links entities and entity flags.
	"""
	__tablename__ = 'entities_flags_def'
	__table_args__ = (
		Comment('Entity flag mappings'),
		Index('entities_flags_def_u_ef', 'entityid', 'flagid', unique=True),
		Index('entities_flags_def_i_flagid', 'flagid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES',
				'cap_read'      : 'ENTITIES_LIST',
				'cap_create'    : 'ENTITIES_EDIT',
				'cap_edit'      : 'ENTITIES_EDIT',
				'cap_delete'    : 'ENTITIES_EDIT',

				'menu_name'     : _('Entity Flags')
			}
		}
	)
	id = Column(
		'efid',
		UInt32(),
		Sequence('entities_flags_def_efid_seq'),
		Comment('Entity flag ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_flags_def_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		nullable=False,
		info={
			'header_string' : _('Entity'),
			'filter_type'   : 'none'
		}
	)
	type_id = Column(
		'flagid',
		UInt32(),
		ForeignKey('entities_flags_types.flagid', name='entities_flags_types_fk_flagid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity flag type ID'),
		nullable=False,
		info={
			'header_string' : _('Type')
		}
	)

class AddressType(DeclEnum):
	"""
	Address type ENUM.
	"""
	home    = 'home', _('Home Address'),    10
	work    = 'work', _('Work Address'),    20
	postal  = 'post', _('Postal Address'),  30
	parcel  = 'parc', _('Parcel Address'),  40
	billing = 'bill', _('Billing Address'), 50

class Address(Base):
	"""
	Entity address.
	"""
	__tablename__ = 'addr_def'
	__table_args__ = (
		Comment('Addresses'),
		Index('addr_def_i_entityid', 'entityid'),
		Index('addr_def_i_houseid', 'houseid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES',
				'cap_read'      : 'ENTITIES_LIST',
				'cap_create'    : 'ENTITIES_EDIT',
				'cap_edit'      : 'ENTITIES_EDIT',
				'cap_delete'    : 'ENTITIES_EDIT',

				'menu_name'     : _('Addresses'),
				'default_sort'  : (
					{ 'property': 'houseid' ,'direction': 'ASC' },
					{ 'property': 'flat' ,'direction': 'ASC' }
				),
				'grid_view'     : ('entity', 'primary', 'atype', 'house', 'entrance', 'floor', 'flat', 'descr'),
				'form_view'     : ('entity', 'primary', 'atype', 'house', 'entrance', 'floor', 'flat', 'entrycode', 'postindex', 'descr'),
#				'easy_search'   : (),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new address'))
			}
		}
	)

	id = Column(
		'addrid',
		UInt32(),
		Sequence('addr_def_addrid_seq'),
		Comment('Address ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='addr_def_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		nullable=False,
		info={
			'header_string' : _('Entity'),
			'filter_type'   : 'none'
		}
	)
	type = Column(
		'atype',
		AddressType.db_type(),
		Comment('Address type'),
		nullable=False,
		default=AddressType.home,
		server_default=AddressType.home
	)
	primary = Column(
		NPBoolean(),
		Comment('Is address primary?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Primary')
		}
	)
	house_id = Column(
		'houseid',
		UInt32(),
		ForeignKey('addr_houses.houseid', name='addr_def_fk_houseid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('House ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('House'),
			'filter_type'   : 'none'
		}
	)
	entrance = Column(
		UInt8(),
		Comment('Entrance number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Entr.')
		}
	)
	floor = Column(
		Int16(),
		Comment('Floor number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Floor')
		}
	)
	flat = Column(
		UInt16(),
		Comment('Flat number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Flat')
		}
	)
	entry_code = Column(
		'entrycode',
		Unicode(8),
		Comment('Entry code'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Entry Code')
		}
	)
	postal_code = Column(
		'postindex',
		Unicode(8),
		Comment('Postal code'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Postal Code')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Address description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	house = relationship(
		'House',
		innerjoin=True,
		backref='addresses'
	)

	def __str__(self):
		req = get_current_request()
		loc = get_localizer(req)

		ret = []
		if self.house:
			ret.append(str(self.house))
		if self.entrance:
			ret.extend((
				loc.translate(_('entr.')),
				str(self.entrance)
			))
		if self.floor:
			ret.extend((
				loc.translate(_('fl.')),
				str(self.floor)
			))
		if self.flat:
			ret.extend((
				loc.translate(_('app.')),
				str(self.flat)
			))

		return ' '.join(ret)

class PhoneType(DeclEnum):
	"""
	Phone type ENUM.
	"""
	home  = 'home',  _('Home Phone'),   10
	cell  = 'cell',  _('Cell Phone'),   20
	work  = 'work',  _('Work Phone'),   30
	pager = 'pager', _('Pager Number'), 40
	fax   = 'fax',   _('Fax Number'),   50
	rec   = 'rec',   _('Receptionist'), 60

class Phone(Base):
	"""
	Generic telephone numbers.
	"""
	__tablename__ = 'addr_phones'
	__table_args__ = (
		Index('addr_def_i_entityid', 'entityid'),
		Index('addr_phones_i_num', 'num'),
		Comment('Phone numbers'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES',
				'cap_read'      : 'ENTITIES_LIST',
				'cap_create'    : 'ENTITIES_EDIT',
				'cap_edit'      : 'ENTITIES_EDIT',
				'cap_delete'    : 'ENTITIES_EDIT',

				'menu_name'     : _('Phones'),
				'default_sort'  : (
					{ 'property': 'ptype' ,'direction': 'ASC' },
					{ 'property': 'num' ,'direction': 'ASC' }
				),
				'grid_view'     : ('entity', 'primary', 'ptype', 'num', 'descr'),
#				'easy_search'   : (),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),

				'create_wizard' : SimpleWizard(title=_('Add new phone'))
			}
		}
	)

	id = Column(
		'phoneid',
		UInt32(),
		Sequence('addr_phones_phoneid_seq'),
		Comment('Phone ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='addr_phones_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		nullable=False,
		info={
			'header_string' : _('Entity'),
			'filter_type'   : 'none'
		}
	)
	primary = Column(
		NPBoolean(),
		Comment('Is phone primary?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Primary')
		}
	)
	type = Column(
		'ptype',
		PhoneType.db_type(),
		Comment('Phone type'),
		nullable=False,
		default=PhoneType.home,
		server_default=PhoneType.home
	)
	number = Column(
		'num',
		ASCIIString(255),
		Comment('Phone number'),
		nullable=False,
		info={
			'header_string' : _('Number')
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Phone description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	def __str__(self):
		req = get_current_request()
		loc = get_localizer(req)

		pfx = None
		if self.type == PhoneType.home:
			pfx = _('home')
		elif self.type == PhoneType.cell:
			pfx = _('cell')
		elif self.type == PhoneType.work:
			pfx = _('work')
		elif self.type == PhoneType.pager:
			pfx = _('pg.')
		elif self.type == PhoneType.fax:
			pfx = _('fax')
		elif self.type == PhoneType.rec:
			pfx = _('rec.')
		else:
			pfx = _('tel.')
		return '%s: %s' % (
			loc.translate(pfx),
			self.number
		)

	@property
	def data(self):
		img = 'phone_small'
		if self.type == PhoneType.cell:
			img = 'mobile_small'
		return {
			'img' : img,
			'str' : str(self)
		}

class EntityFile(Base):
	"""
	Many-to-many relationship object. Links entities and files from VFS.
	"""
	__tablename__ = 'entities_files'
	__table_args__ = (
		Comment('File mappings to entities'),
		Index('entities_files_u_efl', 'entityid', 'fileid', unique=True),
		Index('entities_files_i_fileid', 'fileid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES',
				'cap_read'      : 'ENTITIES_LIST',
				'cap_create'    : 'FILES_ATTACH_2ENTITIES',
				'cap_edit'      : 'FILES_ATTACH_2ENTITIES',
				'cap_delete'    : 'FILES_ATTACH_2ENTITIES',

				'menu_name'     : _('Files'),
				'grid_view'     : ('entity', 'file'),

				'create_wizard' : SimpleWizard(title=_('Attach file'))
			}
		}
	)
	id = Column(
		'efid',
		UInt32(),
		Sequence('entities_files_efid_seq'),
		Comment('Entity-file mapping ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_files_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		nullable=False,
		info={
			'header_string' : _('Entity'),
			'column_flex'   : 1
		}
	)
	file_id = Column(
		'fileid',
		UInt32(),
		ForeignKey('files_def.fileid', name='entities_files_fk_fileid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('File ID'),
		nullable=False,
		info={
			'header_string' : _('File'),
			'column_flex'   : 1
		}
	)

	file = relationship(
		'File',
		backref=backref(
			'linked_entities',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)

	def __str__(self):
		return '%s' % str(self.file)

class EntityComment(Base):
	"""
	Append-only text comments for entities.
	"""
	__tablename__ = 'entities_comments'
	__table_args__ = (
		Comment('Historic comments on entities'),
		Index('entities_comments_i_entityid', 'entityid'),
		Index('entities_comments_i_uid', 'uid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES',
				'cap_read'      : 'ENTITIES_LIST',
				'cap_create'    : 'ENTITIES_COMMENT',
				'cap_edit'      : 'ENTITIES_COMMENTS_EDIT',
				'cap_delete'    : 'ENTITIES_COMMENTS_DELETE',

				'menu_name'     : _('Comments'),
				'grid_view'     : ('entity', 'ts', 'user', 'text')
			}
		}
	)
	id = Column(
		'ecid',
		UInt32(),
		Sequence('entities_comments_ecid_seq'),
		Comment('Entity comment ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_comments_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		nullable=False,
		info={
			'header_string' : _('Entity')
		}
	)
	timestamp = Column(
		'ts',
		TIMESTAMP(),
		Comment('Time stamp'),
		CurrentTimestampDefault(),
		nullable=False,
#		default=zzz,
		info={
			'header_string' : _('Time')
		}
	)
	user_id = Column(
		'uid',
		UInt32(),
		ForeignKey('users.uid', name='entities_comments_fk_uid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('User ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('User')
		}
	)
	obsolete = Column(
		NPBoolean(),
		Comment('Is comment obsolete?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Obsolete'),
			'write_cap'     : 'ENTITIES_COMMENTS_MARK'
		}
	)
	text = Column(
		UnicodeText(),
		Comment('Entity comment text'),
		nullable=False,
		info={
			'header_string' : _('Text')
		}
	)

	user = relationship(
		'User',
		backref=backref(
			'entity_comments',
			passive_deletes=True
		)
	)

class Gender(DeclEnum):
	"""
	Basic gender ENUM.
	"""
	male           = 'M', _('Male'),           10
	female         = 'F', _('Female'),         20
	other          = 'O', _('Other'),          30
	not_applicable = 'N', _('Not applicable'), 40

class PhysicalEntity(Entity):
	"""
	Physical entity. Describes single individual.
	"""

	__tablename__ = 'entities_physical'
	__table_args__ = (
		Comment('Physical entities'),
		Index('entities_physical_u_contractid', 'contractid', unique=True),
		Index('entities_physical_i_name_family', 'name_family'),
		Index('entities_physical_i_name_given', 'name_given'),
		Trigger('before', 'insert', 't_entities_physical_bi'),
		Trigger('after', 'delete', 't_entities_physical_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES',
				'cap_read'      : 'ENTITIES_LIST',
				'cap_create'    : 'ENTITIES_CREATE',
				'cap_edit'      : 'ENTITIES_EDIT',
				'cap_delete'    : 'ENTITIES_DELETE',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('Physical entities'),
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'nick' ,'direction': 'ASC' },),
				'grid_view'     : (
					MarkupColumn(
						name='icon',
						header_string='&nbsp;',
						column_width=22,
						column_name=_('Icon'),
						column_resizable=False,
						cell_class='np-nopad',
						template='<img class="np-block-img" src="{grid_icon}" />'
					),
					'nick', 'name_family', 'name_given'
				),
				'form_view'     : (
					'nick', 'parent', 'state', 'flags', 'contractid',
					'name_family', 'name_given', 'name_middle',
#					'phones', 'addresses',
					'email', 'icq', 'homepage', 'birthdate',
					'pass_series', 'pass_num', 'pass_issuedate', 'pass_issuedby',
					'descr'
				),
				'easy_search'   : ('nick', 'name_family'),
				'extra_data'    : ('grid_icon',),
				'detail_pane'   : ('netprofile_entities.views', 'dpane_entities'),
				'extra_search'  : (
					TextFilter('phone', Entity._filter_phone,
						title=_('Phone')
					),
					AddressFilter('address', Entity._filter_address,
						title=_('Address')
					),
				),

				'create_wizard' : Wizard(
					Step(
						'nick', 'parent',
						'state', 'flags', 'descr',
						id='generic', title=_('Generic entity properties')
					),
					Step(
						'contractid',
						'name_family', 'name_given', 'name_middle',
						id='ent_physical1', title=_('Physical entity properties')
					),
#					Step(
#						'house', 'entrance', 'floor', 'flat',
#						id='ent_physical2', title=_('Physical entity properties')
#					),
					Step(
						'pass_series', 'pass_num', 'pass_issuedby', 'pass_issuedate',
						'email', 'icq', 'homepage', 'birthdate',
						id='ent_physical3', title=_('Physical entity properties')
					),
					title=_('Add new physical entity')
				)
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : EntityType.physical
	}
	id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_physical_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	contract_id = Column(
		'contractid',
		UInt32(),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Contract')
		}
	)
	name_family = Column(
		Unicode(255),
		Comment('Family name'),
		nullable=False,
		info={
			'header_string' : _('Family Name'),
			'column_flex'   : 3
		}
	)
	name_given = Column(
		Unicode(255),
		Comment('Given name'),
		nullable=False,
		info={
			'header_string' : _('Given Name'),
			'column_flex'   : 3
		}
	)
	name_middle = Column(
		Unicode(255),
		Comment('Middle name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Middle Name')
		}
	)
	gender = Column(
		Gender.db_type(),
		Comment('Gender'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Gender')
		}
	)
	email = Column(
		Unicode(64),
		Comment('External e-mail'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('E-mail'),
			'vtype'         : 'email'
		}
	)
	icq = Column(
		Unicode(64),
		Comment('ICQ UIN'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('ICQ')
		}
	)
	homepage = Column(
		Unicode(64),
		Comment('Homepage URL'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('URL'),
			'vtype'         : 'url'
		}
	)
	birthdate = Column(
		Date(),
		Comment('Birth date'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('DoB')
		}
	)
	passport_series = Column(
		'pass_series',
		Unicode(8),
		Comment('Passport series'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Pass. Series')
		}
	)
	passport_number = Column(
		'pass_num',
		Unicode(8),
		Comment('Passport number'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Pass. Number')
		}
	)
	passport_issued_by = Column(
		'pass_issuedby',
		Unicode(255),
		Comment('Passport issued by'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Pass. Issued By')
		}
	)
	passport_issue_date = Column(
		'pass_issuedate',
		Date(),
		Comment('Passport issue date'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Pass. Issue Date')
		}
	)

	def data(self, req):
		loc = get_localizer(req)

		ret = super(PhysicalEntity, self).data

		ret['addrs'] = []
		ret['phones'] = []
		for obj in self.addresses:
			ret['addrs'].append(str(obj))
		for obj in self.phones:
			ret['phones'].append(obj.data)
		return ret

	def template_vars(self, req):
		ret = super(PhysicalEntity, self).template_vars(req)
		ret.update({
			'contract_id'        : self.contract_id,
			'name_family'        : self.name_family,
			'name_given'         : self.name_given,
			'name_middle'        : self.name_middle,
			'email'              : self.email,
			'icq'                : self.icq,
			'homepage'           : self.homepage,
			'passport_series'    : self.passport_series,
			'passport_number'    : self.passport_number,
			'passport_issued_by' : self.passport_issued_by
		})
		# TODO: add birthdate, pass_issuedate
		return ret

	def grid_icon(self, req):
		return req.static_url('netprofile_entities:static/img/physical.png')

	def __str__(self):
		strs = []
		if self.name_family:
			strs.append(self.name_family)
		if self.name_given:
			strs.append(self.name_given)
		if self.name_middle:
			strs.append(self.name_middle)
		return ' '.join(strs)

class LegalEntity(Entity):
	"""
	Legal entity. Describes a company.
	"""

	__tablename__ = 'entities_legal'
	__table_args__ = (
		Comment('Legal entities'),
		Index('entities_legal_u_name', 'name', unique=True),
		Index('entities_legal_u_contractid', 'contractid', unique=True),
		Trigger('before', 'insert', 't_entities_legal_bi'),
		Trigger('after', 'delete', 't_entities_legal_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES',
				'cap_read'      : 'ENTITIES_LIST',
				'cap_create'    : 'ENTITIES_CREATE',
				'cap_edit'      : 'ENTITIES_EDIT',
				'cap_delete'    : 'ENTITIES_DELETE',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('Legal entities'),
				'menu_order'    : 20,
				'default_sort'  : ({ 'property': 'nick' ,'direction': 'ASC' },),
				'grid_view'     : (
					MarkupColumn(
						name='icon',
						header_string='&nbsp;',
						column_width=22,
						column_name=_('Icon'),
						column_resizable=False,
						cell_class='np-nopad',
						template='<img class="np-block-img" src="{grid_icon}" />'
					),
					'nick', 'name', 'cp_name_family', 'cp_name_given'
				),
				'form_view'     : (
					'nick', 'parent', 'state', 'flags', 'contractid',
					'name',
					'cp_name_family', 'cp_name_given', 'cp_name_middle', 'cp_title',
					'cp_email', 'cp_icq', 'homepage', 'address_legal',
					'props_inn', 'props_kpp', 'props_bic', 'props_rs', 'props_cs', 'props_bank',
					'descr'
				),
				'easy_search'   : ('nick', 'name'),
				'extra_data'    : ('grid_icon',),
				'detail_pane'   : ('netprofile_entities.views', 'dpane_entities'),
				'extra_search'  : (
					TextFilter('phone', Entity._filter_phone,
						title=_('Phone')
					),
					AddressFilter('address', Entity._filter_address,
						title=_('Address')
					),
				),

				'create_wizard' : Wizard(
					Step(
						'nick', 'parent',
						'state', 'flags', 'descr',
						id='generic', title=_('Generic entity properties')
					),
					Step(
						'contractid', 'name',
						'homepage',
						id='ent_legal1', title=_('Legal entity properties')
					),
					Step(
						'cp_name_family', 'cp_name_given', 'cp_name_middle',
						'cp_title',
						'cp_email', 'cp_icq',
						id='ent_legal2', title=_('Legal entity contact person')
					),
					Step(
						'address_legal',
						'props_inn', 'props_kpp',
						'props_bic', 'props_rs', 'props_cs', 'props_bank',
						id='ent_legal3', title=_('Legal entity details')
					),
					title=_('Add new legal entity')
				)
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : EntityType.legal
	}
	id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_legal_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	contract_id = Column(
		'contractid',
		UInt32(),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Contract')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Legal name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)
	contact_name_family = Column(
		'cp_name_family',
		Unicode(255),
		Comment('Contact person - family name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Family Name'),
			'column_flex'   : 3
		}
	)
	contact_name_given = Column(
		'cp_name_given',
		Unicode(255),
		Comment('Contact person - given name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Given Name'),
			'column_flex'   : 3
		}
	)
	contact_name_middle = Column(
		'cp_name_middle',
		Unicode(255),
		Comment('Contact person - middle name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Middle Name')
		}
	)
	contact_title = Column(
		'cp_title',
		Unicode(255),
		Comment('Contact person - title'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Title')
		}
	)
	contact_email = Column(
		'cp_email',
		Unicode(64),
		Comment('Contact person - e-mail'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('E-mail'),
			'vtype'         : 'email'
		}
	)
	contact_icq = Column(
		'cp_icq',
		Unicode(64),
		Comment('Contact person - ICQ UIN'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('ICQ')
		}
	)
	homepage = Column(
		Unicode(64),
		Comment('Homepage URL'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('URL'),
			'vtype'         : 'url'
		}
	)
	address_legal = Column(
		Unicode(255),
		Comment('Legal address'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Legal Addr.')
		}
	)
	props_inn = Column(
		Unicode(64),
		Comment('Properties - INN'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Taxpayer ID')
		}
	)
	props_kpp = Column(
		Unicode(64),
		Comment('Properties - KPP'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Tax Code')
		}
	)
	props_bic = Column(
		Unicode(64),
		Comment('Properties - BIC'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Bank ID')
		}
	)
	props_rs = Column(
		Unicode(64),
		Comment('Properties - R/S'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Acc. #')
		}
	)
	props_cs = Column(
		Unicode(64),
		Comment('Properties - C/S'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('C./acc. #')
		}
	)
	props_bank = Column(
		Unicode(255),
		Comment('Properties - bank'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Bank')
		}
	)

	def data(self, req):
		loc = get_localizer(req)

		ret = super(LegalEntity, self).data

		ret['addrs'] = []
		ret['phones'] = []
		for obj in self.addresses:
			ret['addrs'].append(str(obj))
		for obj in self.phones:
			ret['phones'].append(obj.data)
		return ret

	def grid_icon(self, req):
		return req.static_url('netprofile_entities:static/img/legal.png')

	def __str__(self):
		return str(self.name)

class StructuralEntity(Entity):
	"""
	Structural entity. Describes a building.
	"""

	__tablename__ = 'entities_structural'
	__table_args__ = (
		Comment('Structural entities'),
		Trigger('after', 'delete', 't_entities_structural_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES',
				'cap_read'      : 'ENTITIES_LIST',
				'cap_create'    : 'ENTITIES_CREATE',
				'cap_edit'      : 'ENTITIES_EDIT',
				'cap_delete'    : 'ENTITIES_DELETE',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('Structural entities'),
				'menu_order'    : 30,
				'default_sort'  : ({ 'property': 'nick' ,'direction': 'ASC' },),
				'grid_view'     : (
					MarkupColumn(
						name='icon',
						header_string='&nbsp;',
						column_width=22,
						column_name=_('Icon'),
						column_resizable=False,
						cell_class='np-nopad',
						template='<img class="np-block-img" src="{grid_icon}" />'
					),
					'nick'
				),
				'form_view'     : ('nick', 'parent', 'state', 'flags', 'descr'),
				'easy_search'   : ('nick',),
				'extra_data'    : ('grid_icon',),
				'detail_pane'   : ('netprofile_entities.views', 'dpane_entities'),
				'extra_search'  : (
					TextFilter('phone', Entity._filter_phone,
						title=_('Phone')
					),
					AddressFilter('address', Entity._filter_address,
						title=_('Address')
					),
				),

				'create_wizard' : Wizard(
					Step(
						'nick', 'parent',
						'state', 'flags', 'descr',
						id='generic', title=_('Generic entity properties')
					),
					Step(
						'house',
						id='ent_structural1', title=_('Structural entity properties')
					),
					title=_('Add new structural entity')
				)
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : EntityType.structural
	}
	id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_structural_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)

	@property
	def data(self):
		ret = super(StructuralEntity, self).data

		ret['addrs'] = []
		ret['phones'] = []
		for obj in self.addresses:
			ret['addrs'].append(str(obj))
		for obj in self.phones:
			ret['phones'].append(obj.data)
		return ret

	def grid_icon(self, req):
		return req.static_url('netprofile_entities:static/img/structural.png')

#	def __str__(self):
#		return ''
#		return str(self.house)

class ExternalEntity(Entity):
	"""
	External entity. Describes an object outside of geo database.
	"""

	__tablename__ = 'entities_external'
	__table_args__ = (
		Comment('External entities'),
		Trigger('after', 'delete', 't_entities_external_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_ENTITIES',
				'cap_read'      : 'ENTITIES_LIST',
				'cap_create'    : 'ENTITIES_CREATE',
				'cap_edit'      : 'ENTITIES_EDIT',
				'cap_delete'    : 'ENTITIES_DELETE',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('External entities'),
				'menu_order'    : 40,
				'default_sort'  : ({ 'property': 'nick' ,'direction': 'ASC' },),
				'grid_view'     : (
					MarkupColumn(
						name='icon',
						header_string='&nbsp;',
						column_width=22,
						column_name=_('Icon'),
						column_resizable=False,
						cell_class='np-nopad',
						template='<img class="np-block-img" src="{grid_icon}" />'
					),
					'nick', 'name', 'address'
				),
				'form_view'     : (
					'nick', 'parent', 'state', 'flags',
					'name', 'address', 'descr'
				),
				'easy_search'   : ('nick', 'name'),
				'extra_data'    : ('grid_icon',),
				'detail_pane'   : ('netprofile_entities.views', 'dpane_entities'),

				'create_wizard' : Wizard(
					Step(
						'nick', 'parent',
						'state', 'flags', 'descr',
						id='generic', title=_('Generic entity properties')
					),
					Step(
						'name', 'address',
						id='ent_external1', title=_('External entity properties')
					),
					title=_('Add new external entity')
				)
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : EntityType.external
	}
	id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='entities_external_fk_entityid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Entity ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Entity name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)
	address = Column(
		Unicode(255),
		Comment('Entity address'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Address'),
			'column_flex'   : 3
		}
	)

	@property
	def data(self):
		ret = super(ExternalEntity, self).data
		if self.address:
			ret['address'] = str(self.address)
		return ret

	def grid_icon(self, req):
		return req.static_url('netprofile_entities:static/img/external.png')

	def __str__(self):
		return str(self.name)

class EntityHistory(object):
	def __init__(self, ent, title, time=None, author=None):
		self.entity = ent
		self.title = title
		if time is None:
			self.time = dt.datetime.now()
		else:
			self.time = time
		self.author = author
		self.parts = []

	def __json__(self, req=None):
		return {
			'title'  : self.title,
			'author' : self.author,
			'time'   : self.time,
			'parts'  : [x.__json__(req) for x in self.parts]
		}

class EntityHistoryPart(object):
	def __init__(self, icon, text):
		self.icon = icon
		self.text = text

	def __str__(self):
		return str(self.text)

	def __json__(self, req=None):
		return {
			'icon' : self.icon,
			'text' : self.text
		}

EntitiesBaseView = View(
	'entities_base',
	DBSession.query(
		Entity.id.label('entityid'),
		literal_column('NULL').label('parentid'),
		Entity.nick.label('nick'),
		Entity.state_id.label('esid'),
		Entity.relative_dn.label('rdn'),
		Entity.type.label('etype'),
		Entity.creation_time.label('ctime'),
		Entity.modification_time.label('mtime'),
		Entity.created_by_id.label('cby'),
		Entity.modified_by_id.label('mby'),
		Entity.description.label('descr')
	).select_from(Entity.__table__).filter(Entity.parent_id == None),
	check_option='CASCADED'
)

