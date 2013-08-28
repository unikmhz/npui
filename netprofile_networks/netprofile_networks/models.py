#!/usr/bin/env python
# -*- coding: utf-8 -*-

#netd_def.rtid references on non-existent table
# перевести
# установить
# закоммитить

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

#тут возвращаем названия классов
__all__ = [
    "IsNetworkEnabled",
    "IsPublic",
    "IsUnique",
    "Network",
    "NetworkGroup",
    "NetworkHostLinkage",
    "NetworkHost"
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
    validates,
    )

from sqlalchemy.ext.associationproxy import association_proxy

from sqlalchemy.ext.hybrid import hybrid_property

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
    npbool,
    IPv4Address,
    IPv6Address
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

from IPy import IP
from mako.template import Template

_ = TranslationStringFactory('netprofile_networks')


class IsNetworkEnabled(DeclEnum):
    """
    Is Network Enabled class
    """
    yes   = 'Y',   _('Yes'),   10
    no   = 'N',   _('No'),   20


class IsPublic(DeclEnum):
    """
    Is Network Visible To Outsiders class
    """
    yes   = 'Y',   _('Yes'),   10
    no   = 'N',   _('No'),   20

class IsUnique(DeclEnum):
    """
    Is Networks-Hosts Linkage Type unique per network class
    """
    yes   = 'Y',   _('Yes'),   10
    no   = 'N',   _('No'),   20


