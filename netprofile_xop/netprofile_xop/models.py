#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: XOP module - Models
# Copyright © 2014-2017 Alex Unigovsky
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
    'ExternalOperation',
    'ExternalOperationProvider'
]

import ipaddress
import pkg_resources
from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Sequence,
    TIMESTAMP,
    Unicode,
    UnicodeText,
    text
)
from sqlalchemy.orm import (
    backref,
    relationship,
    validates
)
from pyramid.i18n import TranslationStringFactory

from netprofile.common.locale import money_format
from netprofile.db.connection import Base
from netprofile.db.fields import (
    ASCIIString,
    DeclEnum,
    JSONData,
    Money,
    NPBoolean,
    UInt32,
    npbool
)
from netprofile.db.ddl import (
    Comment,
    CurrentTimestampDefault,
    Trigger
)
from netprofile.ext.wizards import SimpleWizard

_ = TranslationStringFactory('netprofile_xop')


class ExternalOperationState(DeclEnum):
    """
    Enumeration of xop state codes
    """
    new = 'NEW', _('New'), 10
    checked = 'CHK', _('Checked'), 20
    pending = 'PND', _('Pending'), 30
    confirmed = 'CNF', _('Confirmed'), 40
    cleared = 'CLR', _('Cleared'), 50
    canceled = 'CNC', _('Canceled'), 60


class ExternalOperationProviderAuthMethod(DeclEnum):
    """
    Enumeration of xop provider auth methods
    """
    http = 'http', _('HTTP Basic'), 10
    md5 = 'req-md5', _('Request MD5'), 20
    sha1 = 'req-sha1', _('Request SHA1'), 30


