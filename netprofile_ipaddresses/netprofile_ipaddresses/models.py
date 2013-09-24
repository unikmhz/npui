#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
    'IPAddressVisibility',
    'IPAddressAction',
    'IPAddress',
    'IPAddressHistory',
    'IPAddressFlat'
]

from sqlalchemy import (
	Column,
	Date,
	ForeignKey,
	Index,
	Sequence,
	Unicode,
	UnicodeText,
	text,
	Text,
	TIMESTAMP, 
	BINARY,
	FetchedValue,
	func
)

from sqlalchemy.orm import (
	backref,
	relationship
)

from sqlalchemy.ext.associationproxy import association_proxy

from netprofile.db.connection import Base
from netprofile.db.fields import (
	ASCIIString,
	ASCIIText,
	ASCIITinyText,
	DeclEnum,
	NPBoolean,
	UInt8,
	UInt16,
	UInt32,
	npbool,
	IPv4Address,
	ExactUnicode,
	MACAddress
)


from netprofile.db.ddl import Comment
from netprofile.tpl import TemplateObject
from netprofile.ext.columns import MarkupColumn
from netprofile.ext.wizards import (
	SimpleWizard,
	Step,
	Wizard
)

from netprofile_hosts import Host
from netprofile_dialup import IPPool
from netprofile_networks import Network
from netprofile_domains import Domain


from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

_ = TranslationStringFactory('netprofile_ipaddresses')


class IPAddressVisibility(DeclEnum):
    """
    IP Address Visibility class 
    """

    B = 'B', _('Both'), 10
    I = 'I', _('Internal'), 20
    E = 'E', _('External'), 30


class IPAddressAction(DeclEnum):
    """
    IPAddress action class
    """
    
    added = 'A', _('Added'), 10
    modified = 'M', _('Modified'), 20
    deleted = 'D', _('Deleted'), 30