class Network(Base):
    """
    Netprofile Network Description definition
    """
    __tablename__ = 'nets_def'
    __table_args__ = (
        Comment('Networks'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_NAS',
                #'cap_read'      : 'NAS_LIST',
                #'cap_create'    : 'NAS_CREATE',
                #'cap_edit'      : 'NAS_EDIT',
                #'cap_delete'    : 'NAS_DELETE',
                'menu_name'    : _('Networks'),
                'show_in_menu'  : 'modules', #modules
                'menu_order'    : 70,
                'menu_main'     : True,
                'default_sort' : ({ 'property': 'netid' ,'direction': 'ASC' },),
                'grid_view' : ('name',
                               'ipaddr',
                               MarkupColumn(
                               name='state',
                               header_string=_('State'),
                               template=TemplateObject('netprofile_networks:templates/networks_icons.mak'),
                               column_width=60,
                               column_resizable=False
                               )
                               ),
                'form_view' : ('netid', 'name', 'netdomain', 'netgroup', 'mgmtdid', 'enabled', 'public', 'ipaddr', 'ip6addr', 'cidr', 'cidr6', 'vlanid', 'rtid', 'gueststart', 'guestend', 'gueststart6', 'guestend6', 'descr'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new network'))
                }
            }
        )
    netid = Column(
        'netid',
        UInt32(10),
        Comment('Network ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    name = Column(
        'name',
        Unicode(255),
        Comment('Network Name'),
        nullable=False,
        info={
            'header_string' : _('Name')
            }
        )
    domainid = Column(
        'domainid',
        UInt32(10),
        #netdomain
        ForeignKey('domains_def.domainid', name='nets_def_fk_domainid', onupdate='CASCADE'),
        nullable=False,
        info={
            'header_string' : _('Domain ID')
            }
        )
    netgid = Column(
        'netgid',
        UInt32(10),
        #netgroup
        ForeignKey('nets_groups.netgid', name='nets_def_fk_domainid', onupdate='CASCADE'),
        nullable=False,
        info={
            'header_string' : _('Netgork Group ID')
            }
        )
    mgmtdid = Column(
        'mgmtdid',
        UInt32(10),
        #netdevice
        ForeignKey('devices_network.did', name='nets_def_fk_mgmtdid', onupdate='CASCADE'),
        nullable=False,
        info={
            'header_string' : _('Management Device ID')
            }
        )
    enabled = Column(
        #'enabled',
        NPBoolean(),
        #IsNetworkEnabled.db_type(),
        Comment('Is network enabled?'),
        nullable=False,
        default=False,#IsNetworkEnabled.yes,
        server_default=npbool(False),
        info={
            'header_string' : _('Is Network Enabled?')
            }
        )
    public = Column(
        NPBoolean(),
        #'public',
        #IsPublic.db_type(),
        Comment('Is network visible to outsiders?'),
        nullable=False,
        default=False,
        #default=IsPublic.yes,
        server_default=npbool(False),
        info={
            'header_string' : _('Is Public?')
            }
        )
    ipaddr = Column(
        'ipaddr',
        IPv4Address(10),
        Comment('Network IP Address'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('IP Address')
            }
        )
    ip6addr = Column(
        'ip6addr',
        IPv6Address(39),
        Comment('Network IPV6 Address'),
        info={
            'header_string' : _('IPV6 Address')
            }
        )
    cidr = Column(
        'cidr',
        UInt8(2),
        Comment('Network CIDR Number'),
        nullable=False,
        default=24,
        info={
            'header_string' : _('Network mask')
            }
        )
    cidr6 = Column(
        'cidr6',
        UInt8(3),
        Comment('Network CIDR6 Number'),
        nullable=False,
        default=64,
        info={
            'header_string' : _('IPv6 netmask')
            }
        )
    vlanid = Column(
        'vlanid',
        UInt8(4),
        Comment('Network VLAN ID'),
        nullable=False,
        default=0,
        info={
            'header_string' : _('VLAN ID')
            }
        )
    rtid = Column(
        'rtid',
        #foreignkey to RoutingTables, этого модуля еще нет. 
        UInt8(10),
        Comment('Route Table ID'),
        info={
            'header_string' : _('Route Table ID')
            }
        )
    gueststart = Column(
        'gueststart',
        UInt8(5),
        Comment('Start of Guest Allocation Area'),
        info={
            'header_string' : _('Start of Guest Allocation Area')
            }
        )
    guestend = Column(
        'guestend',
        UInt8(5),
        Comment('End of Guest Allocation Area'),
        info={
            'header_string' : _('End of Guest Allocation Area')
            }
        )
    gueststart6 = Column(
        'gueststart6',
        UInt8(5),
        Comment('Start of Guest Allocation Area'),
        info={
            'header_string' : _('Start of Guest Allocation Area (IPV6)')
            }
        )
    guestend6 = Column(
        'guestend6',
        UInt8(5),
        Comment('End of Guest Allocation Area'),
        info={
            'header_string' : _('End of Guest Allocation Area (IPV6)')
            }
        )
    descr = Column(
        'descr',
        UnicodeText(),
        Comment('Network Description'),
        info={
            'header_string' : _('Description')
            }
        )
    

    network = relationship("NetworkHost", backref=backref('network', innerjoin=True))


    def __str__(self):
        return self.name

    def __repr__(self):
        return "123 {0}".format(self.ipaddr)


class NetworkGroup(Base):
    """
    Netprofile Network Description definition
    """
    __tablename__ = 'nets_groups'
    __table_args__ = (
        Comment('Network Groups definition'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_NAS',
                #'cap_read'      : 'NAS_LIST',
                #'cap_create'    : 'NAS_CREATE',
                #'cap_edit'      : 'NAS_EDIT',
                #'cap_delete'    : 'NAS_DELETE',
                'menu_name'    : _('Network Groups'),
                'show_in_menu'  : 'admin', #modules
                'menu_order'    : 70,
                'default_sort' : ({ 'property': 'netgid' ,'direction': 'ASC' },),
                #дописать после описания столбцов
                'grid_view' : ('name', 'descr'),
                'form_view' : ('name', 'descr'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new network group'))
                }
            }
        )    
    netgid = Column(
        'netgid',
        UInt32(10),
        Comment('Network Group ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    name = Column(
        'name',
        Unicode(255),
        Comment('Network Group Name'),
        nullable=False,
        info={
            'header_string' : _('Network Group Name')
            }
        )
    descr = Column(
        'descr',
        UnicodeText(),
        Comment('Network Group Description'),
        info={
            'header_string' : _('Network Group Description')
            }
        )
    netgroups = relationship("Network", backref=backref('netgroup', innerjoin=True))

    def __str__(self):
        return self.name


class NetworkHostLinkage(Base):
    """
    Netprofile Network-Host Linkage definition
    """
    __tablename__ = 'nets_hltypes'
    __table_args__ = (
        Comment('Networks-Hosts Linkage Types'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_NAS',
                #'cap_read'      : 'NAS_LIST',
                #'cap_create'    : 'NAS_CREATE',
                #'cap_edit'      : 'NAS_EDIT',
                #'cap_delete'    : 'NAS_DELETE',
                'menu_name'    : _('Networks-Hosts Linkage Types'),
                'show_in_menu'  : 'admin', 
                'menu_order'    : 60,
                'default_sort' : ({ 'property': 'hltypeid' ,'direction': 'ASC' },),
                #дописать после описания столбцов
                'grid_view' : ('hltypeid', 'name', 'unique'),
                'form_view' : ('hltypeid', 'name', 'unique'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new network-host linkage type'))
                }
            }
        )    
    hltypeid = Column(
        'hltypeid',
        UInt32(10),
        Comment('Networks-Hosts Linkage Type ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    name = Column(
        'name',
        Unicode(255),
        Comment('Networks-Hosts Linkage Type Name'),
        nullable=False,
        info={
            'header_string' : _('Linkage Type Name')
            }
        )
    unique = Column(
        'unique',
        IsUnique.db_type(),
        Comment('Is unique per network?'),
        nullable=False,
        default=IsNetworkEnabled.no,
        info={
            'header_string' : _('Is Unique?')
            }
        )
        
    linkage = relationship('NetworkHost', backref=backref('linkage', innerjoin=True))

    def __str__(self):
        return self.name

class NetworkHost(Base):
    """
    Netprofile Network Host Description definition
    """
    __tablename__ = 'nets_hosts'
    __table_args__ = (
        Comment('Network Hosts definition'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_NAS',
                #'cap_read'      : 'NAS_LIST',
                #'cap_create'    : 'NAS_CREATE',
                #'cap_edit'      : 'NAS_EDIT',
                #'cap_delete'    : 'NAS_DELETE',
                'menu_name'    : _('Network Host'),
                'show_in_menu'  : 'admin', #modules
                'menu_order'    : 60,
                'default_sort' : ({ 'property': 'nhid' ,'direction': 'ASC' },),
                #дописать после описания столбцов
                'grid_view' : ('network', 'hostid', 'linkage'),
                'form_view' : ('network', 'hostid', 'linkage'),
                'easy_search' : ('network',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new network host'))
                }
            }
        )
    nhid = Column(
        'nhid',
        UInt32(10),
        Comment('Network-Host Linkage ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    netid = Column(
        'netid',
        UInt32(10),
        #network
        ForeignKey('nets_def.netid', name='nets_hosts_fk_netid', ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Network ID'),
        nullable=False,
        info={
            'header_string' : _('Network ID')
            }
        )
    hostid = Column(
        'hostid',
        UInt32(10),
        Comment('Host ID'),
        #hosts_def еще не готова
        #  CONSTRAINT `nets_hosts_fk_hostid` FOREIGN KEY (`hostid`) REFERENCES `hosts_def` (`hostid`) ON DELETE CASCADE ON UPDATE CASCADE,
        nullable=False,
        info={
            'header_string' : _('Host ID')
            }
        )
    hltypeid = Column(
        'hltypeid',
        UInt32(10),
        #linkage
        ForeignKey('nets_hltypes.hltypeid', name='nets_hosts_fk_hltypeid', onupdate='CASCADE'),
        Comment('Network-Host Linkage Type'),
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    
    def __str__(self):
        return "{0}-{1}".format(self.netid, self.hostid)
