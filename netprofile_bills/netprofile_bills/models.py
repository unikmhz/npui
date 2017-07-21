#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Bills module - Models
# Copyright © 2017 Alex Unigovsky
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
    'Bill',
    'BillType',
    'BillSerial'
]

from sqlalchemy import (
    Column,
    Date,
    FetchedValue,
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
    relationship
)
from sqlalchemy.ext.mutable import (
    MutableDict,
    MutableList
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

_ = TranslationStringFactory('netprofile_bills')


class BillSerial(Base):
    """
    Bill serial number counter object.
    """
    __tablename__ = 'bills_serials'
    __table_args__ = (
        Comment('Bill serial counters'),
        Index('bills_serials_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_BILLS',
                'cap_read':      'BILLS_LIST',
                'cap_create':    'BILLS_TYPES_EDIT',
                'cap_edit':      'BILLS_TYPES_EDIT',
                'cap_delete':    'BILLS_TYPES_EDIT',

                'menu_name':     _('Serial Numbers'),
                'show_in_menu':  'admin',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('bsid', 'name', 'value'),
                'grid_hidden':   ('bsid',),
                'form_view':     ('name', 'value'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(
                                     title=_('Add new serial counter'))
            }
        })
    id = Column(
        'bsid',
        UInt32(),
        Sequence('bills_serials_bsid_seq'),
        Comment('Bill serial counter ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Bill serial counter name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 2
        })
    value = Column(
        UInt32(),
        Comment('Bill serial counter value'),
        nullable=False,
        info={
            'header_string': _('Value'),
            'column_flex': 1
        })

    def __str__(self):
        return str(self.name)


class BillPart(MutableDict):
    pass


class BillPartList(MutableList):
    def __getitem__(self, idx):
        val = super(BillPartList, self).__getitem__(idx)
        if isinstance(val, dict):
            if not isinstance(val, BillPart):
                val = BillPart.coerce(idx, val)
                val._parents = self._parents
                list.__setitem__(self, idx, val)
        return val

    def __setitem__(self, idx, val):
        if isinstance(val, dict):
            if not isinstance(val, BillPart):
                val = BillPart.coerce(idx, val)
                val._parents = self._parents
        list.__setitem__(self, idx, val)
        self.changed()


class BillType(Base):
    """
    Bill type object.
    """
    __tablename__ = 'bills_types'
    __table_args__ = (
        Comment('Bill types'),
        Index('bills_types_u_name', 'name', unique=True),
        Index('bills_types_i_bsid', 'bsid'),
        Index('bills_types_i_cap', 'cap'),
        Index('bills_types_i_issuer', 'issuer'),
        Index('bills_types_i_siotypeid', 'siotypeid'),
        Index('bills_types_i_docid', 'docid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_BILLS',
                'cap_read':      'BILLS_LIST',
                'cap_create':    'BILLS_TYPES_CREATE',
                'cap_edit':      'BILLS_TYPES_EDIT',
                'cap_delete':    'BILLS_TYPES_DELETE',

                'show_in_menu':  'admin',
                'menu_name':     _('Bill Types'),
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('btypeid', 'serial', 'name',
                                  'prefix', 'issuer', 'document'),
                'grid_hidden':   ('btypeid', 'issuer', 'document'),
                'form_view':     ('name', 'serial', 'prefix',
                                  'document', 'issuer', 'privilege', 'io_type',
                                  'mutable', 'template', 'descr'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),

                'create_wizard': SimpleWizard(title=_('Add new bill type'))
            }
        })
    id = Column(
        'btypeid',
        UInt32(),
        Sequence('bills_types_btypeid_seq'),
        Comment('Bill type ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    serial_id = Column(
        'bsid',
        UInt32(),
        ForeignKey('bills_serials.bsid', name='bills_types_fk_bsid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Bill serial counter ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Serial Counter'),
            'editor_xtype': 'simplemodelselect',
            'filter_type': 'nplist',
            'column_flex': 2
        })
    name = Column(
        Unicode(255),
        Comment('Bill type name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 3
        })
    prefix = Column(
        Unicode(48),
        Comment('Bill number prefix'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Prefix'),
            'column_flex': 1
        })
    privilege_code = Column(
        'cap',
        ASCIIString(48),
        ForeignKey('privileges.code', name='bills_types_fk_cap',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Capability to create bills of this type'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Privilege'),
            'column_flex': 1
        })
    issuer = Column(
        UInt32(),
        ForeignKey('entities_def.entityid', name='bills_types_fk_issuer',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Issuer entity ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Issuer'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    io_type_id = Column(
        'siotypeid',
        UInt32(),
        ForeignKey('stashes_io_types.siotypeid',
                   name='bills_types_fk_siotypeid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Stash I/O type generated when paid'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Type'),
            'filter_type': 'nplist',
            'editor_xtype': 'simplemodelselect',
            'column_flex': 2
        })
    document_id = Column(
        'docid',
        UInt32(),
        ForeignKey('docs_def.docid', name='bills_types_fk_docid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Bill document ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Document'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    template = Column(
        BillPartList.as_mutable(JSONData),
        Comment('Bill parts template'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Parts'),
            'editor_xtype': 'gridfield',
            'editor_config': {
                'gridCfg': {
                    'store': {
                        'xtype': 'array',
                        'autoLoad': False,
                        'fields': [{
                            'name': 'name',
                            'type': 'string'
                        }, {
                            'name': 'sum',
                            'type': 'float',
                            'defaultValue': 0.0
                        }, {
                            'name': 'quantity',
                            'type': 'int',
                            'defaultValue': 1
                        }, {
                            'name': 'taxmult',
                            'type': 'float',
                            'defaultValue': 1.0
                        }, {
                            'name': 'counts',
                            'type': 'boolean',
                            'defaultValue': True
                        }]
                    },
                    'columns': [{
                        'text': _('Name'),
                        'dataIndex': 'name',
                        'flex': 3,
                        'editor': {'xtype': 'textfield'}
                    }, {
                        'text': _('Sum'),
                        'dataIndex': 'sum',
                        'xtype': 'numbercolumn',
                        'align': 'right',
                        'format': '0.00',
                        'flex': 2
                    }, {
                        'text': _('Quantity'),
                        'dataIndex': 'quantity',
                        'xtype': 'numbercolumn',
                        'align': 'right',
                        'format': '0',
                        'flex': 2
                    }, {
                        'text': _('Tax Multiplier'),
                        'dataIndex': 'taxmult',
                        'xtype': 'numbercolumn',
                        'align': 'right',
                        'format': '0.00',
                        'flex': 2
                    }, {
                        'text': _('Counts'),
                        'dataIndex': 'counts',
                        'xtype': 'checkcolumn',
                        'flex': 2
                    }]
                }
            }
        })
    mutable = Column(
        NPBoolean(),
        Comment('Is template mutable?'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string': _('Mutable')
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Bill type description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    serial = relationship(
        'BillSerial',
        backref=backref('bill_types',
                        passive_deletes=True))
    privilege = relationship(
        'Privilege',
        backref=backref('bill_types',
                        passive_deletes=True))
    io_type = relationship(
        'StashIOType',
        backref=backref('bill_types',
                        passive_deletes=True))
    document = relationship(
        'Document',
        backref=backref('bill_types',
                        passive_deletes=True))
    bills = relationship(
        'Bill',
        backref=backref('type', innerjoin=True, lazy='joined'),
        passive_deletes='all')

    def __str__(self):
        return str(self.name)


class BillState(DeclEnum):
    """
    Bill state enumeration.
    """
    created = 'C', _('Created'), 10
    sent = 'S', _('Sent'), 20
    paid = 'P', _('Paid'), 30
    recalled = 'R', _('Recalled'), 40


class Bill(Base):
    """
    Bill object.
    """
    __tablename__ = 'bills_def'
    __table_args__ = (
        Comment('Bills'),
        Index('bills_def_i_btypeid', 'btypeid'),
        Index('bills_def_i_entityid', 'entityid'),
        Index('bills_def_i_stashid', 'stashid'),
        Index('bills_def_i_currid', 'currid'),
        Index('bills_def_i_cby', 'cby'),
        Index('bills_def_i_mby', 'mby'),
        Index('bills_def_i_pby', 'pby'),
        Trigger('before', 'insert', 't_bills_def_bi'),
        Trigger('before', 'update', 't_bills_def_bu'),
        Trigger('after', 'insert', 't_bills_def_ai'),
        Trigger('after', 'update', 't_bills_def_au'),
        Trigger('after', 'delete', 't_bills_def_ad'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_BILLS',
                'cap_read':      'BILLS_LIST',
                'cap_create':    'BILLS_CREATE',
                'cap_edit':      'BILLS_EDIT',
                'cap_delete':    'BILLS_DELETE',

                'show_in_menu':  'modules',
                'menu_name':     _('Bills'),
                'menu_main':     True,
                'default_sort':  ({'property': 'ctime', 'direction': 'DESC'},),
                'grid_view':     ('billid', 'type', 'entity', 'stash', 'title',
                                  'adate', 'ctime', 'mtime', 'state', 'ptime',
                                  'sum', 'currency'),
                'grid_hidden':   ('billid', 'type', 'stash',
                                  'adate', 'ctime', 'mtime', 'ptime',
                                  'currency'),
                'form_view':     ('type', 'title', 'serial',
                                  'entity', 'stash', 'state',
                                  'currency', 'sum', 'adate',),
                'easy_search':   ('title',),
                'extra_data':    ('formatted_total_sum',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),

                'create_wizard': SimpleWizard(title=_('Add new bill'))
            }
        })
    id = Column(
        'billid',
        UInt32(),
        Sequence('bills_def_billid_seq'),
        Comment('Bill ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    type_id = Column(
        'btypeid',
        UInt32(),
        ForeignKey('bills_types.btypeid', name='bills_def_fk_btypeid',
                   onupdate='CASCADE'),  # ondelete=RESTRICT
        Comment('Bill type ID'),
        nullable=False,
        info={
            'header_string': _('Type'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    serial_number = Column(
        'serial',
        UInt32(),
        Comment('Bill serial number'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Serial #')
        })
    entity_id = Column(
        'entityid',
        UInt32(),
        ForeignKey('entities_def.entityid', name='bills_def_fk_entityid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Entity ID'),
        nullable=False,
        info={
            'header_string': _('Entity'),
            'column_flex': 2
        })
    stash_id = Column(
        'stashid',
        UInt32(),
        ForeignKey('stashes_def.stashid', name='bills_def_fk_stashid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Stash ID'),
        nullable=False,
        info={
            'header_string': _('Stash'),
            'column_flex': 2
        })
    currency_id = Column(
        'currid',
        UInt32(),
        ForeignKey('currencies_def.currid', name='bills_def_fk_currid',
                   onupdate='CASCADE'),  # ondelete=RESTRICT
        Comment('Currency ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Currency'),
            'editor_xtype': 'simplemodelselect',
            'editor_config': {
                'extraParams': {'__ffilter': [{
                    'property': 'oper_visible',
                    'operator': 'eq',
                    'value': True
                }]}
            },
            'filter_type': 'nplist',
            'column_flex': 1
        })
    total_sum = Column(
        'sum',
        Money(),
        Comment('Total amount to be paid'),
        nullable=False,
        info={
            'header_string': _('Sum'),
            'column_xtype': 'templatecolumn',
            'template': '{formatted_total_sum}'
        })
    state = Column(
        BillState.db_type(),
        Comment('Created / Sent / Paid / Recalled'),
        nullable=False,
        default=BillState.created,
        server_default=BillState.created,
        info={
            'header_string': _('State')
        })
    title = Column(
        Unicode(255),
        Comment('Bill title'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Title'),
            'column_flex': 3
        })
    accounting_date = Column(
        'adate',
        Date(),
        Comment('Accounting date'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Accounting Date')
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
    payment_time = Column(
        'ptime',
        TIMESTAMP(),
        Comment('Payment timestamp'),
        nullable=True,
        default=None,
        server_default=FetchedValue(),
        info={
            'header_string': _('Marked as Paid'),
            'read_only': True
        })
    created_by_id = Column(
        'cby',
        UInt32(),
        ForeignKey('users.uid', name='bills_def_fk_cby',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Created by'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Created'),
            'filter_type': 'nplist',
            'read_only': True
        })
    modified_by_id = Column(
        'mby',
        UInt32(),
        ForeignKey('users.uid', name='bills_def_fk_mby',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Modified by'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Modified'),
            'filter_type': 'nplist',
            'read_only': True
        })
    paid_by_id = Column(
        'pby',
        UInt32(),
        ForeignKey('users.uid', name='bills_def_fk_pby',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Marked as paid by'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Marked as Paid'),
            'filter_type': 'nplist',
            'read_only': True
        })
    parts = Column(
        BillPartList.as_mutable(JSONData),
        Comment('Bill parts'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Contents')
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Bill description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    entity = relationship(
        'Entity',
        innerjoin=True,
        backref=backref('bills',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    stash = relationship(
        'Stash',
        innerjoin=True,
        backref=backref('bills',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    currency = relationship(
        'Currency',
        lazy='joined',
        backref=backref('bills',
                        passive_deletes='all'))
    created_by = relationship(
        'User',
        foreign_keys=created_by_id,
        backref=backref('created_bills',
                        passive_deletes=True))
    modified_by = relationship(
        'User',
        foreign_keys=modified_by_id,
        backref=backref('modified_bills',
                        passive_deletes=True))
    paid_by = relationship(
        'User',
        foreign_keys=paid_by_id,
        backref=backref('paid_bills',
                        passive_deletes=True))

    def __str__(self):
        return str(self.title)

    def formatted_total_sum(self, req):
        return money_format(req, self.total_sum, currency=self.currency)
