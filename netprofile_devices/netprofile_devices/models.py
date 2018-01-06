#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Devices module - Models
# Copyright © 2013-2018 Alex Unigovsky
# Copyright © 2014 Sergey Dikunov
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

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

__all__ = [
    'DeviceClass',

    'DeviceTypeCategory',
    'DeviceTypeManufacturer',

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

    'NetworkDeviceMediaType',
    'NetworkDeviceInterface',
    'NetworkDeviceBinding',

    'SNMPTypeField',
    'SNMPV3SchemeField',
    'SNMPV3ProtoField',
    'SNMPV3PrivProtoField',
    'SNMPV3MgmtTypeField'
]

import snimpy.manager
import pkg_resources
from sqlalchemy import (
    Column,
    FetchedValue,
    ForeignKey,
    Index,
    Sequence,
    TIMESTAMP,
    Unicode,
    UnicodeText,
    VARBINARY,
    text
)
from sqlalchemy.orm import (
    backref,
    relationship
)
from sqlalchemy.ext.associationproxy import association_proxy
from pyramid.i18n import (
    TranslationString,
    TranslationStringFactory
)

from netprofile.db.connection import Base
from netprofile.db.fields import (
    ASCIIString,
    DeclEnum,
    NPBoolean,
    UInt32,
    UInt64,
    npbool
)
from netprofile.db.ddl import (
    Comment,
    CurrentTimestampDefault,
    Trigger
)
from netprofile.ext.columns import MarkupColumn
from netprofile.ext.wizards import SimpleWizard

_ = TranslationStringFactory('netprofile_devices')