class ExternalOperation(Base):
    """
    External operation object.
    """

    __tablename__ = 'xop_def'
    __table_args__ = (
        Comment('External operations'),
        Index('xop_def_i_extid', 'extid'),
        Index('xop_def_i_xoppid', 'xoppid'),
        Index('xop_def_i_ts', 'ts'),
        Index('xop_def_i_entityid', 'entityid'),
        Index('xop_def_i_stashid', 'stashid'),
        Index('xop_def_u_sioid', 'sioid', unique=True),
        Trigger('before', 'insert', 't_xop_def_bi'),
        Trigger('before', 'update', 't_xop_def_bu'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_XOP',
                'cap_read':      'STASHES_IO',
                'cap_create':    'STASHES_IOTYPES_CREATE',
                'cap_edit':      '__NOPRIV__',
                'cap_delete':    '__NOPRIV__',

                'menu_name':     _('External Operations'),
                'menu_main':     True,
                'show_in_menu':  'modules',
                'default_sort':  ({'property': 'ts', 'direction': 'DESC'},),
                'grid_view':     ('xopid', 'provider', 'ts', 'entity',
                                  'currency', 'diff', 'state'),
                'grid_hidden':   ('xopid', 'currency'),
                'form_view':     ('provider', 'ts', 'entity',
                                  'currency', 'diff', 'state',
                                  'stash', 'stash_io',
                                  'extid', 'eacct'),
                'easy_search':   ('extid', 'eacct'),
                'extra_data':    ('formatted_difference',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple')
            }
        })
    id = Column(
        'xopid',
        UInt32(),
        Sequence('xop_def_xopid_seq'),
        Comment('External operation ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    external_id = Column(
        'extid',
        ASCIIString(255),
        Comment('Remote provider operation ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('External ID')
        })
    external_account = Column(
        'eacct',
        Unicode(255),
        Comment('External account name'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('External Account')
        })
    provider_id = Column(
        'xoppid',
        UInt32(),
        ForeignKey('xop_providers.xoppid', name='xop_def_fk_xoppid',
                   onupdate='CASCADE'),
        Comment('External operation provider ID'),
        nullable=False,
        info={
            'header_string': _('Provider'),
            'column_flex': 3
        })
    currency_id = Column(
        'currid',
        UInt32(),
        Comment('Currency ID'),
        ForeignKey('currencies_def.currid', name='xop_def_fk_currid',
                   onupdate='CASCADE'),  # ondelete=RESTRICT
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Currency'),
            'filter_type': 'nplist'
        })
    timestamp = Column(
        'ts',
        TIMESTAMP(),
        Comment('Timestamp of operation'),
        CurrentTimestampDefault(on_update=True),
        nullable=False,
        info={
            'header_string': _('Date')
        })
    entity_id = Column(
        'entityid',
        UInt32(),
        ForeignKey('entities_def.entityid', name='xop_def_fk_entityid',
                   onupdate='CASCADE', ondelete='SET NULL'),
        Comment('Entity ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Entity'),
            'filter_type': 'none',
            'column_flex': 3
        })
    stash_id = Column(
        'stashid',
        UInt32(),
        ForeignKey('stashes_def.stashid', name='xop_def_fk_stashid',
                   onupdate='CASCADE', ondelete='SET NULL'),
        Comment('Affected stash ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Stash'),
            'filter_type': 'none',
            'column_flex': 3
        })
    stash_io_id = Column(
        'sioid',
        UInt32(),
        ForeignKey('stashes_io_def.sioid', name='xop_def_fk_sioid',
                   onupdate='CASCADE', ondelete='SET NULL'),
        Comment('Related stash operation ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Operation'),
            'filter_type': 'none'
        })
    difference = Column(
        'diff',
        Money(),
        Comment('Stash amount changes'),
        nullable=False,
        default=0,
        server_default=text('0.0'),
        info={
            'header_string': _('Amount'),
            'column_xtype': 'templatecolumn',
            'template': '{formatted_difference}'
        })
    state = Column(
        ExternalOperationState.db_type(),
        Comment('Operation state'),
        nullable=False,
        default=ExternalOperationState.new,
        server_default=ExternalOperationState.new,
        info={
            'header_string': _('State')
        })
    data = Column(
        JSONData(),
        Comment('Extra data for use by extensions'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Extra Data'),
            'read_cap': 'ADMIN_DEV'
        })

    provider = relationship(
        'ExternalOperationProvider',
        innerjoin=True,
        backref=backref('external_operations',
                        passive_deletes='all'))
    currency = relationship(
        'Currency',
        lazy='joined',
        backref=backref('external_operations',
                        passive_deletes='all'))
    entity = relationship(
        'Entity',
        backref=backref('external_operations',
                        passive_deletes=True))
    stash = relationship(
        'Stash',
        backref=backref('external_operations',
                        passive_deletes=True))
    stash_io = relationship(
        'StashIO',
        backref=backref('external_operations',
                        passive_deletes=True))

    @validates('state')
    def _valid_state(self, key, val):
        if val not in ExternalOperationState:
            raise ValueError('Invalid XOP state')
        if self.state is None or self.state == val:
            return val
        if self.state in (ExternalOperationState.new,
                          ExternalOperationState.pending):
            if val in (ExternalOperationState.checked,
                       ExternalOperationState.confirmed,
                       ExternalOperationState.canceled):
                return val
            raise ValueError('Invalid XOP state transition')
        if self.state == ExternalOperationState.checked:
            if val in (ExternalOperationState.pending,
                       ExternalOperationState.canceled):
                return val
            raise ValueError('Invalid XOP state transition')
        if self.state == ExternalOperationState.confirmed:
            if val in (ExternalOperationState.cleared,
                       ExternalOperationState.canceled):
                return val
            raise ValueError('Invalid XOP state transition')
        raise ValueError('Invalid XOP state')

    def __str__(self):
        return '%s %s' % (self.provider,
                          self.external_id)

    def formatted_difference(self, req):
        return money_format(req, self.difference, currency=self.currency)


