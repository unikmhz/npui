#!/usr/bin/env python
# -*- coding: utf-8 -*-

#| devices_network | CREATE TABLE `devices_network` (
#  `did` int(10) unsigned NOT NULL COMMENT 'Device ID',
#  `hostid` int(10) unsigned DEFAULT NULL COMMENT 'Host ID',
#  `snmptype` enum('v1','v2c','v3') CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT 'SNMP Access Type',
#  `cs_ro` varchar(255) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT 'SNMPv2 Read-Only Community',
#  `cs_rw` varchar(255) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT 'SNMPv2 Read-Write Community',
#  `v3user` varchar(255) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT 'SNMPv3 User Name',
#  `v3scheme` enum('noAuthNoPriv','authNoPriv','authPriv') CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT 'SNMPv3 Connection Level',
#  `v3authproto` enum('MD5','SHA') CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT 'SNMPv3 Auth Protocol',
#  `v3authpass` varchar(255) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT 'SNMPv3 Auth Passphrase',
#  `v3privproto` enum('DES','AES128','AES192','AES256') CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT 'SNMPv3 Crypt Protocol',
#  `v3privpass` varchar(255) CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT 'SNMPv3 Crypt Passphrase',
#  `mgmttype` enum('ssh','telnet','vnc','rdp') CHARACTER SET ascii COLLATE ascii_bin DEFAULT NULL COMMENT 'Management Access Type',
#  `mgmtuser` varchar(255) DEFAULT NULL COMMENT 'Management User Name',
#  `mgmtpass` varchar(255) DEFAULT NULL COMMENT 'Management Password',
#  `mgmtepass` varchar(255) DEFAULT NULL COMMENT 'Management Enablement Password',
#  PRIMARY KEY (`did`),
#  UNIQUE KEY `u_hostid` (`hostid`),
#  CONSTRAINT `devices_network_fk_did` FOREIGN KEY (`did`) REFERENCES `devices_def` (`did`) ON DELETE CASCADE ON UPDATE CASCADE,
#  CONSTRAINT `devices_network_fk_hostid` FOREIGN KEY (`hostid`) REFERENCES `hosts_def` (`hostid`) ON DELETE SET NULL ON UPDATE CASCADE
#) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Network Devices' |


from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
    'IsOperational',
    'DeviceMetatype',
    'DeviceTypeFlagType',
    'DeviceFlagType',
    'DeviceCategory',
    'DeviceManufacturer',
    'DeviceType',
    'Device',
    'DeviceNetwork'
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

class IsOperational(DeclEnum):
    """
    Is Device Operational ENUM
    """
    yes   = 'Y',   _('Yes'),   10
    no   = 'N',   _('No'),   20