class DeviceClass(Base):
    """
    Defines a class of devices and device types.
    """
    __tablename__ = 'devices_classes'
    __table_args__ = (
        Comment('Device classes'),
        Index('devices_classes_u_name', 'name', unique=True),
        Index('devices_classes_u_spec', 'npmodid', 'model', unique=True),
        Index('devices_classes_u_longname', 'longname', unique=True),
        Index('devices_classes_u_plural', 'plural', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICES_LIST',
                'cap_create':    'ADMIN_DEV',
                'cap_edit':      'ADMIN_DEV',
                'cap_delete':    'ADMIN_DEV',

                'menu_name':     _('Classes'),
                'show_in_menu':  'admin',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('dclsid', 'module', 'name', 'model'),
                'grid_hidden':   ('dclsid',),
                'form_view':     ('module', 'model', 'name',
                                  'longname', 'plural', 'descr'),
                'easy_search':   ('name', 'model', 'longname', 'plural'),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new device class'))
            }
        })
    id = Column(
        'dclsid',
        UInt32(),
        Sequence('devices_classes_dclsid_seq', start=101, increment=1),
        Comment('Device class ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Device class name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 3
        })
    module_id = Column(
        'npmodid',
        UInt32(),
        ForeignKey('np_modules.npmodid', name='devices_classes_fk_npmodid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('NetProfile module ID'),
        nullable=False,
        default=1,
        server_default=text('1'),
        info={
            'header_string': _('Module'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    model = Column(
        ASCIIString(255),
        Comment('ORM declarative model class name'),
        nullable=False,
        info={
            'header_string': _('Model'),
            'column_flex': 2
        })
    long_name = Column(
        'longname',
        Unicode(255),
        Comment('Long device class name'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Long Name')
        })
    plural = Column(
        Unicode(255),
        Comment('Device class plural string'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Plural')
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Device class description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    module = relationship(
        'NPModule',
        innerjoin=True,
        backref=backref('device_classes',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    device_types = relationship(
        'DeviceType',
        backref=backref('class', innerjoin=True),
        passive_deletes='all')
    devices = relationship(
        'Device',
        backref=backref('class', innerjoin=True),
        passive_deletes='all')

    def __str__(self):
        req = getattr(self, '__req__', None)
        if req is not None:
            if self.module:
                domain = 'netprofile_' + self.module.name
                return req.localizer.translate(
                        TranslationString(self.name, domain=domain))
        return str(self.name)


class DeviceTypeManufacturer(Base):
    """
    Device manufacturer.
    """
    __tablename__ = 'devices_types_mfct'
    __table_args__ = (
        Comment('Device type manufacturers'),
        Index('devices_types_mfct_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICETYPES_LIST',
                'cap_create':    'DEVICETYPES_MANUFACTURERS_CREATE',
                'cap_edit':      'DEVICETYPES_MANUFACTURERS_EDIT',
                'cap_delete':    'DEVICETYPES_MANUFACTURERS_DELETE',

                'menu_name':     _('Manufacturers'),
                'show_in_menu':  'admin',
                'default_sort':  ({'property': 'sname', 'direction': 'ASC'},),
                'grid_view':     ('dtmid', 'sname', 'name'),
                'grid_hidden':   ('dtmid',),
                'form_view':     ('sname', 'name', 'website'),
                'easy_search':   ('sname', 'name'),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(
                                    title=_('Add new device manufacturer'))
            }
        })
    id = Column(
        'dtmid',
        UInt32(),
        Sequence('devices_types_mfct_dtmid_seq'),
        Comment('Device type manufacturer ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    short_name = Column(
        'sname',
        Unicode(48),
        Comment('Device type manufacturer short name'),
        nullable=False,
        info={
            'header_string': _('Short Name'),
            'column_flex': 2
        })
    name = Column(
        Unicode(255),
        Comment('Device type manufacturer name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 3
        })
    website = Column(
        Unicode(255),
        Comment('Device type manufacturer website URL'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('URL')
        })

    def __str__(self):
        return str(self.name)


class DeviceFlagType(Base):
    """
    Device flag type.
    """
    __tablename__ = 'devices_flags_types'
    __table_args__ = (
        Comment('Device flag types'),
        Index('devices_flags_types_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICES_LIST',
                'cap_create':    'DEVICES_FLAGTYPES_CREATE',
                'cap_edit':      'DEVICES_FLAGTYPES_EDIT',
                'cap_delete':    'DEVICES_FLAGTYPES_DELETE',

                'menu_name':     _('Device Flags'),
                'show_in_menu':  'admin',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('dftid', 'name'),
                'grid_hidden':   ('dftid',),
                'form_view':     ('name', 'descr'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(
                                    title=_('Add new device flag type'))
            }
        })
    id = Column(
        'dftid',
        UInt32(),
        Sequence('devices_flags_types_dftid_seq'),
        Comment('Device flag type ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Device flag type name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Device flag type description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    flagmap = relationship(
        'DeviceFlag',
        backref=backref('type', innerjoin=True, lazy='joined'),
        cascade='all, delete-orphan',
        passive_deletes=True)

    devices = association_proxy(
        'flagmap',
        'device',
        creator=lambda v: DeviceFlag(device=v))

    def __str__(self):
        return str(self.name)


class DeviceTypeFlagType(Base):
    """
    Device type flag type.
    """
    __tablename__ = 'devices_types_flags_types'
    __table_args__ = (
        Comment('Device type flag types'),
        Index('devices_types_flags_types_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICETYPES_LIST',
                'cap_create':    'DEVICETYPES_FLAGTYPES_CREATE',
                'cap_edit':      'DEVICETYPES_FLAGTYPES_EDIT',
                'cap_delete':    'DEVICETYPES_FLAGTYPES_DELETE',

                'menu_name':     _('Type Flags'),
                'show_in_menu':  'admin',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('dtftid', 'name'),
                'grid_hidden':   ('dtftid',),
                'form_view':     ('name', 'descr'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(
                                    title=_('Add new device type flag type'))
            }
        })
    id = Column(
        'dtftid',
        UInt32(),
        Sequence('devices_types_flags_types_dtftid_seq'),
        Comment('Device type flag type ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Device type flag type name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Device type flag type description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    flagmap = relationship(
        'DeviceTypeFlag',
        backref=backref('flag_type', innerjoin=True, lazy='joined'),
        cascade='all, delete-orphan',
        passive_deletes=True)

    device_types = association_proxy(
        'flagmap',
        'device_type',
        creator=lambda v: DeviceTypeFlag(device_type=v))

    def __str__(self):
        return str(self.name)


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
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICETYPES_LIST',
                'cap_create':    'DEVICETYPES_EDIT',
                'cap_edit':      'DEVICETYPES_EDIT',
                'cap_delete':    'DEVICETYPES_EDIT',

                'menu_name':     _('Flags')
            }
        })
    id = Column(
        'dtfid',
        UInt32(),
        Sequence('devices_types_flags_def_dtfid_seq'),
        Comment('Device type flag ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    device_type_id = Column(
        'dtid',
        UInt32(),
        ForeignKey('devices_types_def.dtid',
                   name='devices_types_flags_def_fk_dtid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Device type ID'),
        nullable=False,
        info={
            'header_string': _('Device Type'),
            'filter_type': 'none'
        })
    flag_type_id = Column(
        'dtftid',
        UInt32(),
        ForeignKey('devices_types_flags_types.dtftid',
                   name='devices_types_flags_def_fk_dtftid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Device type flag type ID'),
        nullable=False,
        info={
            'header_string': _('Type'),
            'filter_type': 'nplist'
        })


class DeviceTypeCategory(Base):
    """
    Device category.
    """
    __tablename__ = 'devices_types_cats'
    __table_args__ = (
        Comment('Device categories'),
        Index('devices_types_cats_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICETYPES_LIST',
                'cap_create':    'DEVICETYPES_CATEGORIES_CREATE',
                'cap_edit':      'DEVICETYPES_CATEGORIES_EDIT',
                'cap_delete':    'DEVICETYPES_CATEGORIES_DELETE',

                'menu_name':     _('Categories'),
                'show_in_menu':  'admin',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('dtcid', 'name'),
                'grid_hidden':   ('dtcid',),
                'form_view':     ('name',),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(
                                    title=_('Add new device category'))
            }
        })
    id = Column(
        'dtcid',
        UInt32(),
        Sequence('devices_types_cats_dtcid_seq'),
        Comment('Device type category ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Device type category name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })

    def __str__(self):
        return str(self.name)


class DeviceType(Base):
    """
    Abstract device type.
    """
    __tablename__ = 'devices_types_def'
    __table_args__ = (
        Comment('Device types'),
        Index('devices_types_def_u_dt', 'dtmid', 'name', unique=True),
        Index('devices_types_def_i_dtcid', 'dtcid'),
        Index('devices_types_def_i_dclsid', 'dclsid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICETYPES_LIST',
                'cap_create':    'DEVICETYPES_CREATE',
                'cap_edit':      'DEVICETYPES_EDIT',
                'cap_delete':    'DEVICETYPES_DELETE',

                'show_in_menu':  'admin',
                'menu_name':     _('Types'),
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('dtid', 'category', 'manufacturer', 'name'),
                'grid_hidden':   ('dtid',),
                'form_view':     ('category', 'manufacturer', 'name',
                                  'descr', 'flags'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple')
            }
        })
    id = Column(
        'dtid',
        UInt32(),
        Sequence('devices_types_def_dtid_seq'),
        Comment('Device type ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    class_id = Column(
        'dclsid',
        UInt32(),
        ForeignKey('devices_classes.dclsid',
                   name='devices_types_def_fk_dclsid',
                   onupdate='CASCADE'),
        Comment('Device class ID'),
        nullable=False,
        info={
            'header_string': _('Class')
        })
    manufacturer_id = Column(
        'dtmid',
        UInt32(),
        ForeignKey('devices_types_mfct.dtmid',
                   name='devices_types_def_fk_dtmid',
                   onupdate='CASCADE'),
        Comment('Device type manufacturer ID'),
        nullable=False,
        info={
            'header_string': _('Manufacturer'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    category_id = Column(
        'dtcid',
        UInt32(),
        ForeignKey('devices_types_cats.dtcid',
                   name='devices_types_def_fk_dtcid',
                   onupdate='CASCADE'),
        Comment('Device type category ID'),
        nullable=False,
        info={
            'header_string': _('Category'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    name = Column(
        Unicode(255),
        Comment('Device type name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 3
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Device type description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })
    __mapper_args__ = {
        'polymorphic_identity': 0,
        'polymorphic_on': class_id,
        'with_polymorphic': '*'
    }

    manufacturer = relationship(
        'DeviceTypeManufacturer',
        innerjoin=True,
        backref='device_types')
    category = relationship(
        'DeviceTypeCategory',
        innerjoin=True,
        backref='device_types')
    flagmap = relationship(
        'DeviceTypeFlag',
        backref=backref('device_type', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)
    filemap = relationship(
        'DeviceTypeFile',
        backref=backref('device_type', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    flags = association_proxy(
        'flagmap',
        'flag_type',
        creator=lambda v: DeviceTypeFlag(flag_type=v))
    files = association_proxy(
        'filemap',
        'file',
        creator=lambda v: DeviceTypeFile(file=v))

    def has_flag(self, name):
        for flag in self.flags:
            if flag.name == name:
                return True
        return False

    def __str__(self):
        return '%s %s' % (
            str(self.manufacturer.short_name or self.manufacturer.name),
            str(self.name))


class SimpleDeviceType(DeviceType):
    """
    Simple device type.
    """
    __tablename__ = 'devices_types_simple'
    __table_args__ = (
        Comment('Simple device types'),
        Trigger('after', 'delete', 't_devices_types_simple_ad'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICETYPES_LIST',
                'cap_create':    'DEVICETYPES_CREATE',
                'cap_edit':      'DEVICETYPES_EDIT',
                'cap_delete':    'DEVICETYPES_DELETE',

                'show_in_menu':  'admin',
                'menu_name':     _('Simple Devices'),
                'menu_parent':   'devicetype',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('dtid', 'category', 'manufacturer', 'name'),
                'grid_hidden':   ('dtid',),
                'form_view':     ('category', 'manufacturer', 'name',
                                  'descr', 'flags'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(
                                    title=_('Add new simple device type'))
            }
        })
    __mapper_args__ = {'polymorphic_identity': 1}
    id = Column(
        'dtid',
        UInt32(),
        ForeignKey('devices_types_def.dtid',
                   name='devices_types_simple_fk_dtid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Device type ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })


class NetworkDeviceType(DeviceType):
    """
    Network device type.
    """
    __tablename__ = 'devices_types_network'
    __table_args__ = (
        Comment('Network device types'),
        Trigger('after', 'delete', 't_devices_types_network_ad'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICETYPES_LIST',
                'cap_create':    'DEVICETYPES_CREATE',
                'cap_edit':      'DEVICETYPES_EDIT',
                'cap_delete':    'DEVICETYPES_DELETE',

                'show_in_menu':  'admin',
                'menu_name':     _('Network Devices'),
                'menu_parent':   'devicetype',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('dtid', 'category', 'manufacturer', 'name',
                                  'manageable', 'modular'),
                'grid_hidden':   ('dtid',),
                'form_view':     ('category', 'manufacturer',
                                  'name', 'descr', 'flags',
                                  'manageable', 'modular',
                                  'icon', 'handler'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(
                                    title=_('Add new network device type'))
            }
        })
    __mapper_args__ = {'polymorphic_identity': 2}
    id = Column(
        'dtid',
        UInt32(),
        ForeignKey('devices_types_def.dtid',
                   name='devices_types_network_fk_dtid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Device type ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    manageable = Column(
        NPBoolean(),
        Comment('Is manageable?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Manageable')
        })
    modular = Column(
        NPBoolean(),
        Comment('Is modular/slotted/chassis?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Modular')
        })
    icon = Column(
        ASCIIString(16),
        Comment('Schematic icon name'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Icon')
        })
    handler = Column(
        ASCIIString(255),
        Comment('Device handler class'),
        nullable=True,
        default='default',
        server_default='default',
        info={
            'header_string': _('Handler')
        })


class Device(Base):
    """
    Abstract device.
    """
    __tablename__ = 'devices_def'
    __table_args__ = (
        Comment('Devices'),
        Index('devices_def_i_dclsid', 'dclsid'),
        Index('devices_def_i_dtid', 'dtid'),
        Index('devices_def_i_placeid', 'placeid'),
        Index('devices_def_i_entityid', 'entityid'),
        Index('devices_def_i_cby', 'cby'),
        Index('devices_def_i_mby', 'mby'),
        Index('devices_def_i_iby', 'iby'),
        Trigger('before', 'insert', 't_devices_def_bi'),
        Trigger('before', 'update', 't_devices_def_bu'),
        Trigger('after', 'insert', 't_devices_def_ai'),
        Trigger('after', 'update', 't_devices_def_au'),
        Trigger('after', 'delete', 't_devices_def_ad'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICES_LIST',
                'cap_create':    'DEVICES_CREATE',
                'cap_edit':      'DEVICES_EDIT',
                'cap_delete':    'DEVICES_DELETE',

                'show_in_menu':  'modules',
                'menu_name':     _('Devices'),
                'menu_main':     True,
                'default_sort':  ({'property': 'serial', 'direction': 'ASC'},),
                'grid_view':     (MarkupColumn(
                                    name='icon',
                                    header_string='&nbsp;',
                                    help_text=_('Device icon'),
                                    column_width=22,
                                    column_name=_('Icon'),
                                    column_resizable=False,
                                    cell_class='np-nopad',
                                    template='<tpl if="grid_icon">'
                                             '<img class="np-block-img" '
                                             'src="{grid_icon:encodeURI}" '
                                             '/></tpl>'),
                                  'did', 'device_type', 'serial', 'place',
                                  'entity', 'oper'),
                'grid_hidden':   ('did',),
                'form_view':     ('device_type', 'serial',
                                  'place', 'entity', 'oper',
                                  'ctime', 'created_by',
                                  'mtime', 'modified_by',
                                  'itime', 'installed_by',
                                  'descr'),
                'easy_search':   ('serial',),
                'extra_data':    ('grid_icon',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
            }
        })
    id = Column(
        'did',
        UInt32(),
        Sequence('devices_def_did_seq'),
        Comment('Device ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    class_id = Column(
        'dclsid',
        UInt32(),
        ForeignKey('devices_classes.dclsid', name='devices_def_fk_dclsid',
                   onupdate='CASCADE'),
        Comment('Device class ID'),
        nullable=False,
        info={
            'header_string': _('Class'),
            'filter_type': 'nplist',
            'editor_xtype': 'simplemodelselect'
        })
    serial = Column(
        Unicode(64),
        Comment('Device serial'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Serial'),
            'column_flex': 1
        })
    device_type_id = Column(
        'dtid',
        UInt32(),
        ForeignKey('devices_types_def.dtid', name='devices_def_fk_dtid',
                   onupdate='CASCADE'),
        Comment('Device type ID'),
        nullable=False,
        info={
            'header_string': _('Type'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    operational = Column(
        'oper',
        NPBoolean(),
        Comment('Is operational?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Operational')
        })
    place_id = Column(
        'placeid',
        UInt32(),
        ForeignKey('addr_places.placeid', name='devices_def_fk_placeid',
                   onupdate='CASCADE'),
        Comment('Place ID'),
        nullable=False,
        info={
            'header_string': _('Place'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    entity_id = Column(
        'entityid',
        UInt32(),
        ForeignKey('entities_def.entityid', name='devices_def_fk_entityid',
                   onupdate='CASCADE', ondelete='SET NULL'),
        Comment('Owner\'s entity ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Entity'),
            'filter_type': 'none',
            'column_flex': 1
        })
    creation_time = Column(
        'ctime',
        TIMESTAMP(),
        Comment('Creation timestamp'),
        nullable=True,
        default=None,
        server_default=FetchedValue(),
        info={
            'header_string': _('Created'),
            'read_only': True
        })
    modification_time = Column(
        'mtime',
        TIMESTAMP(),
        Comment('Last modification timestamp'),
        CurrentTimestampDefault(on_update=True),
        nullable=False,
        info={
            'header_string': _('Modified'),
            'read_only': True
        })
    installation_time = Column(
        'itime',
        TIMESTAMP(),
        Comment('Installation timestamp'),
        nullable=True,
        default=None,
        server_default=FetchedValue(),
        info={
            'header_string': _('Installed'),
            'read_only': True
        })
    created_by_id = Column(
        'cby',
        UInt32(),
        ForeignKey('users.uid', name='devices_def_fk_cby',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Created by'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Created'),
            'read_only': True
        })
    modified_by_id = Column(
        'mby',
        UInt32(),
        ForeignKey('users.uid', name='devices_def_fk_mby',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Modified by'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Modified'),
            'read_only': True
        })
    installed_by_id = Column(
        'iby',
        UInt32(),
        ForeignKey('users.uid', name='devices_def_fk_iby',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Installed by'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Installed'),
            'read_only': True
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Device description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })
    __mapper_args__ = {
        'polymorphic_identity': 0,
        'polymorphic_on': class_id,
        'with_polymorphic': '*'
    }

    place = relationship(
        'Place',
        innerjoin=True,
        backref='devices')
    entity = relationship(
        'Entity',
        backref=backref('devices',
                        passive_deletes=True))
    created_by = relationship(
        'User',
        foreign_keys=created_by_id,
        backref=backref('created_devices',
                        passive_deletes=True))
    modified_by = relationship(
        'User',
        foreign_keys=modified_by_id,
        backref=backref('modified_devices',
                        passive_deletes=True))
    installed_by = relationship(
        'User',
        foreign_keys=installed_by_id,
        backref=backref('installed_devices',
                        passive_deletes=True))
    device_type = relationship(
        'DeviceType',
        innerjoin=True,
        backref='devices')
    flagmap = relationship(
        'DeviceFlag',
        backref=backref('device', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    flags = association_proxy(
        'flagmap',
        'type',
        creator=lambda v: DeviceFlag(type=v))

    def grid_icon(self, req):
        return req.static_url('netprofile_devices:static/img/device.png')

    def has_flag(self, name):
        for flag in self.flags:
            if flag.name == name:
                return True
        return False

    def __str__(self):
        if self.serial:
            fmt = _('%s: S/N %s')
        else:
            fmt = _('%s @%s')
        req = getattr(self, '__req__', None)
        if req:
            fmt = req.localizer.translate(fmt)
        return fmt % (str(self.device_type),
                      str(self.serial if self.serial else self.place))


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
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICES_LIST',
                'cap_create':    'DEVICES_EDIT',
                'cap_edit':      'DEVICES_EDIT',
                'cap_delete':    'DEVICES_EDIT',

                'menu_name':     _('Flags')
            }
        })
    id = Column(
        'dfid',
        UInt32(),
        Sequence('devices_flags_def_dfid_seq'),
        Comment('Device flag ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    device_id = Column(
        'did',
        UInt32(),
        ForeignKey('devices_def.did', name='devices_flags_def_fk_did',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Device ID'),
        nullable=False,
        info={
            'header_string': _('Device'),
            'filter_type': 'none'
        })
    type_id = Column(
        'dftid',
        UInt32(),
        ForeignKey('devices_flags_types.dftid',
                   name='devices_flags_def_fk_dftid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Device flag type ID'),
        nullable=False,
        info={
            'header_string': _('Type'),
            'filter_type': 'nplist'
        })


class SimpleDevice(Device):
    """
    Simple device.
    """
    __tablename__ = 'devices_simple'
    __table_args__ = (
        Comment('Simple devices'),
        Trigger('after', 'delete', 't_devices_simple_ad'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICES_LIST',
                'cap_create':    'DEVICES_CREATE',
                'cap_edit':      'DEVICES_EDIT',
                'cap_delete':    'DEVICES_DELETE',

                'show_in_menu':  'modules',
                'menu_name':     _('Simple Devices'),
                'default_sort':  ({'property': 'serial', 'direction': 'ASC'},),
                'grid_view':     (MarkupColumn(name='icon',
                                               header_string='&nbsp;',
                                               help_text=_('Device icon'),
                                               column_width=22,
                                               column_name=_('Icon'),
                                               column_resizable=False,
                                               cell_class='np-nopad',
                                               template='<tpl if="grid_icon">'
                                               '<img class="np-block-img" '
                                               'src="{grid_icon:encodeURI}" />'
                                               '</tpl>'),
                                  'did', 'device_type', 'serial', 'place',
                                  'entity', 'oper'),
                'grid_hidden':   ('did',),
                'form_view':     (
                    'device_type', 'serial',
                    'place', 'entity', 'oper',
                    'ctime', 'created_by',
                    'mtime', 'modified_by',
                    'itime', 'installed_by',
                    'descr'
                ),
                'easy_search':   ('serial',),
                'extra_data':    ('grid_icon',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new simple device'))
            }
        })
    __mapper_args__ = {'polymorphic_identity': 1}
    id = Column(
        'did',
        UInt32(),
        ForeignKey('devices_def.did', name='devices_simple_fk_did',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Device ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })

    def grid_icon(self, req):
        return req.static_url(
                'netprofile_devices:static/img/device_simple.png')


class SNMPTypeField(DeclEnum):
    """
    SNMP type ENUM.
    """
    v1 = 'v1', _('Version 1'), 10
    v2c = 'v2c', _('Version 2'), 20
    v3 = 'v3', _('Version 3'), 30


class SNMPV3SchemeField(DeclEnum):
    """
    SNMP security level ENUM.
    """
    noAuthNoPriv = 'noAuthNoPriv', _('NoAuthNoPriv'), 10
    authNoPriv = 'authNoPriv', _('AuthNoPriv'), 20
    authPriv = 'authPriv', _('AuthPriv'), 30


class SNMPV3ProtoField(DeclEnum):
    """
    SNMP authentication protocol ENUM.
    """
    md5 = 'MD5', _('MD5'), 10
    sha = 'SHA', _('SHA'), 20


class SNMPV3PrivProtoField(DeclEnum):
    """
    SNMP privacy protocol ENUM.
    """
    des = 'DES', _('DES'), 10
    des3 = '3DES', _('3DES'), 20
    aes128 = 'AES128', _('AES128'), 30
    aes192 = 'AES192', _('AES192'), 40
    aes256 = 'AES256', _('AES256'), 50


class SNMPV3MgmtTypeField(DeclEnum):
    """
    Management access type ENUM.
    """
    ssh = 'ssh', _('SSH'), 10
    telnet = 'telnet', _('Telnet'), 20
    vnc = 'vnc', _('VNC'), 30
    rdp = 'rdp', _('RDP'), 40


class NetworkDevice(Device):
    """
    Network device.
    """
    __tablename__ = 'devices_network'
    __table_args__ = (
        Comment('Network devices'),
        Index('devices_network_u_hostid', 'hostid', unique=True),
        Trigger('after', 'delete', 't_devices_network_ad'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICES_LIST',
                'cap_create':    'DEVICES_CREATE',
                'cap_edit':      'DEVICES_EDIT',
                'cap_delete':    'DEVICES_DELETE',

                'show_in_menu':  'modules',
                'menu_name':     _('Network Devices'),
                'default_sort':  ({'property': 'serial', 'direction': 'ASC'},),
                'grid_view':     (MarkupColumn(name='icon',
                                               header_string='&nbsp;',
                                               help_text=_('Device icon'),
                                               column_width=22,
                                               column_name=_('Icon'),
                                               column_resizable=False,
                                               cell_class='np-nopad',
                                               template='<tpl if="grid_icon">'
                                               '<img class="np-block-img" '
                                               'src="{grid_icon:encodeURI}" '
                                               '/></tpl>'),
                                  'did', 'device_type', 'serial', 'place',
                                  'entity', 'host', 'oper'),
                'grid_hidden':   ('did',),
                'form_view':     ('device_type', 'serial',
                                  'place', 'entity', 'host', 'oper',
                                  'snmptype', 'cs_ro', 'cs_rw',
                                  'v3user', 'v3scheme',
                                  'v3authproto', 'v3authpass',
                                  'v3privproto', 'v3privpass',
                                  'mgmttype', 'mgmtuser',
                                  'mgmtpass', 'mgmtepass',
                                  'remoteid',
                                  'ctime', 'created_by',
                                  'mtime', 'modified_by',
                                  'itime', 'installed_by',
                                  'descr'),
                'easy_search':   ('serial',),
                'extra_data':    ('grid_icon',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(
                                    title=_('Add new network device'))
            }
        })
    __mapper_args__ = {'polymorphic_identity': 2}
    id = Column(
        'did',
        UInt32(),
        ForeignKey('devices_def.did', name='devices_network_fk_did',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Device ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    host_id = Column(
        'hostid',
        UInt32(),
        ForeignKey('hosts_def.hostid', name='devices_network_fk_hostid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Host ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Host'),
            'filter_type': 'none',
            'column_flex': 2
        })
    snmp_type = Column(
        'snmptype',
        SNMPTypeField.db_type(),
        Comment('SNMP access type'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('SNMP Version'),
            'read_cap': 'DEVICES_PASSWORDS',
            'write_cap': 'DEVICES_PASSWORDS'
        })
    snmp_ro_community = Column(
        'cs_ro',
        ASCIIString(255),
        Comment('SNMPv2 read-only community'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('R/O Community'),
            'read_cap': 'DEVICES_PASSWORDS',
            'write_cap': 'DEVICES_PASSWORDS'
        })
    snmp_rw_community = Column(
        'cs_rw',
        ASCIIString(255),
        Comment('SNMPv2 read-write community'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('R/W Community'),
            'read_cap': 'DEVICES_PASSWORDS',
            'write_cap': 'DEVICES_PASSWORDS'
        })
    snmp_v3_user = Column(
        'v3user',
        ASCIIString(255),
        Comment('SNMPv3 user name'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('SNMPv3 User'),
            'read_cap': 'DEVICES_PASSWORDS',
            'write_cap': 'DEVICES_PASSWORDS'
        })
    snmp_v3_scheme = Column(
        'v3scheme',
        SNMPV3SchemeField.db_type(),
        Comment('SNMPv3 security level'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('SNMPv3 Security Level'),
            'read_cap': 'DEVICES_PASSWORDS',
            'write_cap': 'DEVICES_PASSWORDS'
        })
    snmp_v3_auth_protocol = Column(
        'v3authproto',
        SNMPV3ProtoField.db_type(),
        Comment('SNMPv3 authentication protocol'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('SNMPv3 Authentication Protocol'),
            'read_cap': 'DEVICES_PASSWORDS',
            'write_cap': 'DEVICES_PASSWORDS'
        })
    snmp_v3_auth_passphrase = Column(
        'v3authpass',
        ASCIIString(255),
        Comment('SNMPv3 authentication passphrase'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('SNMPv3 Authentication Passphrase'),
            'secret_value': True,
            'editor_xtype': 'passwordfield',
            'read_cap': 'DEVICES_PASSWORDS',
            'write_cap': 'DEVICES_PASSWORDS'
        })
    snmp_v3_privacy_protocol = Column(
        'v3privproto',
        SNMPV3PrivProtoField.db_type(),
        Comment('SNMPv3 privacy protocol'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('SNMPv3 Privacy Protocol'),
            'read_cap': 'DEVICES_PASSWORDS',
            'write_cap': 'DEVICES_PASSWORDS'
        })
    snmp_v3_privacy_passphrase = Column(
        'v3privpass',
        ASCIIString(255),
        Comment('SNMPv3 privacy passphrase'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('SNMPv3 Privacy Passphrase'),
            'secret_value': True,
            'editor_xtype': 'passwordfield',
            'read_cap': 'DEVICES_PASSWORDS',
            'write_cap': 'DEVICES_PASSWORDS'
        })
    management_type = Column(
        'mgmttype',
        SNMPV3MgmtTypeField.db_type(),
        Comment('Management access type'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Management Type'),
            'read_cap': 'DEVICES_PASSWORDS',
            'write_cap': 'DEVICES_PASSWORDS'
        })
    management_user = Column(
        'mgmtuser',
        Unicode(255),
        Comment('Management user name'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Management User'),
            'read_cap': 'DEVICES_PASSWORDS',
            'write_cap': 'DEVICES_PASSWORDS'
        })
    management_password = Column(
        'mgmtpass',
        Unicode(255),
        Comment('Management password'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Management Password'),
            'secret_value': True,
            'editor_xtype': 'passwordfield',
            'read_cap': 'DEVICES_PASSWORDS',
            'write_cap': 'DEVICES_PASSWORDS'
        })
    management_enable_password = Column(
        'mgmtepass',
        Unicode(255),
        Comment('Management enable password'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Management Enable Password'),
            'secret_value': True,
            'editor_xtype': 'passwordfield',
            'read_cap': 'DEVICES_PASSWORDS',
            'write_cap': 'DEVICES_PASSWORDS'
        })
    remote_id = Column(
        'remoteid',
        VARBINARY(134),
        Comment('Binary agent remote ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Remote ID')
        })

    host = relationship(
        'Host',
        backref=backref('network_devices',
                        passive_deletes=True))

    def get_handler(self):
        devtype = self.device_type
        if devtype is None:
            return None
        hdlname = devtype.handler
        if not hdlname:
            return None
        itp = list(pkg_resources.iter_entry_points(
                'netprofile.devices.handlers', hdlname))
        if len(itp) == 0:
            return None
        cls = itp[0].load()
        return cls(devtype, self)

    def snmp_context(self, is_rw=False):
        snmp_type = self.snmp_type
        if snmp_type is None:
            raise RuntimeError('SNMP is not configured for a device')
        host = self.host
        # TODO: Make prefer-v4 / prefer-v6 configurable
        # TODO: Provide finer-grained control of chosen addresses
        # TODO: allow specifying custom SNMP port
        # TODO: allow configuring snimpy parameters:
        #       cache, none, timeout, retries
        if not host:
            raise RuntimeError('Can\'t find host to connect to')
        if len(host.ipv4_addresses):
            addr = str(host.ipv4_addresses[0])
        elif len(host.ipv6_addresses):
            addr = str(host.ipv6_addresses[0])
        else:
            addr = str(host)

        kwargs = {'host': addr}
        if snmp_type == SNMPTypeField.v3:
            if self.snmp_v3_user is None:
                raise RuntimeError('SNMPv3 secName is unset')
            kwargs.update(version=3,
                          secname=self.snmp_v3_user)
            if self.snmp_v3_scheme in {SNMPV3SchemeField.authNoPriv,
                                       SNMPV3SchemeField.authPriv}:
                if self.snmp_v3_auth_protocol is None:
                    raise RuntimeError('SNMPv3 authProtocol is unset')
                if self.snmp_v3_auth_passphrase is None:
                    raise RuntimeError('SNMPv3 authPassword is unset')
                kwargs.update(authprotocol=self.snmp_v3_auth_protocol.value,
                              authpassword=self.snmp_v3_auth_passphrase)
            if self.snmp_v3_scheme == SNMPV3SchemeField.authPriv:
                if self.snmp_v3_privacy_protocol is None:
                    raise RuntimeError('SNMPv3 privProtocol is unset')
                if self.snmp_v3_privacy_passphrase is None:
                    raise RuntimeError('SNMPv3 privPassword is unset')
                kwargs.update(privprotocol=self.snmp_v3_privacy_protocol.value,
                              privpassword=self.snmp_v3_privacy_passphrase)
        else:
            comm = self.snmp_rw_community if is_rw else self.snmp_ro_community
            if comm is None:
                raise RuntimeError('Appropriate SNMP community string '
                                   'is not set')
            kwargs.update(version=1 if snmp_type == SNMPTypeField.v1 else 2,
                          community=comm)
        return snimpy.manager.Manager(**kwargs)

    @property
    def snmp_has_rw_context(self):
        if self.snmp_type not in {SNMPTypeField.v1, SNMPTypeField.v2c}:
            return False
        if not self.snmp_rw_community:
            return False
        if self.snmp_rw_community == self.snmp_ro_community:
            return False
        return True

    def grid_icon(self, req):
        return req.static_url(
                'netprofile_devices:static/img/device_network.png')

    def __str__(self):
        if self.host:
            return '%s: %s' % (str(self.device_type),
                               str(self.host))
        return super(NetworkDevice, self).__str__()


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
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICETYPES_LIST',
                'cap_create':    'FILES_ATTACH_2DEVICETYPES',
                'cap_edit':      '__NOPRIV__',
                'cap_delete':    'FILES_ATTACH_2DEVICETYPES',

                'menu_name':     _('Files'),
                'grid_view':     ('device_type', 'file'),
                'create_wizard': SimpleWizard(title=_('Attach file'))
            }
        })
    id = Column(
        'dtfid',
        UInt32(),
        Sequence('deveices_types_files_dtfid_seq'),
        Comment('DeviceType-file mapping ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    device_type_id = Column(
        'dtid',
        UInt32(),
        ForeignKey('devices_types_def.dtid',
                   name='devices_types_files_fk_dtid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Device type ID'),
        nullable=False,
        info={
            'header_string': _('Device Type'),
            'column_flex': 1
        })
    file_id = Column(
        'fileid',
        UInt32(),
        ForeignKey('files_def.fileid', name='devices_types_files_fk_fileid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('File ID'),
        nullable=False,
        info={
            'header_string': _('File'),
            'column_flex': 1,
            'editor_xtype': 'fileselect'
        })

    file = relationship(
        'File',
        innerjoin=True,
        backref=backref('linked_device_types',
                        cascade='all, delete-orphan',
                        passive_deletes=True))

    def __str__(self):
        return str(self.file)


class NetworkDeviceMediaType(Base):
    """
    Interface media type.

    Used by network devices to specify interfaces.
    """
    __tablename__ = 'netdev_media'
    __table_args__ = (
        Comment('Network device interfaces\' media types'),
        Index('netdev_media_u_name', 'name', unique=True),
        Index('netdev_media_i_iftype', 'iftype'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICETYPES_LIST',
                'cap_create':    'DEVICETYPES_EDIT',
                'cap_edit':      'DEVICETYPES_EDIT',
                'cap_delete':    'DEVICETYPES_EDIT',

                'show_in_menu':  'admin',
                'menu_name':     _('Media Types'),
                'grid_view':     ('ndmid', 'name', 'physical'),
                'grid_hidden':   ('ndmid',),
                'form_view':     ('name', 'iftype', 'iftype_alt',
                                  'physical', 'speed', 'descr'),
                'easy_search':   ('name', 'descr'),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new media type'))
            }
        })
    id = Column(
        'ndmid',
        UInt32(),
        Sequence('netdev_media_ndmid_seq'),
        Comment('Network device media ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Network device media name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 3
        })
    iftype = Column(
        UInt32(),
        Comment('IANA ifType MIB value'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('ifType')
        })
    iftype_alternate = Column(
        'iftype_alt',
        UInt32(),
        Comment('Alternate IANA ifType MIB value'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Alt. ifType')
        })
    is_physical = Column(
        'physical',
        NPBoolean(),
        Comment('Is media type physical'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string': _('Physical')
        })
    speed = Column(
        UInt64(),
        Comment('Fixed speed of the media (if any, in bps)'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Speed')
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Media type description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    def __str__(self):
        req = getattr(self, '__req__', None)
        name = self.name
        if req and name:
            name = req.localizer.translate(_(name))
        return str(name)


class NetworkDeviceInterface(Base):
    """
    Network device interface definition.
    """
    __tablename__ = 'netdev_ifaces'
    __table_args__ = (
        Comment('Network device interfaces'),
        Index('netdev_ifaces_u_devifname', 'did', 'name', unique=True),
        Index('netdev_ifaces_u_devifindex', 'did', 'index', unique=True),
        Index('netdev_ifaces_i_ndmid', 'ndmid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICES_LIST',
                'cap_create':    'DEVICES_EDIT',
                'cap_edit':      'DEVICES_EDIT',
                'cap_delete':    'DEVICES_EDIT',

                'menu_name':     _('Interfaces'),
                'grid_view':     ('ifid', 'device', 'media', 'name'),
                'grid_hidden':   ('ifid',),
                'form_view':     ('device', 'media', 'name', 'index', 'descr'),
                'easy_search':   ('name', 'descr'),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new interface'))
            }
        })
    id = Column(
        'ifid',
        UInt32(),
        Sequence('netdev_ifaces_ifid_seq'),
        Comment('Network device interface ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    device_id = Column(
        'did',
        UInt32(),
        ForeignKey('devices_network.did', name='netdev_ifaces_fk_did',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Network device ID'),
        nullable=False,
        info={
            'header_string': _('Device'),
            'filter_type': 'none',
            'column_flex': 2
        })
    media_id = Column(
        'ndmid',
        UInt32(),
        ForeignKey('netdev_media.ndmid', name='netdev_ifaces_fk_ndmid',
                   onupdate='CASCADE'),  # ondelete='RESTRICT'
        Comment('Network device media ID'),
        nullable=False,
        info={
            'header_string': _('Media'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    name = Column(
        Unicode(255),
        Comment('Interface name (filled manually or via SNMP)'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 3
        })
    index = Column(
        UInt32(),
        Comment('Interface SNMP ifIndex'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': 'ifIndex'
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Interface description (filled manually or via SNMP)'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    device = relationship(
        'NetworkDevice',
        innerjoin=True,
        backref=backref('interfaces',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    media = relationship(
        'NetworkDeviceMediaType',
        innerjoin=True,
        backref=backref('interfaces',
                        passive_deletes='all'))
    bindings = relationship(
        'NetworkDeviceBinding',
        backref=backref('interface', lazy='joined'),
        passive_deletes=True)

    def __str__(self):
        if self.device:
            return '%s: %s' % (str(self.device),
                               str(self.name))
        return str(self.name)


class NetworkDeviceBinding(Base):
    """
    Definition for customer binding to network device interface.
    """
    __tablename__ = 'netdev_bindings'
    __table_args__ = (
        Comment('Network device interface bindings'),
        Index('netdev_bindings_i_aeid', 'aeid'),
        Index('netdev_bindings_i_hostid', 'hostid'),
        Index('netdev_bindings_i_did', 'did'),
        Index('netdev_bindings_i_ifid', 'ifid'),
        Index('netdev_bindings_i_index', 'index'),
        Index('netdev_bindings_i_circuitid', 'circuitid'),
        Index('netdev_bindings_i_att_did', 'att_did'),
        Index('netdev_bindings_i_rateid', 'rateid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_DEVICES',
                'cap_read':      'DEVICES_LIST',
                'cap_create':    'DEVICES_EDIT',
                'cap_edit':      'DEVICES_EDIT',
                'cap_delete':    'DEVICES_EDIT',

                'menu_name':     _('Bindings'),
                'grid_view':     ('ndbid', 'device', 'interface',
                                  'access_entity', 'host'),
                'grid_hidden':   ('ndbid',),
                'form_view':     ('access_entity', 'host', 'device',
                                  'interface', 'index', 'circuitid',
                                  'rate',
                                  'att_cable', 'attached_device',
                                  'descr'),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new binding'))
            }
        })
    id = Column(
        'ndbid',
        UInt32(),
        Sequence('netdev_bindings_ndbid_seq'),
        Comment('Network device binding ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    access_entity_id = Column(
        'aeid',
        UInt32(),
        ForeignKey('entities_access.entityid', name='netdev_bindings_fk_aeid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Access entity ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Access Entity'),
            'filter_type': 'none',
            'column_flex': 3
        })
    host_id = Column(
        'hostid',
        UInt32(),
        ForeignKey('hosts_def.hostid', name='netdev_bindings_fk_hostid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Host ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Host'),
            'filter_type': 'none',
            'column_flex': 3
        })
    device_id = Column(
        'did',
        UInt32(),
        ForeignKey('devices_network.did', name='netdev_bindings_fk_did',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Device ID'),
        nullable=False,
        info={
            'header_string': _('Device'),
            'filter_type': 'none',
            'column_flex': 2
        })
    interface_id = Column(
        'ifid',
        UInt32(),
        ForeignKey('netdev_ifaces.ifid', name='netdev_bindings_fk_ifid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Network device interface ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Interface'),
            'filter_type': 'none',
            'column_flex': 2
        })
    index = Column(
        UInt32(),
        Comment('Interface SNMP ifIndex'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': 'ifIndex'
        })
    circuit_id = Column(
        'circuitid',
        VARBINARY(32),
        Comment('Binary agent circuit ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Circuit ID')
        })
    rate_id = Column(
        'rateid',
        UInt32(),
        ForeignKey('rates_def.rateid', name='netdev_bindings_fk_rateid',
                   onupdate='CASCADE'),  # ondelete=RESTRICT
        Comment('Optional rate ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Rate'),
            'filter_type': 'nplist'
        })
    cable_length = Column(
        'att_cable',
        UInt32(),
        Comment('Cable length (in meters)'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Cable Length')
        })
    attached_device_id = Column(
        'att_did',
        UInt32(),
        ForeignKey('devices_network.did', name='netdev_bindings_fk_att_did',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Attached device ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Device'),
            'filter_type': 'none'
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Network device binding description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    access_entity = relationship(
        'AccessEntity',
        backref=backref('interface_bindings',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    host = relationship(
        'Host',
        backref=backref('interface_bindings',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    device = relationship(
        'NetworkDevice',
        foreign_keys=device_id,
        innerjoin=True,
        backref=backref('interface_bindings',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    rate = relationship(
        'Rate',
        backref=backref('interface_bindings',
                        passive_deletes='all'))
    attached_device = relationship(
        'NetworkDevice',
        foreign_keys=attached_device_id,
        backref=backref('upstream_bindings',
                        passive_deletes=True))

    def __str__(self):
        return '%s → %s' % (str(self.interface),
                            str(self.host))