class ExternalOperationProvider(Base):
    """
    External Operation Providers object
    """
    __tablename__ = 'xop_providers'
    __table_args__ = (
        Comment('External operation providers'),
        Index('xop_providers_u_name', 'name', unique=True),
        Index('xop_providers_u_uri', 'uri', unique=True),
        Index('xop_providers_u_sname', 'sname', unique=True),
        Index('xop_providers_i_siotypeid', 'siotypeid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_XOP',
                'cap_read':      'STASHES_IO',
                'cap_create':    'STASHES_IOTYPES_CREATE',
                'cap_edit':      'STASHES_IOTYPES_EDIT',
                'cap_delete':    'STASHES_IOTYPES_DELETE',

                'menu_name':     _('Providers'),
                'show_in_menu':  'admin',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('xoppid', 'name', 'sname', 'gwclass',
                                  'enabled'),
                'grid_hidden':   ('xoppid',),
                'form_view':     ('uri', 'name', 'sname', 'gwclass',
                                  'enabled', 'accesslist', 'io_type',
                                  'mindiff', 'maxdiff',
                                  'authmethod', 'authopts',
                                  'authuser', 'authpass', 'descr'),
                'create_wizard': SimpleWizard(title=_('Add new provider')),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple')
            }
        })
    id = Column(
        'xoppid',
        UInt32(),
        Sequence('xop_providers_xoppid_seq'),
        Comment('External operation provider ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    uri = Column(
        ASCIIString(64),
        Comment('URI used in XOP interface'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('URI'),
            'column_flex': 1
        })
    name = Column(
        Unicode(255),
        Comment('External operation provider name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 2
        })
    short_name = Column(
        'sname',
        Unicode(32),
        Comment('External operation provider short name'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Short Name'),
            'column_flex': 1
        })
    enabled = Column(
        NPBoolean(),
        Comment('Is provider enabled?'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Enabled')
        })
    access_list = Column(
        'accesslist',
        ASCIIString(255),
        Comment('Allowed access rules'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Access List')
        })
    gateway_class = Column(
        'gwclass',
        ASCIIString(64),
        Comment('Provider gateway class name'),
        nullable=False,
        info={
            'header_string': _('Gateway')
        })
    io_type_id = Column(
        'siotypeid',
        UInt32(),
        Comment('Stash I/O type generated in transaction'),
        ForeignKey('stashes_io_types.siotypeid',
                   name='xop_providers_fk_soitypeid',
                   onupdate='CASCADE'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Operation Type'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    min_difference = Column(
        'mindiff',
        Money(),
        Comment('Minimum operation result'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Minimum Amount')
        })
    max_difference = Column(
        'maxdiff',
        Money(),
        Comment('Maxmum operation result'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Maximum Amount')
        })
    authentication_method = Column(
        'authmethod',
        ExternalOperationProviderAuthMethod.db_type(),
        Comment('Authentication method'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Auth Type')
        })
    authentication_options = Column(
        'authopts',
        JSONData(),
        Comment('Authentication options'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Auth Options')
        })
    authentication_username = Column(
        'authuser',
        Unicode(255),
        Comment('Authentication user'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Auth User')
        })
    authentication_password = Column(
        'authpass',
        Unicode(255),
        Comment('Authentication password'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Auth Password')
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('External operation provider description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    io_type = relationship(
        'StashIOType',
        backref='external_operation_providers')

    @property
    def access_nets(self):
        if not self.access_list:
            return ()
        nets = []
        for ace in self.access_list.split(';'):
            try:
                nets.append(ipaddress.ip_network(ace.strip()))
            except ValueError:
                pass
        return nets

    def __str__(self):
        return '%s' % self.name

    def can_access(self, req):
        if not req.remote_addr:
            return False
        try:
            addr = ipaddress.ip_address(req.remote_addr)
        except ValueError:
            return False
        nets = self.access_nets
        if len(nets) == 0:
            return True
        for net in nets:
            if addr in net:
                return True
        return False

    def get_gateway(self):
        if not self.gateway_class:
            return None
        itp = list(pkg_resources.iter_entry_points('netprofile.xop.gateways',
                                                   self.gateway_class))
        if len(itp) == 0:
            return None
        cls = itp[0].load()
        return cls(self)

    def check_operation(self, xop):
        is_ok = True
        if (self.min_difference is not None
                and xop.difference < self.min_difference):
            is_ok = False
        if (self.max_difference is not None
                and xop.difference > self.max_difference):
            is_ok = False
        if not is_ok:
            xop.state = ExternalOperationState.canceled
