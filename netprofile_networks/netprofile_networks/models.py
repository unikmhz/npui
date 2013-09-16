#!/usr/bin/env python
# -*- coding: utf-8 -*-

#netd_def.rtid references on non-existent table

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
    "Network",
    "NetworkGroup",
    "NetworkHostLinkage",
    "NetworkHostLinkageType",
    "SNMPScheme",
    "SNMPAuthProtocol",
    "SNMPCryptProtocol",
    "ManagementType",
    "NetworkDevice"
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

from netprofile_domains.models import Domain
from netprofile_devices.models import Device
from netprofile_hosts.models import Host

from pyramid.threadlocal import get_current_request
from pyramid.i18n import (
    TranslationStringFactory,
	get_localizer
        )

from IPy import IP
from mako.template import Template

_ = TranslationStringFactory('netprofile_networks')


class Network(Base):
    """
    Netprofile Network Description definition
    """
    __tablename__ = 'nets_def'
    __table_args__ = (
        Comment('Networks'),
        Index('nets_def_u_name', 'name', unique=True),
        Index('nets_def_u_ipaddr', 'ipaddr', unique=True),
        Index('nets_def_u_ip6addr', 'ip6addr', unique=True),
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
                'default_sort' : ({ 'property': 'name', 'direction': 'ASC' },),
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
                'form_view' : ('name', 'networkdomain', 'netgroup', 'networkdevice', 'enabled', 'public', 'ipaddr', 'ip6addr', 'cidr', 'cidr6', 'vlanid', 'rtid', 'gueststart', 'guestend', 'gueststart6', 'guestend6', 'descr'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new network'))
                }
            }
        )
    id = Column(
        'netid',
        UInt32(),
        Sequence('netid_seq'),
        Comment('Network ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    name = Column(
        'name',
        ASCIIString(),
        Comment('Network Name'),
        nullable=False,
        info={
            'header_string' : _('Name')
            }
        )
    domainid = Column(
        'domainid',
        UInt32(),
        #networkdomain
        ForeignKey('domains_def.domainid', name='nets_def_fk_domainid', onupdate='CASCADE'),
        nullable=False,
        info={
            'header_string' : _('Domain ID')
            }
        )
    netgid = Column(
        'netgid',
        UInt32(),
        #netgroup
        ForeignKey('nets_groups.netgid', name='nets_def_fk_domainid', onupdate='CASCADE'),
        nullable=False,
        info={
            'header_string' : _('Network Group ID')
            }
        )
    mgmtdid = Column(
        'mgmtdid',
        UInt32(),
        #networkdevice
        ForeignKey('devices_network.did', name='nets_def_fk_mgmtdid', onupdate='CASCADE'),
        nullable=False,
        info={
            'header_string' : _('Management Device ID')
            }
        )
    enabled = Column(
        NPBoolean(),
        Comment('Is network enabled?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string' : _('Is Network Enabled?')
            }
        )
    public = Column(
        NPBoolean(),
        Comment('Is network visible to outsiders?'),
        nullable=False,
        default=False,
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
        #foreignkey to RoutingTables, this module isn't ready yet. 
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

    network = relationship("NetworkHostLinkage", backref=backref('network', innerjoin=True))
    Domain.networkdomain = relationship('Network', backref=backref('networkdomain', innerjoin=True))

    def __str__(self):
        return self.name


class NetworkGroup(Base):
    """
    Netprofile Network Description definition
    """
    __tablename__ = 'nets_groups'
    __table_args__ = (
        Comment('Network Groups definition'),
        Index('nets_group_u_name', 'name', unique=True),
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
                'show_in_menu'  : 'admin',
                'menu_order'    : 70,
                'default_sort' : ({ 'property': 'netgid' ,'direction': 'ASC' },),
                'grid_view' : ('name', 'descr'),
                'form_view' : ('name', 'descr'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new network group'))
                }
            }
        )    
    id = Column(
        'netgid',
        UInt32(),
        Sequence('netgid_seq'),
        Comment('Network Group ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    name = Column(
        'name',
        ASCIIString(),
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


class NetworkHostLinkageType(Base):
    """
    Netprofile Network-Host Linkage Type definition
    """
    __tablename__ = 'nets_hltypes'
    __table_args__ = (
        Comment('Networks-Hosts Linkage Types'),
        Index('nets_hltypes_u_name', 'name', unique=True),
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
                'grid_view' : ('name', 'unique'),
                'form_view' : ('name', 'unique'),
                'easy_search' : ('name',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new network-host linkage type'))
                }
            }
        )    
    id = Column(
        'hltypeid',
        UInt32(),
        Sequence('hltypeid_seq'),
        Comment('Networks-Hosts Linkage Type ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('Type ID')
            }
        )
    name = Column(
        'name',
        ASCIIString(),
        Comment('Networks-Hosts Linkage Type Name'),
        nullable=False,
        info={
            'header_string' : _('Linkage Type Name')
            }
        )
    unique = Column(
        'unique',
        NPBoolean()
        Comment('Is unique per network?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string' : _('Is Unique?')
            }
        )
        
    linkage = relationship('NetworkHostLinkage', backref=backref('linkagetype', innerjoin=True))

    def __str__(self):
        return self.name

class NetworkHostLinkage(Base):
    """
    Netprofile Network Host Linkage definition
    """
    __tablename__ = 'nets_hosts'
    __table_args__ = (
        Comment('Networks-Hosts Linkage'),
        Index('nets_hosts_u_nhl', 'netid', 'hostid', 'hltypeid', unique=True),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                #'cap_menu'      : 'BASE_NAS',
                #'cap_read'      : 'NAS_LIST',
                #'cap_create'    : 'NAS_CREATE',
                #'cap_edit'      : 'NAS_EDIT',
                #'cap_delete'    : 'NAS_DELETE',
                'menu_name'    : _('Network-Host Linkage'),
                'show_in_menu'  : 'admin', #modules
                'menu_order'    : 60,
                'default_sort' : ({ 'property': 'nhid' ,'direction': 'ASC' },),
                'grid_view' : ('network', 'networklinkagehost', 'linkagetype'),
                'form_view' : ('network', 'networklinkagehost', 'linkagetype'),
                'easy_search' : ('network',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new network-host linkage'))
                }
            }
        )
    id = Column(
        'nhid',
        UInt32(),
        Sequence('nhid_seq'),
        Comment('Network-Host Linkage ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    netid = Column(
        'netid',
        UInt32(),
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
        UInt32(),
        Comment('Host ID'),
        #networklinkagehost
        ForeignKey('hosts_def.hostid', name='nets_hosts_fk_hostid', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=False,
        info={
            'header_string' : _('Host ID')
            }
        )
    hltypeid = Column(
        'hltypeid',
        UInt32(),
        #linkagetype
        ForeignKey('nets_hltypes.hltypeid', name='nets_hosts_fk_hltypeid', onupdate='CASCADE'),
        Comment('Network-Host Linkage Type'),
        nullable=False,
        info={
            'header_string' : _('Type ID')
            }
        )
    
    Host.networklinkagehost = relationship('NetworkHostLinkage', backref=backref('networklinkagehost', innerjoin=True))

    def __str__(self):
        return "{0}-{1}".format(self.netid, self.hostid)


class SNMPType(DeclEnum):
    v1 = 'v1', _('Version 1'), 10
    v2 = 'v2', _('Version 2'), 20
    v3 = 'v3', _('Version 3'), 30


class SNMPScheme(DeclEnum):
    noAuthNoPriv = 'noAuthNoPriv', _('Not authorized, no privileges'), 10
    authNoPriv = 'authNoPriv', _('Authorized, no privileges'), 20
    authPriv = 'authPriv', _('Authorized, privileged'), 30


class SNMPAuthProtocol(DeclEnum):
    md5 = 'MD5', _('MD5'), 10
    sha = 'SHA', _('SHA'), 20


class SNMPCryptProtocol(DeclEnum):
    des = 'DES', _('DES'), 10
    aes128 = 'AES128', _('AES128'), 20
    aes192 = 'AES192', _('AES192'), 30 
    aes256 = 'AES256', _('AES256'), 40

class ManagementType(DeclEnum):
    ssh = 'ssh', _('ssh'), 10
    telnet = 'telnet', _('telnet'), 20
    vnc = 'vnc', _('vnc'), 30
    rdp = 'rdp', _('rdp'), 40


class NetworkDevice(Base):
    """
    Netprofile Network Device definition
    """
    __tablename__ = 'devices_network'
    __table_args__ = (
        Comment('Network Devices'),
        Index('devices_network_u_hostid', 'hostid', unique=True),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                'menu_name'    : _('Network Device'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 70,
                'default_sort' : ({ 'property': 'did' ,'direction': 'ASC' },),
                'grid_view' : ('netdevice', 'networkdevicehost'),
                'form_view' : ('netdevice', 'networkdevicehost', 'snmptype', 'mgmtpass', 'mgmtepass'),
                'easy_search' : ('did',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new network device'))
                }
            }
        )
    did = Column(
        'did',
        UInt32(),
        Sequence('did_seq'),
        Comment('Device ID'),
        #netdevice
        ForeignKey('devices_def.did', name='devices_network_fk_did', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('Device')
            }
        )
    hostid = Column(
        'hostid',
        UInt32(),
        Comment('Host ID'),
        #networkdevicehost
        ForeignKey('hosts_def.hostid', name='devices_network_fk_hostid', ondelete='SET NULL', onupdate='CASCADE'),
        nullable=False,
        info={
            'header_string' : _('Host')
            }
        )
    snmptype = Column(
        'snmptype',
        SNMPType.db_type(),
        Comment('SNMP Access Type'),
        info={
            'header_string' : _('SNMP type')
            }
        )
    v2readonly = Column(
        'cs_ro',
        ASCIIString(),
        Comment('SNMPv2 Read-Only Community'),
        info={
            'header_string' : _('SNMPv2 Read Only')
            }
        )
    v2readwrite = Column(
        'cs_rw',
        ASCIIString(),
        Comment('SNMPv2 Read-Write Community'),
        info={
            'header_string' : _('SNMPv2 Read-Write')
            }
        )
    v3user = Column(
        'v3user',
        ASCIIString(),
        Comment('SNMPv3 User Name'),
        info={
            'header_string' : _('SNMPv3 User Name')
            }
        )
    v3scheme = Column(
        'v3scheme',
        SNMPScheme.db_type(),
        Comment('SNMPv3 Connection Level'),
        info={
            'header_string' : 'Connection level'
            }
        )
    v3authproto = Column(
        'v3authproto',
        SNMPAuthProtocol.db_type(),
        Comment('SNMPv3 Auth Protocol'),
        info={
            'header_string' : 'Auth protocol'
            }
        )
    v3authpass = Column(
        'v3authpass',
        ASCIIString(),
        Comment('SNMPv3 Auth Passphrase'),
        info={
            'header_string' : 'Passphrase'
            }
        )
    v3privproto = Column(
        'v3privproto',
        SNMPCryptProtocol.db_type(),
        Comment('SNMPv3 Crypt Protocol'),
        info={
            'header_string' : 'Crypt protocol'
            }
        )
    v3privpass = Column(
        'v3privpass',
        ASCIIString(),
        Comment('SNMPv3 Crypt Passphrase'),
        info={
            'header_string' : 'Crypt Passphrase'
            }
        )
    mgmttype = Column(
        'mgmttype',
        ManagementType.db_type(),
        Comment('Management Access Type'),
        info={
            'header_string' : 'Management access type'
            }
        )
    mgmtuser = Column(
        'mgmtuser',
        ASCIIString(),
        Comment('Management User Name'),
        info={
            'header_string' : 'Management User Name'
            }
        )
    mgmtpass = Column(
        'mgmtpass',
        ASCIIString(),
        Comment('Management Password'),
        info={
            'header_string' : 'Management Password'
            }
        )
    mgmtepass = Column(
        'mgmtepass',
        ASCIIString(),
        Comment('Management Enablement Password'),
        info={
            'header_string' : 'Enabled password'
            }
        )
    networkdevice = relationship('Network', backref=backref('networkdevice', innerjoin=True))
    Host.networkdevicehost = relationship('NetworkDevice', backref=backref('networkdevicehost', innerjoin=True))
    Device.netdevice = relationship('NetworkDevice', backref=backref('netdevice', innerjoin=True))

    def __str__(self):
        return "{0}".format(self.did)
    
