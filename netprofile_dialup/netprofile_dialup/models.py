#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
    'NAS',
    'IPPool',
    'NASPool',
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

_ = TranslationStringFactory('netprofile_dialup')


class NAS(Base):
    """
    NetProfile Network Access Server definition
    """
    __tablename__ = 'nas_def'
    __table_args__ = (
        Comment('Network Access Servers'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_NAS',
                #'cap_read'      : 'NAS_LIST',
                #'cap_create'    : 'NAS_CREATE',
                #'cap_edit'      : 'NAS_EDIT',
                #'cap_delete'    : 'NAS_DELETE',
                'menu_name'    : _('Network Access Servers'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 90,
                'default_sort' : ({ 'property': 'nasid' ,'direction': 'ASC' },),
                'grid_view' : ('idstr',),
                'form_view' : ('idstr', 'descr'),
                'easy_search' : ('idstr',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new NAS'))
                }
            }
        )

    nasid = Column(
        'nasid',
        UInt32(10),
        Comment('Network Access Server ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )

    idstr = Column(
        'idstr',
        Unicode(255),
        Comment('Network Access Server Identification String'),
        unique=True,
        nullable=False,
        info={
            'header_string' : _('ID string')
            }
        )

    descr  = Column(
        'descr',
        UnicodeText(),
        Comment('Network Access Server Description'),
        info={
            'header_string' : _('Description')
            }
        )

    #here will be a relationship with nas_pools
    network_access_servers = relationship("NASPool", backref=backref('naservers', innerjoin=True))

class IPPool(Base):
    """
    IP Address Pools
    """

    __tablename__ = 'ippool_def'
    __table_args__ = (
        Comment('IP Address Pools'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_IPPOOL',
                #'cap_read'      : 'IPPOOL_LIST',
                #'cap_create'    : 'IPPOOL_CREATE',
                #'cap_edit'      : 'IPPOOL_EDIT',
                #'cap_delete'    : 'IPPOOL_DELETE',
                'menu_name'    : _('IP Address Pools'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 90,
                'default_sort' : ({ 'property': 'poolid' ,'direction': 'ASC' },),
                'grid_view' : ('name',),
                'form_view' : ('name', 'descr'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new IP address pool'))
                }
            }
        )

    poolid = Column(
        'poolid',
        UInt32(10),
        Comment('IP Address Pool ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )

    name = Column(
        'name',
        Unicode(255),
        Comment('IP Address Pool Name'),
        unique=True,
        nullable=False,
        info={
            'header_string' : _('Name')
            }
        )

    descr  = Column(
        'descr',
        UnicodeText(),
        Comment('IP Address Pool Description'),
        info={
            'header_string' : _('Description')
            }
        )

    #here will be a relationship with nas_pools
    ip_pools = relationship("NASPool", backref=backref('ippools', innerjoin=True))
    ip_pools_elements = relationship("Rates", backref=backref('ippoolselements', innerjoin=True))

class NASPool(Base):
    """
    NAS IP Pools
    """

    __tablename__ = 'nas_pools'
    __table_args__ = (
        Comment('NAS IP Pools'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_NAS',
                #'cap_read'      : 'NAS_LIST',
                #'cap_create'    : 'NAS_CREATE',
                #'cap_edit'      : 'NAS_EDIT',
                #'cap_delete'    : 'NAS_DELETE',
                'menu_main': True,
                'menu_name'    : _('NAS IP Pools'),
                'show_in_menu'  : 'modules',
                'menu_order'    :90,
                'default_sort' : ({ 'property': 'nasid' ,'direction': 'ASC' },),
                'grid_view' : ('naservers','ippools'),
                'form_view' : ('naservers', 'ippools'),
                'easy_search' : ('npid', 'naservers', 'ippools'),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new NAS IP pool'))
                }
            }
        )

    npid = Column(
        'npid',
        UInt32(10),
        Comment('NAS IP Pool ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('NAS IP Pool Linkage ID')
            }
        )
    
    nasid = Column(
        'nasid',
        UInt32(10),
        ForeignKey('nas_def.nasid', name='nas_pools_fk_nasid', onupdate='CASCADE'),
        Comment('Network Access Server ID'),
        nullable=False,
        info={
            'header_string' : _('Network Access Server')
            }
        )

    poolid = Column(
        'poolid',
        UInt32(10),
        ForeignKey('ippool_def.poolid', name='nas_pools_fk_poolid', onupdate='CASCADE'),
        Comment('IP Address Pool ID'),
        nullable=False,
        info={
            'header_string' : _('IP Address Pool')
            }
        )

