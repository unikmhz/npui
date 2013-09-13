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

from netprofile_geo import Place
#addr_places.placeid
from netprofile_entities import Entity
#entities_def.entityid
from netprofile_core import User
#users.uid


from pyramid.threadlocal import get_current_request
from pyramid.i18n import (
    TranslationStringFactory,
	get_localizer
        )

_ = TranslationStringFactory('netprofile_devices')


class DeviceMetatype(DeclEnum):
    """                                                                                                                                    Device metatypes class
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
        ASCIIString(255),
        Comment('Device Type Category Name'),
        unique=True,
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
                'menu_name'    : _('Device manufacturers'),
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
        ASCIIString(48),
        Comment('Device Manufacturer Short Name'),
        nullable=False,
        info={
            'header_string' : _('Short name')
            }
        )
    name = Column(
        'name',
        ASCIIString(255),
        Comment('Device Type Manufacturer Name'),
        unique=True,
        nullable=False,
        info={
            'header_string' : _('Name')
            }
        )
    website = Column(
        'website',
        ASCIIString(255),
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
            'header_string' : _('Device manufacturer'),
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
            'header_string' : _('Device category')
            }
        )
    name = Column(
        'name',
        ASCIIString(255),
        Comment('Device Type Name'),
        nullable=False,
        info={
            'header_string' : _('Device type')
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
    
    device_types = relationship("Device", backref=backref('devtype', innerjoin=True))    

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
        ASCIIString(255),
        Comment('Device Flag Type Name'),
        nullable=False,
        info={
            'header_string' : _('Device flag type name')
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
        ASCIIString(255),
        Comment('Device Type Flag Type Name'),
        nullable=False,
        info={
            'header_string' : _('Device type flag type')
            }
        )
    descr = Column(
        'descr',
        UnicodeText(),
        Comment('Device Type Flag Type Description'),
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
                'grid_view'    : ('devtype', 'serial', 'entities', 'addr', 'descr'),
                'form_view'    : ('devtype',
                                  'serial',
                                  'dtype',
                                  'oper',
                                  'deviceplaces',
                                  'deviceentities',
                                  'devicecreated',
                                  'devicemodified',
                                  'deviceinstalled',
                                  'descr'),
                'easy_search'  : ('devtype',),
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
            'header_string' : _('Device ID')
            }
        )
    serial = Column(
        'serial', 
        ASCIIString(64), 
        Comment('Device serial'),
        nullable=True,
        default='NULL',
        info={
            'header_string' : _('Device Serial')
            }
        )
    #devtype
    dtid = Column(
        'dtid',
        UInt32(),
        ForeignKey('devices_types_def.dtid', name='devices_def_fk_dtid', onupdate='CASCADE'),
        Comment('Device Type ID'),
        nullable=False,
        unique=True,
        info={
            'header_string' : _('Device Type'),
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
            'header_string' : _('Device metatype')
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
    #deviceplaces
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
    #deviceentities
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
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        info={
            'header_string' : _('Modified')
            }
        )
    installation_time = Column(
        'itime',
        TIMESTAMP(),
        Comment('Installation timestamp'),
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        info={
            'header_string' : _('Installed')
            }
        )
    #devicecreated
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
    #devicemodified
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
    #deviceinstalled
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

    Place.deviceplaces = relationship('Device', backref=backref('deviceplaces', innerjoin=True))
    Entity.deviceentities = relationship('Device', backref=backref('deviceentities', innerjoin=True))
    User.devicecreated = relationship('Device', backref=backref('devicecreated', innerjoin=True), foreign_keys=created_by_id)
    User.devicemodified = relationship('Device', backref=backref('devicemodified', innerjoin=True), foreign_keys=modified_by_id)
    User.deviceinstalled = relationship('Device', backref=backref('deviceinstalled', innerjoin=True), foreign_keys=installed_by_id)

    devicetypes = association_proxy('devtype', 'name', creator=lambda v: DeviceType(id=v))

    def __str__(self):
        return "{0}".format(self.devicetypes)


    

