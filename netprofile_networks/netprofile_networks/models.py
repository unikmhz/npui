#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Networks module - Models
# Copyright © 2013-2017 Alex Unigovsky
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
    'Network',
    'NetworkGroup',
    'NetworkService',
    'NetworkServiceType',
    'RoutingTable',
    'RoutingTableEntry'
]

import ipaddress
import itertools
import math
from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Sequence,
    Unicode,
    UnicodeText,
    text
)
from sqlalchemy.orm import (
    backref,
    relationship
)
from pyramid.i18n import TranslationStringFactory

from netprofile.db.connection import Base
from netprofile.db.fields import (
    NPBoolean,
    UInt8,
    UInt16,
    UInt32,
    npbool,
    IPv4Address,
    IPv6Address,
    IPv6Offset
)
from netprofile.db.ddl import (
    Comment,
    Trigger
)
from netprofile.tpl import TemplateObject
from netprofile.ext.columns import MarkupColumn
from netprofile.ext.wizards import SimpleWizard

_ = TranslationStringFactory('netprofile_networks')


class Network(Base):
    """
    Network object.
    """
    __tablename__ = 'nets_def'
    __table_args__ = (
        Comment('Networks'),
        Index('nets_def_u_name', 'name', unique=True),
        Index('nets_def_u_ipaddr', 'ipaddr', unique=True),
        Index('nets_def_u_ip6addr', 'ip6addr', unique=True),
        Index('nets_def_i_domainid', 'domainid'),
        Index('nets_def_i_netgid', 'netgid'),
        Index('nets_def_i_rtid', 'rtid'),
        Index('nets_def_i_mgmtdid', 'mgmtdid'),
        Trigger('after', 'insert', 't_nets_def_ai'),
        Trigger('after', 'update', 't_nets_def_au'),
        Trigger('after', 'delete', 't_nets_def_ad'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_NETS',
                'cap_read':      'NETS_LIST',
                'cap_create':    'NETS_CREATE',
                'cap_edit':      'NETS_EDIT',
                'cap_delete':    'NETS_DELETE',

                'menu_name':     _('Networks'),
                'show_in_menu':  'modules',
                'menu_main':     True,
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('netid',
                                  'name', 'domain', 'group',
                                  'ipaddr', 'ip6addr',
                                  MarkupColumn(
                                      name='state',
                                      header_string=_('State'),
                                      template=TemplateObject(
                                          'netprofile_networks:templates'
                                          '/networks_icons.mak'),
                                      column_width=40,
                                      column_resizable=False)),
                'grid_hidden':   ('netid', 'domain', 'group'),
                'form_view':     ('name', 'domain', 'group',
                                  'management_device',
                                  'enabled', 'public',
                                  'ipaddr', 'cidr',
                                  'ip6addr', 'cidr6',
                                  'vlanid', 'routing_table',
                                  'gueststart', 'guestend',
                                  'gueststart6', 'guestend6',
                                  'descr'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new network'))
            }
        })
    id = Column(
        'netid',
        UInt32(),
        Sequence('nets_def_netid_seq'),
        Comment('Network ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Network name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 4
        })
    domain_id = Column(
        'domainid',
        UInt32(),
        ForeignKey('domains_def.domainid', name='nets_def_fk_domainid',
                   onupdate='CASCADE'),
        Comment('Domain ID'),
        nullable=False,
        info={
            'header_string': _('Domain'),
            'filter_type': 'nplist',
            'column_flex': 3
        })
    group_id = Column(
        'netgid',
        UInt32(),
        ForeignKey('nets_groups.netgid', name='nets_def_fk_netgid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Network group ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Group'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    management_device_id = Column(
        'mgmtdid',
        UInt32(),
        ForeignKey('devices_network.did', name='nets_def_fk_mgmtdid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Management device ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Management Device'),
            'filter_type': 'none'
        })
    enabled = Column(
        NPBoolean(),
        Comment('Is network enabled?'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string': _('Enabled')
        })
    public = Column(
        NPBoolean(),
        Comment('Is network visible to outsiders?'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string': _('Public')
        })
    ipv4_address = Column(
        'ipaddr',
        IPv4Address(),
        Comment('Network IPv4 address'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('IPv4 Address'),
            'column_flex': 1
        })
    ipv6_address = Column(
        'ip6addr',
        IPv6Address(),
        Comment('Network IPv6 address'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('IPv6 Address'),
            'column_flex': 1
        })
    ipv4_cidr = Column(
        'cidr',
        UInt8(),
        Comment('Network CIDR number'),
        nullable=False,
        default=24,
        server_default=text('24'),
        info={
            'header_string': _('IPv4 Netmask')
        })
    ipv6_cidr = Column(
        'cidr6',
        UInt8(),
        Comment('Network CIDRv6 number'),
        nullable=False,
        default=64,
        server_default=text('64'),
        info={
            'header_string': _('IPv6 Netmask')
        })
    vlan_id = Column(
        'vlanid',
        UInt16(),
        Comment('Network VLAN ID'),
        nullable=False,
        default=0,
        server_default=text('0'),
        info={
            'header_string': _('VLAN')
        })
    routing_table_id = Column(
        'rtid',
        UInt32(),
        ForeignKey('rt_def.rtid', name='nets_def_fk_rtid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Routing table ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Routing Table'),
            'filter_type': 'nplist'
        })
    ipv4_guest_start = Column(
        'gueststart',
        UInt16(),
        Comment('Start of IPv4 guest allocation area'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Start of IPv4 Guest Allocation Area')
        })
    ipv4_guest_end = Column(
        'guestend',
        UInt16(),
        Comment('End of IPv4 guest allocation area'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('End of IPv4 Guest Allocation Area')
        })
    ipv6_guest_start = Column(
        'gueststart6',
        IPv6Offset(),
        Comment('Start of IPv6 guest allocation area'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Start of IPv6 Guest Allocation Area')
        })
    ipv6_guest_end = Column(
        'guestend6',
        IPv6Offset(),
        Comment('End of IPv6 guest allocation area'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('End of IPv6 Guest Allocation Area')
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Network description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    domain = relationship(
        'Domain',
        innerjoin=True,
        backref='networks')
    group = relationship(
        'NetworkGroup',
        backref=backref('networks',
                        passive_deletes=True))
    management_device = relationship(
        'NetworkDevice',
        backref=backref('networks',
                        passive_deletes=True))
    routing_table = relationship(
        'RoutingTable',
        backref=backref('networks',
                        passive_deletes=True))
    services = relationship(
        'NetworkService',
        backref=backref('network', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    @property
    def ipv4_network(self):
        if self.ipv4_address:
            return ipaddress.IPv4Network('%s/%s' % (str(self.ipv4_address),
                                                    str(self.ipv4_cidr)))

    @property
    def ipv6_network(self):
        if self.ipv6_address:
            return ipaddress.IPv6Network('%s/%s' % (str(self.ipv6_address),
                                                    str(self.ipv6_cidr)))

    def __str__(self):
        return str(self.name)


class NetworkGroup(Base):
    """
    Network group object.
    """
    __tablename__ = 'nets_groups'
    __table_args__ = (
        Comment('Network groups'),
        Index('nets_groups_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_NETS',
                'cap_read':      'NETS_LIST',
                'cap_create':    'NETGROUPS_CREATE',
                'cap_edit':      'NETGROUPS_EDIT',
                'cap_delete':    'NETGROUPS_DELETE',

                'menu_name':     _('Groups'),
                'show_in_menu':  'modules',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('netgid', 'name', 'descr'),
                'grid_hidden':   ('netgid',),
                'form_view':     ('name', 'descr'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new network group'))
            }
        })
    id = Column(
        'netgid',
        UInt32(),
        Sequence('nets_groups_netgid_seq'),
        Comment('Network group ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Network group name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Network group description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    def __str__(self):
        return str(self.name)


class NetworkServiceType(Base):
    """
    Network service type object.
    """
    __tablename__ = 'nets_hltypes'
    __table_args__ = (
        Comment('Networks-hosts linkage types'),
        Index('nets_hltypes_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_NETS',
                'cap_read':      'NETS_LIST',
                'cap_create':    'NETS_SERVICETYPES_CREATE',
                'cap_edit':      'NETS_SERVICETYPES_EDIT',
                'cap_delete':    'NETS_SERVICETYPES_DELETE',

                'menu_name':     _('Services'),
                'show_in_menu':  'admin',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('hltypeid', 'name', 'unique'),
                'grid_hidden':   ('hltypeid',),
                'form_view':     ('name', 'unique'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(
                                    title=_('Add new network service type'))
            }
        })
    id = Column(
        'hltypeid',
        UInt32(),
        Sequence('nets_hltypes_hltypeid_seq', start=101, increment=1),
        Comment('Networks-hosts linkage type ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Networks-hosts linkage type name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })
    unique = Column(
        NPBoolean(),
        Comment('Is unique per network?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Unique')
        })

    services = relationship(
        'NetworkService',
        backref=backref('type', innerjoin=True))

    def __str__(self):
        req = getattr(self, '__req__', None)
        if req:
            return req.localizer.translate(_(self.name))
        return str(self.name)


class NetworkService(Base):
    """
    Network service object.
    """
    __tablename__ = 'nets_hosts'
    __table_args__ = (
        Comment('Networks-hosts linkage'),
        Index('nets_hosts_u_nhl', 'netid', 'hostid', 'hltypeid', unique=True),
        Index('nets_hosts_i_hostid', 'hostid'),
        Index('nets_hosts_i_hltypeid', 'hltypeid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_NETS',
                'cap_read':      'NETS_LIST',
                'cap_create':    'NETS_EDIT',
                'cap_edit':      'NETS_EDIT',
                'cap_delete':    'NETS_EDIT',

                'menu_name':     _('Services'),
                'grid_view':     ('nhid', 'network', 'host', 'type'),
                'grid_hidden':   ('nhid',),
                'form_view':     ('network', 'host', 'type'),
                'create_wizard': SimpleWizard(
                                    title=_('Add new network service'))
            }
        })
    id = Column(
        'nhid',
        UInt32(),
        Sequence('nets_hosts_nhid_seq'),
        Comment('Network-host linkage ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    network_id = Column(
        'netid',
        UInt32(),
        ForeignKey('nets_def.netid', name='nets_hosts_fk_netid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Network ID'),
        nullable=False,
        info={
            'header_string': _('Network'),
            'filter_type': 'none',
            'column_flex': 1
        })
    host_id = Column(
        'hostid',
        UInt32(),
        ForeignKey('hosts_def.hostid', name='nets_hosts_fk_hostid',
                   onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Host ID'),
        nullable=False,
        info={
            'header_string': _('Host'),
            'filter_type': 'none',
            'column_flex': 1
        })
    type_id = Column(
        'hltypeid',
        UInt32(),
        ForeignKey('nets_hltypes.hltypeid', name='nets_hosts_fk_hltypeid',
                   onupdate='CASCADE'),
        Comment('Network-host linkage type'),
        nullable=False,
        info={
            'header_string': _('Type'),
            'filter_type': 'nplist',
            'column_flex': 1
        })

    host = relationship(
        'Host',
        innerjoin=True,
        backref=backref('network_services',
                        cascade='all, delete-orphan',
                        passive_deletes=True))


class RoutingTable(Base):
    """
    Routing table object.
    """
    __tablename__ = 'rt_def'
    __table_args__ = (
        Comment('Routing tables'),
        Index('rt_def_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_NETS',
                'cap_read':      'NETS_LIST',
                'cap_create':    'NETS_EDIT',
                'cap_edit':      'NETS_EDIT',
                'cap_delete':    'NETS_EDIT',

                'menu_name':     _('Routing Tables'),
                'show_in_menu':  'admin',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('rtid', 'name'),
                'grid_hidden':   ('rtid',),
                'form_view':     ('name',),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new routing table'))
            }
        })
    id = Column(
        'rtid',
        UInt32(),
        Sequence('rt_def_rtid_seq'),
        Comment('Routing table ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Routing table name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })

    entries = relationship(
        'RoutingTableEntry',
        backref=backref('table', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    def __str__(self):
        return str(self.name)


class RoutingTableEntry(Base):
    """
    IPv4 routing table entry object.
    """
    __tablename__ = 'rt_bits'
    __table_args__ = (
        Comment('IPv4 routing table entries'),
        Index('rt_bits_i_rtid', 'rtid'),
        Index('rt_bits_i_rtr', 'rtr'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_NETS',
                'cap_read':      'NETS_LIST',
                'cap_create':    'NETS_EDIT',
                'cap_edit':      'NETS_EDIT',
                'cap_delete':    'NETS_EDIT',

                'menu_name':     _('Routing Table Entries'),
                'grid_view':     ('rtbid', 'table', 'net', 'cidr', 'next_hop'),
                'grid_hidden':   ('rtbid',),
                'form_view':     ('table', 'net', 'cidr', 'next_hop'),
                'create_wizard': SimpleWizard(title=_(
                                    'Add new IPv4 routing table entry'))
            }
        })
    id = Column(
        'rtbid',
        UInt32(),
        Sequence('rt_bits_rtbid_seq'),
        Comment('Routing table bit ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    table_id = Column(
        'rtid',
        UInt32(),
        ForeignKey('rt_def.rtid', name='rt_bits_fk_rtid',
                   onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Routing table ID'),
        nullable=False,
        info={
            'header_string': _('Table'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    network = Column(
        'net',
        IPv4Address(),
        Comment('Network address'),
        nullable=False,
        info={
            'header_string': _('Network'),
            'column_flex': 1
        })
    cidr = Column(
        UInt8(),
        Comment('Network CIDR'),
        nullable=False,
        default=24,
        server_default=text('24'),
        info={
            'header_string': _('Netmask')
        })
    next_hop_id = Column(
        'rtr',
        UInt32(),
        ForeignKey('hosts_def.hostid', name='rt_bits_fk_hostid',
                   onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Next hop host ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Next Hop'),
            'filter_type': 'none',
            'column_flex': 1
        })

    next_hop = relationship(
        'Host',
        backref=backref('next_hops',
                        cascade='all, delete-orphan',
                        passive_deletes=True))

    @property
    def ipv4_network(self):
        return ipaddress.IPv4Network('%s/%s' % (str(self.network),
                                                str(self.cidr)))

    def dhcp_strings(self, net):
        if self.next_hop:
            gws = self.next_hop.ipv4_addresses
        else:
            gws = itertools.chain.from_iterable(ns.host.ipv4_addresses
                                                for ns
                                                in net.services
                                                if ns.type_id == 4)
        ret = []
        netstr = ':'.join('{0:02x}'.format(o)
                          for o
                          in self.network.packed[:math.ceil(self.cidr / 8)])
        for gw in gws:
            ret.append('%02x%s%s:%s' % (
                self.cidr,
                ':' if self.cidr > 0 else '',
                netstr,
                '%02x:%02x:%02x:%02x' % tuple(gw.address.packed)))
        return ret
