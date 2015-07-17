#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Entities module - Models
# © Copyright 2013-2015 Alex 'Unik' Unigovsky
# © Copyright 2014 Sergey Dikunov
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
	'DeviceTypeCategory',
	'DeviceTypeManufacturer',
	'DeviceMetatypeField',

	'DeviceTypeFlagType',
	'DeviceTypeFlag',

	'DeviceTypeFile',

	'DeviceType',
	'SimpleDeviceType',
	'NetworkDeviceType',

	'DeviceFlagType',
	'DeviceFlag',

	'Device',
	'SimpleDevice',
	'NetworkDevice',

	'SNMPTypeField',
	'SNMPV3SchemeField',
	'SNMPV3ProtoField',
	'SNMPV3PrivProtoField',
	'SNMPV3MgmtTypeField'
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

_ = TranslationStringFactory('netprofile_devices')

class DeviceMetatypeField(DeclEnum):
	"""
	Device metatype ENUM.
	"""
	simple  = 'simple',  _('Simple'),  10
	network = 'network', _('Network'), 20

class DeviceTypeManufacturer(Base):
	"""
	Device manufacturer.
	"""
	__tablename__ = 'devices_types_mfct'
	__table_args__ = (
		Comment('Device type manufacturers'),
		Index('devices_types_mfct_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICETYPES_LIST',
				'cap_create'    : 'DEVICETYPES_MANUFACTURERS_CREATE',
				'cap_edit'      : 'DEVICETYPES_MANUFACTURERS_EDIT',
				'cap_delete'    : 'DEVICETYPES_MANUFACTURERS_DELETE',
				'menu_name'     : _('Manufacturers'),
				'show_in_menu'  : 'admin',
				'default_sort'  : ({ 'property': 'sname' ,'direction': 'ASC' },),
				'grid_view'     : ('dtmid', 'sname', 'name'),
				'grid_hidden'   : ('dtmid',),
				'form_view'     : ('sname', 'name', 'website'),
				'easy_search'   : ('sname', 'name'),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new device manufacturer'))
			}
		}
	)
	id = Column(
		'dtmid',
		UInt32(),
		Sequence('devices_types_mfct_dtmid_seq'),
		Comment('Device type manufacturer ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	short_name = Column(
		'sname',
		Unicode(48),
		Comment('Device type manufacturer short name'),
		nullable=False,
		info={
			'header_string' : _('Short Name'),
			'column_flex'   : 2
		}
	)
	name = Column(
		Unicode(255),
		Comment('Device type manufacturer name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)
	website = Column(
		Unicode(255),
		Comment('Device type manufacturer website URL'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('URL')
		}
	)

	def __str__(self):
		return "%s" % str(self.name)

class DeviceFlagType(Base):
	"""
	Device flag type.
	"""
	__tablename__ = 'devices_flags_types'
	__table_args__ = (
		Comment('Device flag types'),
		Index('devices_flags_types_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICES_LIST',
				'cap_create'    : 'DEVICES_FLAGTYPES_CREATE',
				'cap_edit'      : 'DEVICES_FLAGTYPES_EDIT',
				'cap_delete'    : 'DEVICES_FLAGTYPES_DELETE',
				'menu_name'     : _('Device Flags'),
				'show_in_menu'  : 'admin',
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('dftid', 'name'),
				'grid_hidden'   : ('dftid',),
				'form_view'     : ('name', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new device flag type'))
			}
		}
	)
	id = Column(
		'dftid',
		UInt32(),
		Sequence('devices_flags_types_dftid_seq'),
		Comment('Device flag type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Device flag type name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Device flag type description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	flagmap = relationship(
		'DeviceFlag',
		backref=backref('type', innerjoin=True, lazy='joined'),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	devices = association_proxy(
		'flagmap',
		'device',
		creator=lambda v: DeviceFlag(device=v)
	)

	def __str__(self):
		return "%s" % str(self.name)

class DeviceTypeFlagType(Base):
	"""
	Device type flag type.
	"""
	__tablename__ = 'devices_types_flags_types'
	__table_args__ = (
		Comment('Device type flag types'),
		Index('devices_types_flags_types_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICETYPES_LIST',
				'cap_create'    : 'DEVICETYPES_FLAGTYPES_CREATE',
				'cap_edit'      : 'DEVICETYPES_FLAGTYPES_EDIT',
				'cap_delete'    : 'DEVICETYPES_FLAGTYPES_DELETE',
				'menu_name'     : _('Type Flags'),
				'show_in_menu'  : 'admin',
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('dtftid', 'name'),
				'grid_hidden'   : ('dtftid',),
				'form_view'     : ('name', 'descr'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new device type flag type'))
			}
		}
	)
	id = Column(
		'dtftid',
		UInt32(),
		Sequence('devices_types_flags_types_dtftid_seq'),
		Comment('Device type flag type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Device type flag type name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Device type flag type description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)

	flagmap = relationship(
		'DeviceTypeFlag',
		backref=backref('flag_type', innerjoin=True, lazy='joined'),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	device_types = association_proxy(
		'flagmap',
		'device_type',
		creator=lambda v: DeviceTypeFlag(device_type=v)
	)

	def __str__(self):
		return "%s" % str(self.name)

class DeviceTypeFlag(Base):
	"""
	Many-to-many relationship object. Links device types and device type flags.
	"""
	__tablename__ = 'devices_types_flags_def'
	__table_args__ = (
		Comment('Device type flags'),
		Index('devices_types_flags_def_u_dtf', 'dtid', 'dtftid', unique=True),
		Index('devices_types_flags_def_i_dtftid', 'dtftid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICETYPES_LIST',
				'cap_create'    : 'DEVICETYPES_EDIT',
				'cap_edit'      : 'DEVICETYPES_EDIT',
				'cap_delete'    : 'DEVICETYPES_EDIT',

				'menu_name'     : _('Flags')
			}
		}
	)
	id = Column(
		'dtfid',
		UInt32(),
		Sequence('devices_types_flags_def_dtfid_seq'),
		Comment('Device type flag ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	device_type_id = Column(
		'dtid',
		UInt32(),
		ForeignKey('devices_types_def.dtid', name='devices_types_flags_def_fk_dtid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Device type ID'),
		nullable=False,
		info={
			'header_string' : _('Device Type'),
			'filter_type'   : 'none'
		}
	)
	flag_type_id = Column(
		'dtftid',
		UInt32(),
		ForeignKey('devices_types_flags_types.dtftid', name='devices_types_flags_def_fk_dtftid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Device type flag type ID'),
		nullable=False,
		info={
			'header_string' : _('Type'),
			'filter_type'   : 'list'
		}
	)

class DeviceTypeCategory(Base):
	"""
	Device category.
	"""
	__tablename__ = 'devices_types_cats'
	__table_args__ = (
		Comment('Device categories'),
		Index('devices_types_cats_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICETYPES_LIST',
				'cap_create'    : 'DEVICETYPES_CATEGORIES_CREATE',
				'cap_edit'      : 'DEVICETYPES_CATEGORIES_EDIT',
				'cap_delete'    : 'DEVICETYPES_CATEGORIES_DELETE',
				'menu_name'     : _('Categories'),
				'show_in_menu'  : 'admin',
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('dtcid', 'name'),
				'grid_hidden'   : ('dtcid',),
				'form_view'     : ('name',),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new device category'))
			}
		}
	)
	id = Column(
		'dtcid',
		UInt32(),
		Sequence('devices_types_cats_dtcid_seq'),
		Comment('Device type category ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Device type category name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 1
		}
	)

	def __str__(self):
		return "%s" % str(self.name)

class DeviceType(Base):
	"""
	Abstract device type.
	"""
	__tablename__ = 'devices_types_def'
	__table_args__ = (
		Comment('Device types'),
		Index('devices_types_def_u_dt', 'dtmid', 'name', unique=True),
		Index('devices_types_def_i_dtcid', 'dtcid'),
		#TODO ADD TRIGGERS HERE
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICETYPES_LIST',
				'cap_create'    : 'DEVICETYPES_CREATE',
				'cap_edit'      : 'DEVICETYPES_EDIT',
				'cap_delete'    : 'DEVICETYPES_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Types'),

				#TODO HERE WIZARD AND VIEW CUSTOMIZATION
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('dtid', 'category', 'manufacturer', 'name'),
				'grid_hidden'   : ('dtid',),
				'form_view'     : ('category', 'manufacturer', 'name', 'descr', 'flags'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
#				'create_wizard' : SimpleWizard(title=_('Add new device type'))
			}
		}
	)
	id = Column(
		'dtid',
		UInt32(),
		Sequence('devices_types_def_dtid_seq'),
		Comment('Device type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	manufacturer_id = Column(
		'dtmid',
		UInt32(),
		ForeignKey('devices_types_mfct.dtmid', name='devices_types_def_fk_dtmid', onupdate='CASCADE'),
		Comment('Device type manufacturer ID'),
		nullable=False,
		info={
			'header_string' : _('Manufacturer'),
			'filter_type'   : 'list',
			'column_flex'   : 2
		}
	)
	category_id = Column(
		'dtcid',
		UInt32(),
		ForeignKey('devices_types_cats.dtcid', name='devices_types_def_fk_dtcid', onupdate='CASCADE'),
		Comment('Device type category ID'),
		nullable=False,
		info={
			'header_string' : _('Category'),
			'filter_type'   : 'list',
			'column_flex'   : 2
		}
	)
	type = Column(
		'dtype',
		DeviceMetatypeField.db_type(),
		Comment('Device metatype'),
		nullable=False,
		default=DeviceMetatypeField.simple,
		server_default=DeviceMetatypeField.simple,
		info={
			'header_string' : _('Type')
		}
	)
	name = Column(
		Unicode(255),
		Comment('Device type name'),
		nullable=False,
		info={
			'header_string' : _('Name'),
			'column_flex'   : 3
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Device type description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : 'deviceType',
		'polymorphic_on'       : type,
		'with_polymorphic'     : '*'
	}

	manufacturer = relationship(
		'DeviceTypeManufacturer',
		innerjoin=True,
		backref='device_types'
	)
	category = relationship(
		'DeviceTypeCategory',
		innerjoin=True,
		backref='device_types'
	)
	flagmap = relationship(
		'DeviceTypeFlag',
		backref=backref('device_type', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)
	filemap = relationship(
		'DeviceTypeFile',
		backref=backref('device_type', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	flags = association_proxy(
		'flagmap',
		'flag_type',
		creator=lambda v: DeviceTypeFlag(flag_type=v)
	)
	files = association_proxy(
		'filemap',
		'file',
		creator=lambda v: DeviceTypeFile(file=v)
	)

	# @classmethod
	# def __augment_result__(cls, sess, res, params, req):
	# 	#TODO THIS SECTION
	# 	populate_related(
	# 		res, 'dtmid', 'manufacturer', DeviceTypeManufacturer,
	# 		sess.query(DeviceTypeManufacturer)
	# 	)
	# 	populate_related(
	# 		res, 'dtcid', 'category', DeviceTypeCategory,
	# 		sess.query(DeviceTypeCategory)
	# 	)
	# 	populate_related_list(
	# 		res, 'id', 'flagmap', DeviceTypeFlag,
	# 		sess.query(DeviceTypeFlag),
	# 		None, 'device_type_id'
	# 	)
	# 	return res
	#
	# def template_vars(self, req):
	# 	#TODO THIS SECTION
	# 	return {
	# 		'id'          : self.id,
	# 		'manufacturer': {
	# 			'id'	: self.dtmid,
	# 			'name'	: str(self.manufacturer)
	# 		},
	# 		'category': {
	# 			'id'	: self.dtcid,
	# 			'name'	: str(self.category)
	# 		},
	# 		'flags'       : [(ft.id, ft.name) for ft in self.flags],
	# 		'type'		: self.type,
	# 		'name'		: self.name,
	# 		'descr'		: self.descr
	# 	}

	def __str__(self):
		return '%s %s' % (
			str(self.manufacturer.short_name or self.manufacturer.name),
			str(self.name)
		)

class SimpleDeviceType(DeviceType):
	"""
	Simple device type.
	"""
	__tablename__ = 'devices_types_simple'
	__table_args__ = (
		Comment('Simple device types'),
		#TODO Trigger('after', 'delete', 't_devices_types_simple_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICETYPES_LIST',
				'cap_create'    : 'DEVICETYPES_CREATE',
				'cap_edit'      : 'DEVICETYPES_EDIT',
				'cap_delete'    : 'DEVICETYPES_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Simple Devices'),
				'menu_parent'   : 'devicetype',

				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('dtid', 'category', 'manufacturer', 'name'),
				'grid_hidden'   : ('dtid',),
				'form_view'     : ('category', 'manufacturer', 'name', 'descr', 'flags'),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new simple device type'))
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : DeviceMetatypeField.simple
	}
	id = Column(
		'dtid',
		UInt32(),
		ForeignKey('devices_types_def.dtid', name='devices_types_simple_fk_dtid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Device type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)

	#TODO THIS SECTION
	# def grid_icon(self, req):
	# 	return req.static_url('netprofile_entities:static/img/structural.png')

class NetworkDeviceType(DeviceType):
	"""
	Network device type.
	"""
	__tablename__ = 'devices_types_network'
	__table_args__ = (
		Comment('Network device types'),
		#TODO Trigger('after', 'delete', 't_devices_types_network_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICETYPES_LIST',
				'cap_create'    : 'DEVICETYPES_CREATE',
				'cap_edit'      : 'DEVICETYPES_EDIT',
				'cap_delete'    : 'DEVICETYPES_DELETE',

				'show_in_menu'  : 'admin',
				'menu_name'     : _('Network Devices'),
				'menu_parent'   : 'devicetype',

				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'     : ('dtid', 'category', 'manufacturer', 'name', 'manageable', 'modular'),
				'grid_hidden'   : ('dtid',),
				'form_view'     : (
					'category', 'manufacturer',
					'name', 'descr', 'flags',
					'manageable', 'modular',
					'icon', 'handler'
				),
				'easy_search'   : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new network device type'))
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : DeviceMetatypeField.network
	}
	id = Column(
		'dtid',
		UInt32(),
		ForeignKey('devices_types_def.dtid', name='devices_types_network_fk_dtid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Device type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	manageable = Column(
		NPBoolean(),
		Comment('Is manageable?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Manageable')
		}
	)
	modular = Column(
		NPBoolean(),
		Comment('Is modular/slotted/chassis?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Modular')
		}
	)
	icon = Column(
		ASCIIString(16),
		Comment('Schematic icon name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Icon')
		}
	)
	handler = Column(
		ASCIIString(255),
		Comment('Device handler class'),
		nullable=True,
		default='NPNetworkDeviceHandler',
		server_default='NPNetworkDeviceHandler',
		info={
			'header_string' : _('Handler')
		}
	)

class Device(Base):
	"""
	Abstract device.
	"""
	__tablename__ = 'devices_def'
	__table_args__ = (
		Comment('Devices'),
		Index('devices_def_i_dtid', 'dtid'),
		Index('devices_def_i_placeid', 'placeid'),
		Index('devices_def_i_entityid', 'entityid'),
		Index('devices_def_i_cby', 'cby'),
		Index('devices_def_i_mby', 'mby'),
		Index('devices_def_i_iby', 'iby'),
		{
			#TODO THIS SECTION
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICES_LIST',
				'cap_create'    : 'DEVICES_CREATE',
				'cap_edit'      : 'DEVICES_EDIT',
				'cap_delete'    : 'DEVICES_DELETE',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('Devices'),
				'menu_main'     : True,
				'default_sort'  : ({ 'property': 'serial' ,'direction': 'ASC' },),
				'grid_view'     : ('did', 'device_type', 'serial', 'place', 'entity', 'oper'),
				'grid_hidden'   : ('did',),
				'form_view'     : (
					'device_type', 'serial',
					'place', 'entity', 'oper',
					'ctime', 'created_by',
					'mtime', 'modified_by',
					'itime', 'installed_by',
					'descr'
				),
				'easy_search'   : ('serial',),
				# 'extra_data'    : ('grid_icon',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
#				'create_wizard' : SimpleWizard(title=_('Add new device'))
			}
		}
	)
	id = Column(
		'did',
		UInt32(),
		Sequence('devices_def_did_seq'),
		Comment('Device ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	serial = Column(
		Unicode(64),
		Comment('Device serial'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Serial'),
			'column_flex'   : 1
		}
	)
	device_type_id = Column(
		'dtid',
		UInt32(),
		ForeignKey('devices_types_def.dtid', name='devices_def_fk_dtid', onupdate='CASCADE'),
		Comment('Device type ID'),
		nullable=False,
		info={
			'header_string' : _('Type'),
			'filter_type'   : 'list',
			'column_flex'   : 2
		}
	)
	type = Column(
		'dtype',
		DeviceMetatypeField.db_type(),
		Comment('Device metatype shortcut'),
		nullable=False,
		default=DeviceMetatypeField.simple,
		server_default=DeviceMetatypeField.simple,
		info={
			'header_string' : _('Type') # this is never shown to the user, so repeating header is irrelevant
		}
	)
	operational = Column(
		'oper',
		NPBoolean(),
		Comment('Is operational?'),
		nullable=False,
		default=False,
		server_default=npbool(False),
		info={
			'header_string' : _('Operational')
		}
	)
	place_id = Column(
		'placeid',
		UInt32(),
		ForeignKey('addr_places.placeid', name='devices_def_fk_placeid', onupdate='CASCADE'),
		Comment('Place ID'),
		nullable=False,
		info={
			'header_string' : _('Place'),
			'filter_type'   : 'list',
			'column_flex'   : 1
		}
	)
	entity_id = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='devices_def_fk_entityid', onupdate='CASCADE', ondelete='SET NULL'),
		Comment('Owner\'s entity ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Entity'),
			'filter_type'   : 'none',
			'column_flex'   : 1
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
		info={
			'header_string' : _('Modified'),
			'read_only'     : True
		}
	)
	installation_time = Column(
		'itime',
		TIMESTAMP(),
		Comment('Installation timestamp'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Installed'),
			'read_only'     : True
		}
	)
	created_by_id = Column(
		'cby',
		UInt32(),
		ForeignKey('users.uid', name='devices_def_fk_cby', ondelete='SET NULL', onupdate='CASCADE'),
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
		ForeignKey('users.uid', name='devices_def_fk_mby', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Modified by'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Modified'),
			'read_only'     : True
		}
	)
	installed_by_id = Column(
		'iby',
		UInt32(),
		ForeignKey('users.uid', name='devices_def_fk_iby', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Installed by'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Installed'),
			'read_only'     : True
		}
	)
	description = Column(
		'descr',
		UnicodeText(),
		Comment('Device description'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Description')
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : 'device',
		'polymorphic_on'       : type,
		'with_polymorphic'     : '*'
	}

	place = relationship(
		'Place',
		innerjoin=True,
		backref='devices'
	)
	entity = relationship(
		'Entity',
		backref=backref(
			'devices',
			passive_deletes=True
		)
	)
	created_by = relationship(
		'User',
		foreign_keys=created_by_id,
		backref='created_devices'
	)
	modified_by = relationship(
		'User',
		foreign_keys=modified_by_id,
		backref='modified_devices'
	)
	installed_by = relationship(
		'User',
		foreign_keys=installed_by_id,
		backref='installed_devices'
	)
	device_type = relationship(
		'DeviceType',
		innerjoin=True,
		backref='devices'
	)
	flagmap = relationship(
		'DeviceFlag',
		backref=backref('device', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	flags = association_proxy(
		'flagmap',
		'type',
		creator=lambda v: DeviceFlag(type=v)
	)

	# @classmethod
	# def __augment_result__(cls, sess, res, params, req):
	# 	#TODO THIS SECTION
	# 	from netprofile_geo.models import Place
	# 	from netprofile_entities.models import Entity
	#
	# 	populate_related(
	# 		res, 'dtid', 'device_type', DeviceType,
	# 		sess.query(DeviceType)
	# 	)
	# 	populate_related(
	# 		res, 'placeid', 'place', Place,
	# 		sess.query(Place)
	# 	)
	# 	populate_related(
	# 		res, 'entityid', 'entity', Entity,
	# 		sess.query(Entity)
	# 	)
	# 	#TODO user cby,mby,iby add
	#
	# 	populate_related_list(
	# 		res, 'id', 'flagmap', DeviceFlag,
	# 		sess.query(DeviceFlag),
	# 		None, 'device_id'
	# 	)
	# 	return res
	#
	# @property
	# def data(self):
	# 	#TODO THIS SECTION
	# 	return {
	# 		'flags' : [(ft.id, ft.name) for ft in self.flags]
	# 	}
	#
	# def template_vars(self, req):
	# 	#TODO THIS SECTION
	# 	return {
	# 		'id'          : self.id,
	# 		'serial'      : self.serial,
	# 		'device_type' : {
	# 			'id'   : self.dtid,
	# 			'name' : str(self.device_type)
	# 		},
	# 		'type'        : self.dtype,
	# 		'oper'        : self.oper,
	# 		'place'       : {
	# 			'id'	: self.placeid,
	# 			'name'  : str(self.place)
	# 		},
	# 		'entity'       : {
	# 			'id'	: self.entityid,
	# 			'name'  : str(self.entity)
	# 		},
	# 		'ctime'		: self.ctime,
	# 		'mtime'		: self.mtime,
	# 		'itime'		: self.itime,
	# 		'created_by'	: {
	# 			'id'	: self.created_by_id,
	# 			'name'  : str(self.created_by)
	# 		},
	# 		'modified_by'	: {
	# 			'id'	: self.modified_by_id,
	# 			'name'  : str(self.modified_by)
	# 		},
	# 		'installed_by'	: {
	# 			'id'	: self.installed_by_id,
	# 			'name'  : str(self.installed_by)
	# 		},
	# 		'description' : self.descr
	# 	}

	# def grid_icon(self, req):
	# 	return req.static_url('netprofile_devices:static/img/device.png')

	def __str__(self):
		if self.serial:
			return '%s: S/N %s' % (
				str(self.device_type),
				str(self.serial)
			)
		return '%s @%s' % (
			str(self.device_type),
			str(self.place)
		)

class DeviceFlag(Base):
	"""
	Many-to-many relationship object. Links devices and device flags.
	"""
	__tablename__ = 'devices_flags_def'
	__table_args__ = (
		Comment('Device flags'),
		Index('devices_flags_def_u_df', 'did', 'dftid', unique=True),
		Index('devices_flags_def_i_dftid', 'dftid'),
		{
			#TODO THIS SECTION
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICES_LIST',
				'cap_create'    : 'DEVICES_EDIT',
				'cap_edit'      : 'DEVICES_EDIT',
				'cap_delete'    : 'DEVICES_EDIT',

				'menu_name'     : _('Flags')
			}
		}
	)
	id = Column(
		'dfid',
		UInt32(),
		Sequence('devices_flags_def_dfid_seq'),
		Comment('Device flag ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	device_id = Column(
		'did',
		UInt32(),
		ForeignKey('devices_def.did', name='devices_flags_def_fk_did', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Device ID'),
		nullable=False,
		info={
			'header_string' : _('Device'),
			'filter_type'   : 'none'
		}
	)
	type_id = Column(
		'dftid',
		UInt32(),
		ForeignKey('devices_flags_types.dftid', name='devices_flags_def_fk_dftid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Device flag type ID'),
		nullable=False,
		info={
			'header_string' : _('Type'),
			'filter_type'   : 'list'
		}
	)

class SimpleDevice(Device):
	"""
	Simple device.
	"""

	__tablename__ = 'devices_simple'
	__table_args__ = (
		Comment('Simple devices'),
		#TODO Trigger('after', 'delete', 't_devices_simple_ad'),
		{
			#TODO THIS SECTION
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICES_LIST',
				'cap_create'    : 'DEVICES_CREATE',
				'cap_edit'      : 'DEVICES_EDIT',
				'cap_delete'    : 'DEVICES_DELETE',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('Simple Devices'),
				'default_sort'  : ({ 'property': 'serial' ,'direction': 'ASC' },),
				'grid_view'     : ('did', 'device_type', 'serial', 'place', 'entity', 'oper'),
				'grid_hidden'   : ('did',),
				'form_view'     : (
					'device_type', 'serial',
					'place', 'entity', 'oper',
					'ctime', 'created_by',
					'mtime', 'modified_by',
					'itime', 'installed_by',
					'descr'
				),
				'easy_search'   : ('serial',),
				# 'extra_data'    : ('grid_icon',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new simple device'))
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : DeviceMetatypeField.simple
	}
	id = Column(
		'did',
		UInt32(),
		ForeignKey('devices_def.did', name='devices_simple_fk_did', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Device ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)

	#TODO THIS SECTION
	# @property
	# def data(self):
	# 	ret = super(SimpleDeviceType, self).data
	#
	# 	ret['addrs'] = []
	# 	ret['phones'] = []
	# 	for obj in self.addresses:
	# 		ret['addrs'].append(str(obj))
	# 	for obj in self.phones:
	# 		ret['phones'].append(obj.data)
	# 	return ret
	#
	# def grid_icon(self, req):
	# 	return req.static_url('netprofile_devices:static/img/simple.png')

class SNMPTypeField(DeclEnum):
	"""
	SNMP type ENUM.
	"""
	v1	= 'v1',  _('Version 1'), 10
	v2c	= 'v2c', _('Version 2'), 20
	v3	= 'v3',  _('Version 3'), 30

class SNMPV3SchemeField(DeclEnum):
	"""
	SNMP security level ENUM.
	"""
	noAuthNoPriv = 'noAuthNoPriv', _('NoAuthNoPriv'), 10
	authNoPriv   = 'authNoPriv',   _('AuthNoPriv'),   20
	authPriv     = 'authPriv',     _('AuthPriv'),     30

class SNMPV3ProtoField(DeclEnum):
	"""
	SNMP authentication protocol ENUM.
	"""
	md5	= 'MD5', _('MD5'), 10
	sha	= 'SHA', _('SHA'), 20

class SNMPV3PrivProtoField(DeclEnum):
	"""
	SNMP privacy protocol ENUM.
	"""
	des    = 'DES',    _('DES'),    10
	aes128 = 'AES128', _('AES128'), 20
	aes192 = 'AES192', _('AES192'), 30
	aes256 = 'AES256', _('AES256'), 40

class SNMPV3MgmtTypeField(DeclEnum):
	"""
	Management access type ENUM.
	"""
	ssh    = 'ssh',    _('SSH'),    10
	telnet = 'telnet', _('Telnet'), 20
	vnc    = 'vnc',    _('VNC'),    30
	rdp    = 'rdp',    _('RDP'),    40

class NetworkDevice(Device):
	"""
	Network device.
	"""
	__tablename__ = 'devices_network'
	__table_args__ = (
		Comment('Network devices'),
		#TODO Trigger('after', 'delete', 't_devices_network_ad'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICES_LIST',
				'cap_create'    : 'DEVICES_CREATE',
				'cap_edit'      : 'DEVICES_EDIT',
				'cap_delete'    : 'DEVICES_DELETE',

				'show_in_menu'  : 'modules',
				'menu_name'     : _('Network Devices'),
				'default_sort'  : ({ 'property': 'serial' ,'direction': 'ASC' },),
				'grid_view'     : ('did', 'device_type', 'serial', 'place', 'entity', 'host', 'oper'),
				'grid_hidden'   : ('did',),
				'form_view'     : (
					'device_type', 'serial',
					'place', 'entity', 'host', 'oper',
					'snmptype', 'cs_ro', 'cs_rw',
					'v3user', 'v3scheme',
					'v3authproto', 'v3authpass',
					'v3privproto', 'v3privpass',
					'mgmttype', 'mgmtuser', 'mgmtpass', 'mgmtepass',
					'ctime', 'created_by',
					'mtime', 'modified_by',
					'itime', 'installed_by',
					'descr'
				),
				'easy_search'   : ('serial',),
				# 'extra_data'    : ('grid_icon',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new network device'))
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : DeviceMetatypeField.network
	}
	id = Column(
		'did',
		UInt32(),
		ForeignKey('devices_def.did', name='devices_network_fk_did', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Device ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	host_id = Column(
		'hostid',
		UInt32(),
		ForeignKey('hosts_def.hostid', name='devices_network_fk_hostid', ondelete='SET NULL', onupdate='CASCADE'),
		Comment('Host ID'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Host'),
			'filter_type'   : 'none',
			'column_flex'   : 2
		}
	)
	snmp_type = Column(
		'snmptype',
		SNMPTypeField.db_type(),
		Comment('SNMP access type'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('SNMP Version'),
			'read_cap'      : 'DEVICES_PASSWORDS',
			'write_cap'     : 'DEVICES_PASSWORDS'
		}
	)
	snmp_ro_community = Column(
		'cs_ro',
		ASCIIString(255),
		Comment('SNMPv2 read-only community'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('R/O Community'),
			'read_cap'      : 'DEVICES_PASSWORDS',
			'write_cap'     : 'DEVICES_PASSWORDS'
		}
	)
	snmp_rw_community = Column(
		'cs_rw',
		ASCIIString(255),
		Comment('SNMPv2 read-write community'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('R/W Community'),
			'read_cap'      : 'DEVICES_PASSWORDS',
			'write_cap'     : 'DEVICES_PASSWORDS'
		}
	)
	snmp_v3_user = Column(
		'v3user',
		ASCIIString(255),
		Comment('SNMPv3 user name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('SNMPv3 User'),
			'read_cap'      : 'DEVICES_PASSWORDS',
			'write_cap'     : 'DEVICES_PASSWORDS'
		}
	)
	snmp_v3_scheme = Column(
		'v3scheme',
		SNMPV3SchemeField.db_type(),
		Comment('SNMPv3 security level'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('SNMPv3 Security Level'),
			'read_cap'      : 'DEVICES_PASSWORDS',
			'write_cap'     : 'DEVICES_PASSWORDS'
		}
	)
	snmp_v3_auth_protocol = Column(
		'v3authproto',
		SNMPV3ProtoField.db_type(),
		Comment('SNMPv3 authentication protocol'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('SNMPv3 Authentication Protocol'),
			'read_cap'      : 'DEVICES_PASSWORDS',
			'write_cap'     : 'DEVICES_PASSWORDS'
		}
	)
	snmp_v3_auth_passphrase = Column(
		'v3authpass',
		ASCIIString(255),
		Comment('SNMPv3 authentication passphrase'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('SNMPv3 Authentication Passphrase'),
			'read_cap'      : 'DEVICES_PASSWORDS',
			'write_cap'     : 'DEVICES_PASSWORDS'
		}
	)
	snmp_v3_privacy_protocol = Column(
		'v3privproto',
		SNMPV3PrivProtoField.db_type(),
		Comment('SNMPv3 privacy protocol'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('SNMPv3 Privacy Protocol'),
			'read_cap'      : 'DEVICES_PASSWORDS',
			'write_cap'     : 'DEVICES_PASSWORDS'
		}
	)
	snmp_v3_privacy_passphrase = Column(
		'v3privpass',
		ASCIIString(255),
		Comment('SNMPv3 privacy passphrase'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('SNMPv3 Privacy Passphrase'),
			'read_cap'      : 'DEVICES_PASSWORDS',
			'write_cap'     : 'DEVICES_PASSWORDS'
		}
	)
	management_type = Column(
		'mgmttype',
		SNMPV3MgmtTypeField.db_type(),
		Comment('Management access type'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Management Type'),
			'read_cap'      : 'DEVICES_PASSWORDS',
			'write_cap'     : 'DEVICES_PASSWORDS'
		}
	)
	management_user = Column(
		'mgmtuser',
		Unicode(255),
		Comment('Management user name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Management User'),
			'read_cap'      : 'DEVICES_PASSWORDS',
			'write_cap'     : 'DEVICES_PASSWORDS'
		}
	)
	management_password = Column(
		'mgmtpass',
		Unicode(255),
		Comment('Management password'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Management Password'),
			'read_cap'      : 'DEVICES_PASSWORDS',
			'write_cap'     : 'DEVICES_PASSWORDS'
		}
	)
	management_enable_password = Column(
		'mgmtepass',
		Unicode(255),
		Comment('Management enable password'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Management Enable Password'),
			'read_cap'      : 'DEVICES_PASSWORDS',
			'write_cap'     : 'DEVICES_PASSWORDS'
		}
	)

	host = relationship(
		'Host',
		innerjoin=True,
		backref='network_devices'
	)

	def __str__(self):
		if self.host:
			return '%s: %s' % (
				str(self.device_type),
				str(self.host)
			)
		return super(NetworkDevice, self).__str__()

	# def grid_icon(self, req):
	# 	return req.static_url('netprofile_devices:static/img/network.png')

class DeviceTypeFile(Base):
	"""
	Many-to-many relationship object. Links device types and files from VFS.
	"""
	__tablename__ = 'devices_types_files'
	__table_args__ = (
		Comment('File mappings to devices types'),
		Index('devices_types_files_u_dtfl', 'dtid', 'fileid', unique=True),
		Index('devices_types_files_i_fileid', 'fileid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICETYPES_LIST',
				'cap_create'    : 'FILES_ATTACH_2DEVICETYPES',
				'cap_edit'      : '__NOPRIV__',
				'cap_delete'    : 'FILES_ATTACH_2DEVICETYPES',

				'menu_name'     : _('Files'),
				'grid_view'     : ('device_type', 'file'),

				'create_wizard' : SimpleWizard(title=_('Attach file'))
			}
		}
	)
	id = Column(
		'dtfid',
		UInt32(),
		Sequence('deveices_types_files_dtfid_seq'),
		Comment('DeviceType-file mapping ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	device_type_id = Column(
		'dtid',
		UInt32(),
		ForeignKey('devices_types_def.dtid', name='devices_types_files_fk_dtid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Device type ID'),
		nullable=False,
		info={
			'header_string' : _('Device Type'),
			'column_flex'   : 1
		}
	)
	file_id = Column(
		'fileid',
		UInt32(),
		ForeignKey('files_def.fileid', name='devices_types_files_fk_fileid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('File ID'),
		nullable=False,
		info={
			'header_string' : _('File'),
			'column_flex'   : 1,
			'editor_xtype'  : 'fileselect'
		}
	)

	file = relationship(
		'File',
		backref=backref(
			'linked_device_types',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)

	def __str__(self):
		return '%s' % str(self.file)