class DeviceMetatype(DeclEnum):
    """                                                                                                                                                                                                                                     Device type ENUM.                                                                                                                                                                                                                 
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
    
    dtcid = Column(
        'dtcid',
        UInt32(10),
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
                'default_sort' : ({ 'property': 'dtmid' ,'direction': 'ASC' },),
                'grid_view'    : ('sname', 'name', 'website'),
                'form_view'    : ('sname', 'name', 'website'),
                'easy_search'  : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new device manufacturer'))
                }
            }
        )
    
    dtmid = Column(
        'dtmid',
        UInt32(10),
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
            'header_string' : _('Short name')
            }
        )
    name = Column(
        'name',
        Unicode(255),
        Comment('Device Type Manufacturer Name'),
        unique=True,
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
        #Index('devices_types_def_device_u_devicemanufacturer', 'dtmid', 'name', unique=True),
        #Index('devices_types_def_device_u_devicecategory', 'dtcid', 'name', unique=True),
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
                'default_sort' : ({ 'property': 'dtid' ,'direction': 'ASC' },),
                'grid_view'    : ('category', 'manufacturer', 'name', 'descr'),
                'form_view'    : ('category', 'manufacturer', 'name', 'descr'),
                'easy_search'  : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new device type'))
                }
            }
        )

    dtid = Column(
        'dtid',
        UInt32(10),
        Sequence('dtmid_seq'),
        Comment('Device Type ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    dtmid = Column(
        'dtmid',
        UInt32(10),
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
        UInt32(10),
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
        #Index('devices_flags_types_device_u_devicemanufacturer', 'dtmid', 'name', unique=True),
        #Index('devices_types_def_device_u_devicecategory', 'dtcid', 'name', unique=True),
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
                'default_sort' : ({ 'property': 'dftid' ,'direction': 'ASC' },),
                'grid_view'    : ('name', 'descr'),
                'form_view'    : ('name', 'descr'),
                'easy_search'  : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new device flag type'))
                }
            }
        )

    dftid = Column(
        'dftid',
        UInt32(10),
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
            'header_string' : _('Device Flag Type')
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
                'default_sort' : ({ 'property': 'dtftid' ,'direction': 'ASC' },),
                'grid_view'    : ('name', 'descr'),
                'form_view'    : ('name', 'descr'),
                'easy_search'  : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new device type flag type'))

                }
            }
        )

    dtftid = Column(
        'dtftid',
        UInt32(10),
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
            'header_string' : _('Device Type Flag Type')
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
                'default_sort' : ({ 'property': 'did' ,'direction': 'ASC' },),
                #столбцы, которые будем отображать в таблице.
                #эти названия берутся из Reference классов, на которые ссылаются внешние ключи.
                'grid_view'    : ('devtype', 'serial', 'entities', 'addr', 'descr'),
                'form_view'    : ('devtype', 'serial', 'entities', 'addr', 'oper', 'dtype', 'ctime', 'mtime', 'itime', 'cby', 'mby', 'iby', 'cby', 'iby', 'mby', 'descr'),
                'easy_search'  : ('devtype',),
                #'form_view'    : ('serial', 'dtype', 'entities', 'addr', 'oper', 'creation_time', 'modification_time', 
                #                  'installation_time', 'created_by_id', 'modified_by_id', 'installed_by_id', 'descr'),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new device'))
                }
            }
        )

    did = Column(
        'did',
        UInt32(10),
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
        Unicode(64), 
        Comment('Device serial'),
        nullable=True,
        default='NULL',
        info={
            'header_string' : _('Device Serial')
            }
        )

    dtid = Column(
        'dtid',
        UInt32(10),
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
            'header_string' : _('Device Type')
            }
        )

    oper = Column(
        'oper',
        IsOperational.db_type(),
        Comment('Is Operational?'),
        nullable=False,
        default=IsOperational.no,
        info={
            'header_string' : _('Is Operational?')
            }
        )

    placeid = Column(
        'placeid',
        UInt32(10),
        ForeignKey('addr_places.placeid', name='devices_def_fk_placeid', onupdate='CASCADE'),
        Comment('Place ID'),
        nullable=False,
        info={
            'header_string' : _('Place')
            }
        )
    entityid = Column(
        'entityid',
        UInt32(10),
        ForeignKey('entities_def.entityid', name='devices_def_fk_entityid', onupdate='CASCADE', ondelete='SET NULL'),
        Comment('Entity ID'),
        nullable=True,
        info={
            'header_string' : _('Entity')
            }
        )
    #ctime
    ctime = Column(
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
    #mtime
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

    #itime
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
    #cby
    created_by_id = Column(
        'cby',
        UInt32(),
        #добавить reference
        ForeignKey('users.uid', name='devices_def_fk_cby', ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Created by'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string' : _('Created')
            }
        )
    #mby
    modified_by_id = Column(
        'mby',
        UInt32(),
        #добавить reference
        ForeignKey('users.uid', name='devices_def_fk_mby', ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Modified by'),
        nullable=True,
        default=None,
       server_default=text('NULL'),
        info={
            'header_string' : _('Modified')
            }
        )


    #iby
    installed_by_id = Column(
        'iby',
        UInt32(),
        #добавить reference
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

    device_name = relationship('DeviceType', backref=backref('linked_devtypes'))

    def __str__(self):
        return "{0}".format(self.device_name)


class DeviceNetwork(Base):
    """
    Network Device definition
    """
    