class IPAddress(Base):
    """
    Netprofile IPAddress definition
    """
    __tablename__ = 'ipaddr_def'
    __table_args__ = (
        Comment('IP Addresses'),
        Index('ipaddr_def_u_address', 'netid', 'offset', unique=True),
        Index('ipaddr_def_i_hostid', 'hostid'),
        Index('ipaddr_def_i_poolid', 'poolid'),
        Index('ipaddr_def_i_inuse', 'inuse'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                'menu_name'    : _('IP addresses'),
                'show_in_menu'  : 'modules',
                'menu_order'    : 20,
                'menu_main'     : True,
                'grid_view' : ('host', 'network', 'hwaddr'),
                'form_view' : ('host', 'pool', 'network', 'offset', 'hwaddr'),
                'easy_search' : ('host_id',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new IP address'))
                }
            }
        )

    id = Column(
        'ipaddrid',
        UInt32(),
        Sequence('ipaddrid_seq'),
        Comment('IP Address ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    host_id = Column(
        'hostid',
        UInt32(),
        ForeignKey('hosts_def.hostid', name='ipaddr_def_fk_hostid', onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Host ID'),
        nullable=False,
        info={
            'header_string' : _('Host')
            }
        )
    pool_id = Column(
        'poolid',
        UInt32(),
        ForeignKey('ippool_def.poolid', name='ipaddr_def_fk_poolid', onupdate='CASCADE', ondelete='SET NULL'),
        Comment('IP Address Pool ID'),
        info={
            'header_string' : _('Pool')
            }
        )
    net_id = Column(
        'netid',
        UInt32(),
        ForeignKey('nets_def.netid', name='ipaddr_def_fk_netid', onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Network ID'),
        nullable=False,
        info={
            'header_string' : _('Network')
            }
        )
    offset = Column(
        'offset',
        UInt32(),
        Comment('Offset from Network Start'),
        info={
            'header_string' : _('Offset from Network Start')
            }
        )
    hwaddr = Column(
        'hwaddr',
        MACAddress(17),
        Comment('Hardware Address'),
        nullable=False,
        info={
            'header_string' : _('Hardware Address')
            }
        )
    ttl = Column(
        'ttl',
        UInt32(),
        Comment('RR Time to Live'),
        info={
            'header_string' : _('RR Time to Live')
            }
        )
    visibility = Column(
        'vis',
        IPAddressVisibility.db_type(),
        Comment('IP Address Visibility'),
        nullable=False,
        default=IPAddressVisibility.B,
        info={
            'header_string' : _('IP Visibslity')
            }
        )
    owned = Column(
        'owned',
        NPBoolean(),
        Comment('Is Statically Assigned?'),
        nullable=False,
        default=False,
        info={
            'header_string' : _('Is Statically Assigned?')
            }
        )
    in_use = Column(
        'inuse',
        NPBoolean(),
        Comment('Is this IP address in use?'),
        nullable=False,
        default=False,
        info={
            'header_string' : _('In Use')
            }
        )

    host = relationship('Host', backref=backref('ipaddrhost', innerjoin=True))
    pool = relationship('IPPool', backref=backref('ipaddrpool'))
    network = relationship('Network', backref=backref('ipaddrnetwork', innerjoin=True))

    def __str__(self):
        return "{0} - {1}".format(self.host, self.network)

class IPAddressHistory(Base):
    """
    Netprofile History of IP Address Entries
    """
    __tablename__ = 'ipaddr_history'
    __table_args__ = (
        Comment('IP Addresses'),
		Index('ipaddr_history_i_ipaddr', 'ipaddr', unique=True),
		Index('ipaddr_history_i_hwaddr', 'hwaddr'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                'menu_name'    : _('IP addresses history'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 20,
                'default_sort' : ({ 'property': 'hostname' ,'direction': 'ASC' },),
                'grid_view' : ('ipaddr', 'hwaddr', 'hostname', 'action'),
                'form_view' : ('ipaddr', 'hwaddr', 'hostname', 'action'),
                'easy_search' : ('hostname',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new event'))
                }
            }
        )
    ipaddr = Column(
        'ipaddr',
        IPv4Address(),
        Comment('IP Address'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('IP Address')
            }
        )
    hwaddr = Column(
        'hwaddr',
        MACAddress(17),
        Comment('Hardware Address'),
        nullable=False,
        info={
            'header_string' : _('Hardware Address')
            }
        )
    hostname = Column(
        'hostname',
        Unicode(255),
        Comment('Host Name'),
        info={
            'header_string' : _('Host Name')
            }
        )
    action = Column(
        'action',
        IPAddressAction.db_type(),
        Comment('Added / Modified / Deleted'),
        nullable=False,
        default=IPAddressAction.added,
        info={
            'header_string' : _('Action')
            }
        )

    def __str__(self):
        return "{0}".format(self.ipaddr)


class IPAddressFlat(Base):
    """
    IP Addresses view
    """
    __tablename__ = 'ipaddr_flat'
    __table_args__ = (
        Comment('IP Addresses Flat'),
        {
            'mysql_engine'  : 'InnoDB',
            'mysql_charset' : 'utf8',
            'info'          : {
                'menu_name'    : _('IP addresses'),
                'show_in_menu'  : 'admin',
                'menu_order'    : 20,
                'menu_main'     : False,
                'default_sort' : ({ 'property': 'hostname' ,'direction': 'ASC' },),
                'grid_view' : ('flathost', 'flatnetwork', 'flatdomain', 'ip', 'hwaddr'),
                'form_view' : ('flathost', 'flatnetwork', 'flatdomain', 'flatparent', 'ip', 'hwaddr'),
                'easy_search' : ('hostname',),
                'detail_pane'   : ('netprofile_core.views', 'dpane_simple'),
                'create_wizard' : SimpleWizard(title=_('Add new IP address'))
                }
            }
        )
    id = Column(
        'ipaddrid',
        UInt32(),
        Sequence('ipaddrid_seq'),
        Comment('IP Address ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string' : _('ID')
            }
        )
    hostid = Column(
        'hostid',
        UInt32(),
        ForeignKey('hosts_def.hostid', name='ipaddr_def_fk_hostid', onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Host ID'),
        nullable=False,
        info={
            'header_string' : _('Host')
            }
        )
    netid = Column(
        'netid',
        UInt32(),
        ForeignKey('nets_def.netid', name='ipaddr_def_fk_netid', onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Network'),
        nullable=False,
        info={
            'header_string' : _('Network')
            }
        )
    domainid = Column(
        'domainid',
        UInt32(),
        ForeignKey('domains_def.domainid', name='domains_aliases_fk_domainid', ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Domain'),
        nullable=False,
        info={
            'header_string' : _('Domain')
            }
        )
    hostname = Column(
        'hostname',
        Unicode(255),
        Comment('Host name'),
        nullable=False,
        info={
            'header_string' : _('Hostname')
            }
        )
    domainparent = Column(
        'dp',
        UInt32(),
        ForeignKey('domains_def.domainid', name='domains_aliases_fk_parentid', ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Parent domain ID'),
        info={
            'header_string' : _('Parent domain')
            }
        )
    ip = Column(
        'ip',
        ASCIIString(),
        Comment('IP Address'),
        info={
            'header_string' : _('IP Address')
            }
        )
    hwaddr = Column(
        'hwaddr',
        MACAddress(17),
        Comment('Hardware Address'),
        nullable=False,
        info={
            'header_string' : _('Hardware Address')
            }
        )

    flathost = relationship('Host', backref=backref('flathost', innerjoin=True))
    flatnetwork = relationship('Network', backref=backref('flatnetwork', innerjoin=True))
    flatdomain = relationship('Domain', backref=backref('flatdomain', innerjoin=True), foreign_keys=domainid)
    flatparent = relationship('Domain', backref=backref('flatparent'), foreign_keys=domainparent)

    def __str__(self):
        return "{0}".format(self.hostname)

