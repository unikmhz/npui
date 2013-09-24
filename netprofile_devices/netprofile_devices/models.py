#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
    'DeviceMetatype',
    'DeviceTypeFlagType',
    'DeviceFlagType',
    'DeviceCategory',
    'DeviceManufacturer',
    'DeviceType',
    'Device',
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
from netprofile.tpl import TemplateObject
from netprofile.ext.data import (
    ExtModel,
    _name_to_class
    )
from netprofile.ext.columns import (
    HybridColumn,
    MarkupColumn
    )

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


class DeviceMetatype(DeclEnum):
    """
	Device metatypes class
    """
    simple = 'simple', _('Simple'),   10
    network = 'network', _('Network'), 20


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
                'cap_read'      : 'DEVICES_LIST',
                'cap_create'    : 'DEVICES_CREATE',
                'cap_edit'      : 'DEVICES_EDIT',
                'cap_delete'    : 'DEVICES_DELETE',
                'menu_name'    : _('Device categories'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 3,
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
    device_categories = relationship("DeviceType", backref=backref('category', innerjoin=True))
    
    def __str__(self):
        return "%s" % str(self.name)
    

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
                'cap_create'    : 'DEVICES_CREATE',
                'cap_edit'      : 'DEVICES_EDIT',
                'cap_delete'    : 'DEVICES_DELETE',
                'menu_name'    : _('Device Manufacturers'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 3,
                'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
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
        info={
            'header_string' : _('URL')
            }
        )
    
    manuf_names = relationship("DeviceType", backref=backref('manufacturer', innerjoin=True))
    
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
		Index('devices_types_def_i_dtcid', 'dtcid', 'dtcid'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                'cap_menu'      : 'BASE_DEVICES',
                'cap_read'      : 'DEVICES_LIST',
                'cap_create'    : 'DEVICES_CREATE',
                'cap_edit'      : 'DEVICES_EDIT',
                'cap_delete'    : 'DEVICES_DELETE',
                'menu_name'    : _('Device types'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 3,
                'default_sort' : ({ 'property': 'name' ,'direction': 'ASC' },),
                'grid_view'    : ('category', 'manufacturer', 'name', 'descr'),
                'form_view'    : ('category', 'manufacturer', 'name', 'descr'),
                'easy_search'  : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new device type'))
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
        unique=True,
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
                'menu_order'    : 3,
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
                'cap_create'    : 'DEVICES_TYPES_FLAGTYPES_CREATE',
                'cap_edit'      : 'DEVICES_TYPES_FLAGTYPES_EDIT',
                'cap_delete'    : 'DEVICES_TYPES_FLAGTYPES_DELETE',
                'menu_name'    : _('Device type flag types'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 3,
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
    def __str__(self):
        return "%s" % str(self.name)


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
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                'cap_menu'      : 'BASE_DEVICES',
                'cap_read'      : 'DEVICES_LIST',
                'cap_create'    : 'DEVICES_CREATE',
                'cap_edit'      : 'DEVICES_EDIT',
                'cap_delete'    : 'DEVICES_DELETE',
                'menu_name'    : _('Devices'),
                'show_in_menu'  : 'modules',
                'menu_main'     : True,
                'menu_order'    : 40,
                'default_sort' : ({ 'property': 'serial' ,'direction': 'ASC' },),
                'grid_view'    : ('devicetype', 'serial', 'entity', 'addr', 'descr'),
                'form_view'    : ('devicetype',
                                  'serial',
                                  'dtype',
                                  'oper',
                                  'place',
                                  'entity',
                                  'created',
                                  'modified',
                                  'installed',
                                  'ctime',
                                  'mtime',
                                  'itime',
                                  'descr'),
                'easy_search'  : ('devicetype',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new device'))
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
        default='NULL',
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
        unique=True,
        info={
            'header_string' : _('Type'),
            'filter_type'   : 'list'
            }
        )
    dtype = Column(
        'dtype',
        DeviceMetatype.db_type(),
        Comment('Device Metatype Shortcut'),
        nullable=False,
        default=DeviceMetatype.simple,
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
            'read_only'     : True
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
            'read_only'     : True
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

    place = relationship('Place', backref=backref('deviceplaces', innerjoin=True))
    entity = relationship('Entity', backref=backref('deviceentities', innerjoin=True))
    created = relationship('User', backref=backref('devicecreated'), foreign_keys=created_by_id)
    modified = relationship('User', backref=backref('devicemodified'), foreign_keys=modified_by_id)
    installed = relationship('User', backref=backref('deviceinstalled'), foreign_keys=installed_by_id)
    devicetype = relationship('DeviceType', backref=backref('devicetype', innerjoin=True))

    def __str__(self):
        return "{0}".format(self.devicetype)


    

