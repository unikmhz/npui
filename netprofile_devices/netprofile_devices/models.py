#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Entities module - Models
# © Copyright 2013-2014 Alex 'Unik' Unigovsky
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
	'DeviceCategory',
	'DeviceManufacturer',
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
	simple = 'simple', _('Simple'),   10
	network = 'network', _('Network'), 20

#TODO rename to DeviceTypeManufacturer
class DeviceManufacturer(Base):
	"""
	NetProfile device manufacturer definition
	"""
	__tablename__ = 'devices_types_mfct'
	__table_args__ = (
		Comment('Device Type Manufacturers'),
		Index('devices_types_mfct_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICES_LIST',
				'cap_create'    : 'DEVICETYPES_MANUFACTURERS_CREATE',
				'cap_edit'      : 'DEVICETYPES_MANUFACTURERS_EDIT',
				'cap_delete'    : 'DEVICETYPES_MANUFACTURERS_DELETE',
				'menu_name'    : _('Device Manufacturers'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 30,
				'default_sort' : ({ 'property': 'sname' ,'direction': 'ASC' },),
				'grid_view'    : ('sname', 'name', 'website'),
				'form_view'    : ('sname', 'name', 'website'),
				'easy_search'  : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new device manufacturer'))
				}
			}
		)
	id = Column(
		'dtmid',
		UInt32(),
		Sequence('dtmid_seq'),
		Comment('Device Type Manufacturer ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	sname = Column(
		'sname',
		Unicode(48),
		Comment('Device Manufacturer Short Name'),
		nullable=False,
		info={
			'header_string' : _('Short Name')
			}
		)
	name = Column(
		'name',
		Unicode(255),
		Comment('Device Type Manufacturer Name'),
		nullable=False,
		info={
			'header_string' : _('Name')
			}
		)
	website = Column(
		'website',
		Unicode(255),
		Comment('Device Type Manufacturer Website URL'),
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
	NetProfile devices flag type definition
	"""
	__tablename__ = 'devices_flags_types'
	__table_args__ = (
		Comment('Devices Flag Types'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICES_LIST',
				'cap_create'    : 'DEVICES_FLAGTYPES_CREATE',
				'cap_edit'      : 'DEVICES_FLAGTYPES_EDIT',
				'cap_delete'    : 'DEVICES_FLAGTYPES_DELETE',
				'menu_name'    : _('Device flag types'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 10,
				'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('name', 'descr'),
				'form_view'    : ('name', 'descr'),
				'easy_search'  : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new device flag type'))
				}
			}
		)

	id = Column(
		'dftid',
		UInt32(),
		Sequence('dftid_seq'),
		Comment('Device Flag Type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	name = Column(
		'name',
		Unicode(255),
		Comment('Device Flag Type Name'),
		nullable=False,
		info={
			'header_string' : _('Name')
			}
		)
	descr = Column(
		'descr',
		UnicodeText(),
		Comment('Device Flag Type Description'),
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
	NetProfile devices type flag type definition
	"""
	__tablename__ = 'devices_types_flags_types'
	__table_args__ = (
		Comment('Devices Types Flag Types'),
		Index('devices_types_flags_types_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICES_LIST',
				'cap_create'    : 'DEVICETYPES_FLAGTYPES_CREATE',
				'cap_edit'      : 'DEVICETYPES_FLAGTYPES_EDIT',
				'cap_delete'    : 'DEVICETYPES_FLAGTYPES_DELETE',
				'menu_name'    : _('Device type flag types'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 20,
				'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('name', 'descr'),
				'form_view'    : ('name', 'descr'),
				'easy_search'  : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new device type flag type'))

				}
			}
		)

	id = Column(
		'dtftid',
		UInt32(),
		Sequence('dtftid_seq'),
		Comment('Device Type Flag Type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	name = Column(
		'name',
		Unicode(255),
		Comment('Device Type Flag Type Name'),
		nullable=False,
		info={
			'header_string' : _('Name')
			}
		)
	descr = Column(
		'descr',
		UnicodeText(),
		Comment('Description'),
		info={
			'header_string' : _('Description')
			}
		)

	flagmap = relationship(
		'DeviceTypeFlag',
		backref=backref('type', innerjoin=True, lazy='joined'),
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
	Many-to-many relationship object. Links deviceTypes and deviceTypes flags.
	"""
	__tablename__ = 'devices_types_flags_def'
	__table_args__ = (
		Comment('DeviceType flag mappings'),
		Index('devices_types_flags_def_u_ef', 'devicetypeid', 'flagid', unique=True),
		Index('devices_types_flags_def_i_flagid', 'flagid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICETYPES_LIST',
				'cap_create'    : 'DEVICETYPES_EDIT',
				'cap_edit'      : 'DEVICETYPES_EDIT',
				'cap_delete'    : 'DEVICETYPES_EDIT',

				'menu_name'     : _('Device Type Flags')
			}
		}
	)
	id = Column(
		'id',
		UInt32(),
		Sequence('devices_types_flags_def_id_seq'),
		Comment('Device Type flag ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	device_type_id = Column(
		'devicetypeid',
		UInt32(),
		ForeignKey('devices_types_def.dtid', name='devices_types_flags_def_fk_devicetypeid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Device Type ID'),
		nullable=False,
		info={
			'header_string' : _('Device Type'),
			'filter_type'   : 'none'
		}
	)
	type_id = Column(
		'flagid',
		UInt32(),
		ForeignKey('devices_types_flags_types.dtftid', name='devices_types_flags_types_fk_dtftid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Device Type flag type ID'),
		nullable=False,
		info={
			'header_string' : _('Type')
		}
	)

#TODO rename to DeviceTypeCategory
class DeviceCategory(Base):
	"""
	NetProfile device category definition
	"""
	__tablename__ = 'devices_types_cats'
	__table_args__ = (
		Comment('Device Categories'),
		Index('devices_types_cats_u_name', 'name', unique=True),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICES_CATEGORIES_LIST',
				'cap_create'    : 'DEVICES_CATEGORIES_CREATE',
				'cap_edit'      : 'DEVICES_CATEGORIES_EDIT',
				'cap_delete'    : 'DEVICES_CATEGORIES_DELETE',
				'menu_name'    : _('Device categories'),
				'show_in_menu'  : 'admin',
				'menu_order'    : 40,
				'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view' : ('name',),
				'form_view' : ('name',),
				'easy_search' : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new device category'))
				}
			}
		)
	id = Column(
		'dtcid',
		UInt32(),
		Sequence('dtcid_seq'),
		Comment('Device Type Category ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	name = Column(
		'name',
		Unicode(255),
		Comment('Device Type Category Name'),
		nullable=False,
		info={
			'header_string' : _('Name')
			}
		)

	def __str__(self):
		return "%s" % str(self.name)


class DeviceType(Base):
	"""
	NetProfile device type definition
	"""
	__tablename__ = 'devices_types_def'
	__table_args__ = (
		Comment('Device Types'),
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

#				'show_in_menu'  : 'admin',
#				'menu_name'    : _('Device types'),
#				'menu_order'    : 50,

#				'tree_property' : 'children',
#				'menu_main'     : True,

				#TODO HERE WIZARD AND VIEW CUSTOMIZATION
				'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('category', 'manufacturer', 'name', 'descr'),
				'form_view'    : ('category', 'manufacturer', 'name', 'descr','flags','files'),
				'easy_search'  : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
#				'create_wizard' : SimpleWizard(title=_('Add new device type'))
			}
		}
	)

	id = Column(
		'dtid',
		UInt32(),
		Sequence('dtid_seq'),
		Comment('Device Type ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	dtmid = Column(
		'dtmid',
		UInt32(),
		ForeignKey('devices_types_mfct.dtmid', name='devices_types_def_fk_dtmid', onupdate='CASCADE'),
		Comment('Device Manufacturer ID'),
		nullable=False,
		info={
			'header_string' : _('Device Manufacturer'),
			'filter_type'   : 'list'
			}
		)
	dtcid = Column(
		'dtcid',
		UInt32(),
		ForeignKey('devices_types_cats.dtcid', name='devices_types_def_fk_dtcid', onupdate='CASCADE'),
		Comment('Device Category ID'),
		nullable=False,
		info={
			'header_string' : _('Device Category')
			}
		)
	type = Column(
		'dtype',
		DeviceMetatypeField.db_type(),
		Comment('Device type'),
		nullable=False,
		default=DeviceMetatypeField.simple,
		server_default=DeviceMetatypeField.simple,
		info={
			'header_string' : _('Type')
		}
	)
	name = Column(
		'name',
		Unicode(255),
		Comment('Device Type Name'),
		nullable=False,
		info={
			'header_string' : _('Device Type')
			}
		)
	descr = Column(
		'descr',
		UnicodeText(),
		Comment('Device Type Description'),
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
		'DeviceManufacturer',
		innerjoin=True,
		backref='device_types'
	)

	category = relationship(
		'DeviceCategory',
		innerjoin=True,
		backref='device_types'
	)

	flagmap = relationship(
		'DeviceTypeFlag',
		backref=backref('entity', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
	)

	flags = association_proxy(
		'flagmap',
		'type',
		creator=lambda v: DeviceTypeFlag(type = v)
	)

	filemap = relationship(
		'DeviceTypeFile',
		backref=backref('device_type', innerjoin=True),
		cascade='all, delete-orphan',
		passive_deletes=True
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
	# 		res, 'dtmid', 'manufacturer', DeviceManufacturer,
	# 		sess.query(DeviceManufacturer)
	# 	)
	# 	populate_related(
	# 		res, 'dtcid', 'category', DeviceCategory,
	# 		sess.query(DeviceCategory)
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
		return "%s" % str(self.name)


class SimpleDeviceType(DeviceType):
	"""
	Simple device type.
	"""

	__tablename__ = 'devices_types_simple'
	__table_args__ = (
		Comment('Simple Device Types'),
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
				'menu_name'     : _('Simple Device types'),
				'menu_order'    : 60,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('category', 'manufacturer', 'name', 'descr'),
				'form_view'    : ('category', 'manufacturer', 'name', 'descr','flags','files'),
				'easy_search'  : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new simple device type'))
			}
		}
	)
	id = Column(
		'id',
		UInt32(),
		ForeignKey('devices_types_def.dtid', name='devices_types_simple_def_fk_dtid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('DeviceType ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)

	__mapper_args__ = {
		'polymorphic_identity' : DeviceMetatypeField.simple
	}

	#TODO THIS SECTION
	# def grid_icon(self, req):
	# 	return req.static_url('netprofile_entities:static/img/structural.png')

class NetworkDeviceType(DeviceType):
	"""
	Network device type.
	"""

	__tablename__ = 'devices_types_network'
	__table_args__ = (
		Comment('Network Device Types'),
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
				'menu_name'     : _('Network Device types'),
				'menu_order'    : 70,

				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('category', 'manufacturer',
								  'name', 'descr',
								  'manageable','modular','icon','handler'),
				'form_view'    : ('category', 'manufacturer', 'name', 'descr',
								  'flags','files',
								'manageable','modular','icon','handler'),
				'easy_search'  : ('name',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new network device type'))
			}
		}
	)
	id = Column(
		'id',
		UInt32(),
		ForeignKey('devices_types_def.dtid', name='devices_types_network_def_fk_dtid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('DeviceType ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)

	manageable = Column(
		'manageable',
		NPBoolean(),
		Comment('Is Manageable?'),
		nullable=False,
		default=False,
		info={
			'header_string' : _('Is Manageable?')
			}
		)

	modular = Column(
		'modular',
		NPBoolean(),
		Comment('Is Modular?'),
		nullable=False,
		default=False,
		info={
			'header_string' : _('Is Modular?')
			}
		)

	icon = Column(
		'icon',
		Unicode(16),
		Comment('Device icon'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Icon')
			}
		)

	handler = Column(
		'handler',
		Unicode(255),
		Comment('Device handler'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Handler')
			}
		)

	__mapper_args__ = {
		'polymorphic_identity' : DeviceMetatypeField.network
	}


class Device(Base):
	"""
	NetProfile device definition
	"""
	__tablename__ = 'devices_def'
	__table_args__ = (
		Comment('Devices'),
		Index('device_def_i_dtid', 'dtid'),
		Index('device_def_i_placeid', 'placeid'),
		Index('device_def_i_entityid', 'entityid'),
		Index('device_def_i_cby', 'cby'),
		Index('device_def_i_mby', 'mby'),
		Index('device_def_i_iby', 'iby'),
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

				'tree_property' : 'children',

				'show_in_menu'  : 'modules',
				'menu_name'    : _('Devices'),
				'menu_main'     : True,
				'menu_order'    : 5,
				'default_sort' : ({ 'property': 'serial' ,'direction': 'ASC' },),
				'grid_view'    : ('device_type', 'serial', 'entity', 'descr'),
				'form_view'    : ('device_type',
								  'serial',
								  'oper',
								  'place',
								  'entity',
								  'created_by',
								  'modified_by',
								  'installed_by',
								  'ctime',
								  'mtime',
								  'itime',
								  'descr'),
				'easy_search'  : ('device_type',),
				# 'extra_data'    : ('grid_icon',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
#				'create_wizard' : SimpleWizard(title=_('Add new device'))
				}
			}
		)
	id = Column(
		'did',
		UInt32(),
		Sequence('did_seq'),
		Comment('Device ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
			}
		)
	serial = Column(
		'serial',
		Unicode(64),
		Comment('Device serial'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('Serial')
			}
		)
	dtid = Column(
		'dtid',
		UInt32(),
		ForeignKey('devices_types_def.dtid', name='devices_def_fk_dtid', onupdate='CASCADE'),
		Comment('Device Type ID'),
		nullable=False,
		info={
			'header_string' : _('Type'),
			'filter_type'   : 'list'
			}
		)
	dtype = Column(
		'dtype',
		DeviceMetatypeField.db_type(),
		Comment('Device Metatype Shortcut'),
		nullable=False,
		default=DeviceMetatypeField.simple,
		info={
			'header_string' : _('Metatype')
			}
		)
	oper = Column(
		'oper',
		NPBoolean(),
		Comment('Is Operational?'),
		nullable=False,
		default=False,
		info={
			'header_string' : _('Is Operational?')
			}
		)
	placeid = Column(
		'placeid',
		UInt32(),
		ForeignKey('addr_places.placeid', name='devices_def_fk_placeid', onupdate='CASCADE'),
		Comment('Place ID'),
		nullable=False,
		info={
			'header_string' : _('Place')
			}
		)
	entityid = Column(
		'entityid',
		UInt32(),
		ForeignKey('entities_def.entityid', name='devices_def_fk_entityid', onupdate='CASCADE', ondelete='SET NULL'),
		Comment('Entity ID'),
		nullable=True,
		info={
			'header_string' : _('Entity')
			}
		)
	ctime = Column(
		'ctime',
		TIMESTAMP(),
		Comment('Creation time'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Created'),
			# 'read_only'     : True
			}
		)
	mtime = Column(
		'mtime',
		TIMESTAMP(),
		Comment('Modification time'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Modified'),
			# 'read_only'     : True
			}
		)
	itime = Column(
		'itime',
		TIMESTAMP(),
		Comment('Installation time'),
		nullable=True,
		default=None,
		server_default=FetchedValue(),
		info={
			'header_string' : _('Installed'),
			# 'read_only'     : True
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
			'header_string' : _('Created')
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
			'header_string' : _('Modified')
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
			'header_string' : _('Installed')
			}
		)
	descr = Column(
		'descr',
		UnicodeText(),
		Comment('Device Description'),
		info={
			'header_string' : _('Description')
			}
		)

	place = relationship(
		'Place',
		innerjoin=True,
		backref='deviceplaces'
	)

	entity = relationship(
		'Entity',
		innerjoin=True,
		backref='deviceentities'
	)

	created_by = relationship(
		'User',
		foreign_keys=created_by_id,
		backref='devicecreated'
	)

	modified_by = relationship(
		'User',
		foreign_keys=modified_by_id,
		backref='devicemodified'
	)

	installed_by = relationship(
		'User',
		foreign_keys=installed_by_id,
		backref='deviceinstalled'
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
		creator=lambda v: DeviceFlag(type = v)
	)

	__mapper_args__ = {
		'polymorphic_identity' : 'device',
		'polymorphic_on'       : dtype,
		'with_polymorphic'     : '*'
	}

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
		return str(self.serial)


class DeviceFlag(Base):
	"""
	Many-to-many relationship object. Links devices and device flags.
	"""
	__tablename__ = 'devices_flags_def'
	__table_args__ = (
		Comment('Device flag mappings'),
		Index('devices_flags_def_u_ef', 'deviceid', 'flagid', unique=True),
		Index('devices_flags_def_i_flagid', 'flagid'),
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

				'menu_name'     : _('Device Flags')
			}
		}
	)
	id = Column(
		'id',
		UInt32(),
		Sequence('devices_flags_def_id_seq'),
		Comment('Device flag ID'),
		primary_key=True,
		nullable=False,
		info={
			'header_string' : _('ID')
		}
	)
	device_id = Column(
		'deviceid',
		UInt32(),
		ForeignKey('devices_def.did', name='devices_flags_def_fk_deviceid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Device ID'),
		nullable=False,
		info={
			'header_string' : _('Device'),
			'filter_type'   : 'none'
		}
	)
	type_id = Column(
		'flagid',
		UInt32(),
		ForeignKey('devices_flags_types.dftid', name='devices_flags_types_fk_dftid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('Device flag type ID'),
		nullable=False,
		info={
			'header_string' : _('Type')
		}
	)


class SimpleDevice(Device):
	"""
	Simple device.
	"""

	__tablename__ = 'devices_simple'
	__table_args__ = (
		Comment('Simple Device'),
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
				'menu_order'    : 10,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('device_type', 'serial', 'entity', 'descr'),
				'form_view'    : ('device_type',
								  'serial',
								  'oper',
								  'place',
								  'entity',
								  'created_by',
								  'modified_by',
								  'installed_by',
								  'ctime',
								  'mtime',
								  'itime',
								  'descr'),
				'easy_search'  : ('device_type',),
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
			ForeignKey('devices_def.did', name='devices_simple_def_fk_did', ondelete='CASCADE', onupdate='CASCADE'),
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
	SNMP Type ENUM.
	"""
	v1	= 'v1', _('Version 1'),   10
	v2c	= 'v2c', _('Version 2'), 20
	v3	= 'v3', _('Version 3'), 30

class SNMPV3SchemeField(DeclEnum):
	"""
	SNMP Connection level ENUM.
	"""
	noAuthNoPriv	= 'noAuthNoPriv', _('NoAuthNoPriv'),   10
	authNoPriv		= 'authNoPriv', _('AuthNoPriv'), 20
	authPriv		= 'authPriv', _('AuthPriv'), 30

class SNMPV3ProtoField(DeclEnum):
	"""
	SNMP Auth Protocol ENUM.
	"""
	md5	= 'md5', _('MD5'), 10
	sha	= 'sha', _('SHA'), 20

class SNMPV3PrivProtoField(DeclEnum):
	"""
	SNMP Crypt protocol ENUM.
	"""
	des = 'des', _('DES'),   10
	aes128 = 'aes128', _('AES128'), 20
	aes192 = 'aes192', _('AES192'), 30
	aes256 = 'aes256', _('AES256'), 40

class SNMPV3MgmtTypeField(DeclEnum):
	"""
	Management Access Type.
	"""
	ssh = 'ssh', _('SSH'),   10
	telnet = 'telnet', _('Telnet'), 20
	vnc = 'vnc', _('VNC'), 30
	rdp = 'rdp', _('RDP'), 40

class NetworkDevice(Device):
	"""
	Network device.
	"""

	__tablename__ = 'devices_network'
	__table_args__ = (
		Comment('Network Devices'),
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
				'menu_order'    : 20,
				'default_sort'  : ({ 'property': 'name' ,'direction': 'ASC' },),
				'grid_view'    : ('device_type', 'serial', 'entity', 'descr'),
				'form_view'    : ('device_type',
								  'serial',
								  'oper',
								  'place',
								  'entity',
								  'created_by',
								  'modified_by',
								  'installed_by',
								  'ctime',
								  'mtime',
								  'itime',
								  'descr',
								  'hostid',
								  'snmptype',
								  'cs_ro',
								  'cs_rw',
								  'v3user',
								  'v3scheme',
								  'v3authproto',
								  'v3authpass',
								  'v3privproto',
								  'v3privpass',
								  'mgmttype',
								  'mgmtuser',
								  'mgmtpass',
								  'mgmtepass'
				),
				'easy_search'  : ('device_type',),
				# 'extra_data'    : ('grid_icon',),
				'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
				'create_wizard' : SimpleWizard(title=_('Add new device'))
			}
		}
	)
	__mapper_args__ = {
		'polymorphic_identity' : DeviceMetatypeField.network
	}
	id = Column(
		'did',
		UInt32(),
		ForeignKey('devices_def.did', name='devices_network_def_fk_did', ondelete='CASCADE', onupdate='CASCADE'),
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
		}
	)
	snmp_type = Column(
		'snmptype',
		SNMPTypeField.db_type(),
		Comment('SNMP type'),
		nullable=True,
		default=SNMPTypeField.v1,
		info={
			'header_string' : _('SNMP Type'),
		}
	)
	cs_ro = Column(
		'cs_ro',
		Unicode(255),
		Comment('SNMPv2 Read-Only Community'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('ROCom')
			}
	)
	cs_rw = Column(
		'cs_rw',
		Unicode(255),
		Comment('SNMPv2 Read-Write Community'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('RWCom')
			}
	)
	v3user = Column(
		'v3user',
		Unicode(255),
		Comment('SNMPv3 User Name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('V3User')
			}
	)
	v3scheme = Column(
		'v3scheme',
		SNMPV3SchemeField.db_type(),
		Comment('SNMPv3 Connection Level'),
		nullable=True,
		default=SNMPV3SchemeField.authPriv,
		info={
			'header_string' : _('V3ConnLvl'),
		}
	)
	v3authproto = Column(
		'v3authproto',
		SNMPV3ProtoField.db_type(),
		Comment('SNMPv3 Auth Protocol'),
		nullable=True,
		default=SNMPV3ProtoField.md5,
		info={
			'header_string' : _('V3AuthProto')
		}
	)
	v3authpass = Column(
		'v3authpass',
		Unicode(255),
		Comment('SNMPv3 Auth Passphrase'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('V3AuthPass')
			}
	)
	v3privproto = Column(
		'v3privproto',
		SNMPV3PrivProtoField.db_type(),
		Comment('SNMPv3 Crypt Protocol'),
		nullable=True,
		default=SNMPV3PrivProtoField.des,
		info={
			'header_string' : _('V3CryptProto')
		}
	)
	v3privpass = Column(
		'v3privpass',
		Unicode(255),
		Comment('SNMPv3 Crypt Passphrase'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('V3PrivPass')
		}
	)
	mgmttype = Column(
		'mgmttype',
		SNMPV3MgmtTypeField.db_type(),
		Comment('Management Access Type'),
		nullable=True,
		default=SNMPV3MgmtTypeField.telnet,
		info={
			'header_string' : _('MgmtType')
		}
	)
	mgmtuser = Column(
		'mgmtuser',
		Unicode(255),
		Comment('Management User Name'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('MgmtUser')
		}
	)
	mgmtpass = Column(
		'mgmtpass',
		Unicode(255),
		Comment('Management Password'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('MgmtPass')
		}
	)
	mgmtepass = Column(
		'mgmtepass',
		Unicode(255),
		Comment('Management Enablement Password'),
		nullable=True,
		default=None,
		server_default=text('NULL'),
		info={
			'header_string' : _('MgmtEnabPass')
		}
	)

	host = relationship(
		'Host',
		innerjoin=True,
		backref='network_devices'
	)


	# def grid_icon(self, req):
	# 	return req.static_url('netprofile_devices:static/img/network.png')

class DeviceTypeFile(Base):
	"""
	Many-to-many relationship object. Links device types and files from VFS.
	"""
	__tablename__ = 'devices_types_files'
	__table_args__ = (
		Comment('File mappings to devices types'),
		Index('devices_types_files_u_efl', 'dtid', 'fileid', unique=True),
		Index('devices_types_files_i_fileid', 'fileid'),
		{
			'mysql_engine'  : 'InnoDB',
			'mysql_charset' : 'utf8',
			'info'          : {
				'cap_menu'      : 'BASE_DEVICES',
				'cap_read'      : 'DEVICETYPES_LIST',
				'cap_create'    : 'FILES_ATTACH_2DEVICETYPES',
				'cap_edit'      : 'FILES_ATTACH_2DEVICETYPES',
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
	devicetype_id = Column(
		'dtid',
		UInt32(),
		ForeignKey('devices_types_def.dtid', name='devices_types_files_fk_dtid', ondelete='CASCADE', onupdate='CASCADE'),
		Comment('DeviceType ID'),
		nullable=False,
		info={
			'header_string' : _('DeviceType'),
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
			'column_flex'   : 1
		}
	)

	file = relationship(
		'File',
		backref=backref(
			'linked_devices_types',
			cascade='all, delete-orphan',
			passive_deletes=True
		)
	)

	def __str__(self):
		return '%s' % str(self.file)
