#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Tickets module - Models
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
    'Ticket',
    'TicketChange',
    'TicketChangeBit',
    'TicketChangeField',
    'TicketChangeFlagMod',
    'TicketDependency',
    'TicketFile',
    'TicketFlag',
    'TicketFlagType',
    'TicketOrigin',
    'TicketState',
    'TicketStateTransition',
    'TicketTemplate',
    'TicketScheduler',
    'TicketSchedulerUserAssignment',
    'TicketSchedulerGroupAssignment',
    'TicketSubscriptionType',
    'TicketSubscription',
    'UserTicketSubscription',
    'GroupTicketSubscription',
    'EntityTicketSubscription',
    'AddressTicketSubscription',
    'TicketStateSubscription',
    'UserTicketStateSubscription',
    'GroupTicketStateSubscription',
    'EntityTicketStateSubscription',
    'AddressTicketStateSubscription'
]

import importlib
import datetime as dt
from dateutil.parser import parse as dparse
from sqlalchemy import (
    Column,
    FetchedValue,
    ForeignKey,
    Index,
    Sequence,
    TIMESTAMP,
    Unicode,
    UnicodeText,
    event,
    text,
    or_
)
from sqlalchemy.orm import (
    backref,
    lazyload,
    relationship,
    validates
)
from sqlalchemy.ext.associationproxy import association_proxy
from pyramid.i18n import TranslationStringFactory

from netprofile.db.connection import (
    Base,
    DBSession
)
from netprofile.db.fields import (
    ASCIIString,
    DeclEnum,
    NPBoolean,
    UInt8,
    UInt32,
    npbool
)
from netprofile.db.ddl import (
    Comment,
    CurrentTimestampDefault,
    Trigger
)
from netprofile.db.clauses import IntervalSeconds
from netprofile.db.util import populate_related_list
from netprofile.ext.data import ExtModel
from netprofile.ext.wizards import (
    CompositeWizardField,
    SimpleWizard,
    Step,
    Wizard,
    ExtJSWizardField
)
from netprofile.ext.columns import MarkupColumn
from netprofile_core.models import (
    Group,
    User
)
from netprofile.tpl import TemplateObject
from netprofile_entities.models import (
    Entity,
    EntityHistory,
    EntityHistoryPart,
    LegalEntity,
    PhysicalEntity
)

_ = TranslationStringFactory('netprofile_tickets')

_HIST_MAP = {
    1: 'tickets:user',
    2: 'tickets:group',
    3: 'tickets:time',
    4: 'tickets:archived',
    5: 'tickets:entity'
}


class TicketOrigin(Base):
    """
    Ticket origin type.
    """
    __tablename__ = 'tickets_origins'
    __table_args__ = (
        Comment('Origins of tickets'),
        Index('tickets_origins_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TICKETS',
                'cap_read':      'TICKETS_LIST',
                'cap_create':    'TICKETS_ORIGINS_CREATE',
                'cap_edit':      'TICKETS_ORIGINS_EDIT',
                'cap_delete':    'TICKETS_ORIGINS_DELETE',

                'show_in_menu':  'admin',
                'menu_name':     _('Ticket Origins'),
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('toid', 'name'),
                'grid_hidden':   ('toid',),
                'form_view':     ('name', 'descr'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),

                'create_wizard': SimpleWizard(title=_('Add new ticket origin'))
            }
        })
    id = Column(
        'toid',
        UInt32(),
        Sequence('tickets_origins_toid_seq', start=101, increment=1),
        Comment('Ticket origin ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Ticket origin name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Ticket origin description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    def __str__(self):
        req = getattr(self, '__req__', None)
        if req:
            return req.localizer.translate(_(self.name))
        return str(self.name)


class TicketState(Base):
    """
    Ticket state type.
    """
    __tablename__ = 'tickets_states_types'
    __table_args__ = (
        Comment('Ticket state types'),
        Index('tickets_states_types_u_tst', 'title', 'subtitle', unique=True),
        Index('tickets_states_types_i_is_start', 'is_start'),
        Index('tickets_states_types_i_is_end', 'is_end'),
        Index('tickets_states_types_i_flow', 'flow'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TICKETS',
                'cap_read':      'TICKETS_LIST',
                'cap_create':    'TICKETS_STATES_CREATE',
                'cap_edit':      'TICKETS_STATES_EDIT',
                'cap_delete':    'TICKETS_STATES_DELETE',

                'show_in_menu':  'admin',
                'menu_name':     _('Ticket States'),
                'default_sort':  ({'property': 'title',
                                   'direction': 'ASC'},
                                  {'property': 'subtitle',
                                   'direction': 'ASC'}),
                'grid_view':     ('tstid',
                                  'title', 'subtitle',
                                  'flow', 'is_start', 'is_end'),
                'grid_hidden':   ('tstid',),
                'form_view':     ('title', 'subtitle',
                                  'flow', 'is_start', 'is_end', 'allow_client',
                                  'dur', 'style', 'image', 'descr'),
                'easy_search':   ('title', 'subtitle'),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),

                'create_wizard': SimpleWizard(title=_('Add new ticket state'))
            }
        })
    id = Column(
        'tstid',
        UInt32(),
        Sequence('tickets_states_types_tstid_seq'),
        Comment('Ticket state ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    title = Column(
        Unicode(48),
        Comment('Ticket state title'),
        nullable=False,
        info={
            'header_string': _('Title'),
            'column_flex': 1
        })
    subtitle = Column(
        Unicode(48),
        Comment('Ticket state subtitle'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Subtitle'),
            'column_flex': 1
        })
    flow = Column(
        UInt8(),
        Comment('Process flow index'),
        nullable=False,
        default=1,
        server_default=text('1'),
        info={
            'header_string': _('Flow')
        })
    is_start = Column(
        NPBoolean(),
        Comment('Can be starting state'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Start')
        })
    is_end = Column(
        NPBoolean(),
        Comment('Can be ending state'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('End')
        })
    allow_client = Column(
        NPBoolean(),
        Comment('Can be created by clients'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Show to Clients')
        })
    duration = Column(
        'dur',
        UInt32(),
        Comment('Default ticket duration (in sec)'),
        nullable=True,
        default=0,
        server_default=text('NULL'),
        info={
            'header_string': _('Duration')
        })
    style = Column(
        ASCIIString(16),
        Comment('Ticket state style'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('CSS class')
        })
    image = Column(
        ASCIIString(16),
        Comment('Ticket state image'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Icon URL')
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Ticket state description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    subscriptions = relationship(
        'TicketStateSubscription',
        backref=backref('state', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    transition_to = association_proxy(
        'transitionmap_to',
        'to_state')
    transition_from = association_proxy(
        'transitionmap_from',
        'from_state')

    def __str__(self):
        j = []
        if self.title:
            j.append(self.title)
        if self.subtitle:
            j.append(self.subtitle)
        return ': '.join(j)

    @classmethod
    def get_acls(cls):
        sess = DBSession()
        res = {}
        for ts in sess.query(TicketState):
            res[ts.id] = str(ts)
        return res


class TicketStateTransition(Base):
    """
    Describes a transition between two distinct ticket states.
    """
    __tablename__ = 'tickets_states_trans'
    __table_args__ = (
        Comment('Ticket state transitions'),
        Index('tickets_states_trans_u_trans', 'tstid_from', 'tstid_to',
              unique=True),
        Index('tickets_states_trans_i_tstid_to', 'tstid_to'),
        Index('tickets_states_trans_i_reassign_gid', 'reassign_gid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TICKETS',
                'cap_read':      'TICKETS_LIST',
                'cap_create':    'TICKETS_TRANSITIONS_CREATE',
                'cap_edit':      'TICKETS_TRANSITIONS_EDIT',
                'cap_delete':    'TICKETS_TRANSITIONS_DELETE',

                'show_in_menu':  'admin',
                'menu_name':     _('Ticket Transitions'),
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('ttrid', 'name', 'from_state', 'to_state'),
                'grid_hidden':   ('ttrid',),
                'form_view':     ('name', 'from_state', 'to_state',
                                  'reassign_to', 'descr'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),

                'create_wizard': SimpleWizard(
                                    title=_('Add new ticket transition'))
            }
        })
    id = Column(
        'ttrid',
        UInt32(),
        Sequence('tickets_states_trans_ttrid_seq'),
        Comment('Ticket transition ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(48),
        Comment('Ticket transition name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })
    from_state_id = Column(
        'tstid_from',
        UInt32(),
        ForeignKey('tickets_states_types.tstid',
                   name='tickets_states_trans_fk_tstid_from',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('From state'),
        nullable=False,
        info={
            'header_string': _('From'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    to_state_id = Column(
        'tstid_to',
        UInt32(),
        ForeignKey('tickets_states_types.tstid',
                   name='tickets_states_trans_fk_tstid_to',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('To state'),
        nullable=False,
        info={
            'header_string': _('To'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    reassign_to_id = Column(
        'reassign_gid',
        UInt32(),
        ForeignKey('groups.gid',
                   name='tickets_states_trans_fk_reassign_gid',
                   onupdate='CASCADE'),  # ondelete=RESTRICT
        Comment('Reassign to group ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Reassign To'),
            'filter_type': 'nplist'
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Ticket transition description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    from_state = relationship(
        'TicketState',
        foreign_keys=from_state_id,
        innerjoin=True,
        backref='transitionmap_to')
    to_state = relationship(
        'TicketState',
        foreign_keys=to_state_id,
        innerjoin=True,
        backref='transitionmap_from')
    reassign_to = relationship('Group')

    def __str__(self):
        return str(self.name)

    def apply(self, ticket):
        if ticket.state != self.from_state:
            raise ValueError('Invalid original state.')
        ticket.state = self.to_state
        if self.reassign_to:
            ticket.assigned_group = self.reassign_to


class TicketFlagType(Base):
    __tablename__ = 'tickets_flags_types'
    __table_args__ = (
        Comment('Ticket flag types'),
        Index('tickets_flags_types_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TICKETS',
                'cap_read':      'TICKETS_LIST',
                'cap_create':    'TICKETS_FLAGTYPES_CREATE',
                'cap_edit':      'TICKETS_FLAGTYPES_EDIT',
                'cap_delete':    'TICKETS_FLAGTYPES_DELETE',

                'show_in_menu':  'admin',
                'menu_name':     _('Ticket Flags'),
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('tftid', 'name'),
                'grid_hidden':   ('tftid',),
                'form_view':     ('name', 'descr'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),

                'create_wizard': SimpleWizard(
                                    title=_('Add new ticket flag type'))
            }
        })
    id = Column(
        'tftid',
        UInt32(),
        Sequence('tickets_flags_types_tftid_seq'),
        Comment('Ticket flag type ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Ticket flag type name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Ticket flag type description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    flagmap = relationship(
        'TicketFlag',
        backref=backref('type', innerjoin=True, lazy='joined'),
        cascade='all, delete-orphan',
        passive_deletes=True)
    flagmod = relationship(
        'TicketChangeFlagMod',
        backref=backref('flag_type', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    tickets = association_proxy(
        'flagmap',
        'ticket',
        creator=lambda v: TicketFlag(ticket=v))

    def __str__(self):
        return str(self.name)


class TicketFlag(Base):
    """
    Many-to-many relationship object. Links tickets and ticket flags.
    """
    __tablename__ = 'tickets_flags_def'
    __table_args__ = (
        Comment('Ticket flag mappings'),
        Index('tickets_flags_def_u_tf', 'ticketid', 'tftid', unique=True),
        Index('tickets_flags_def_i_tftid', 'tftid'),
        Trigger('after', 'insert', 't_tickets_flags_def_ai'),
        Trigger('after', 'delete', 't_tickets_flags_def_ad'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TICKETS',
                'cap_read':      'TICKETS_LIST',
                'cap_create':    'TICKETS_EDIT',
                'cap_edit':      'TICKETS_EDIT',
                'cap_delete':    'TICKETS_EDIT',

                'menu_name':     _('Ticket Flags')
            }
        })
    id = Column(
        'tfid',
        UInt32(),
        Sequence('tickets_flags_def_tfid_seq'),
        Comment('Ticket flag ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    ticket_id = Column(
        'ticketid',
        UInt32(),
        ForeignKey('tickets_def.ticketid',
                   name='tickets_flags_def_fk_ticketid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket ID'),
        nullable=False,
        info={
            'header_string': _('Ticket')
        })
    type_id = Column(
        'tftid',
        UInt32(),
        ForeignKey('tickets_flags_types.tftid',
                   name='tickets_flags_types_fk_tftid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket flag type ID'),
        nullable=False,
        info={
            'header_string': _('Type')
        })


class TicketFile(Base):
    """
    Many-to-many relationship object. Links tickets and files from VFS.
    """
    __tablename__ = 'tickets_files'
    __table_args__ = (
        Comment('File mappings to tickets'),
        Index('tickets_files_u_tfl', 'ticketid', 'fileid', unique=True),
        Index('tickets_files_i_fileid', 'fileid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TICKETS',
                'cap_read':      'TICKETS_LIST',
                'cap_create':    'FILES_ATTACH_2TICKETS',
                'cap_edit':      '__NOPRIV__',
                'cap_delete':    'FILES_ATTACH_2TICKETS',

                'menu_name':     _('Files'),
                'grid_view':     ('tfid', 'ticket', 'file'),
                'grid_hidden':   ('tfid',),

                'create_wizard': SimpleWizard(title=_('Attach file'))
            }
        })
    id = Column(
        'tfid',
        UInt32(),
        Sequence('tickets_files_tfid_seq'),
        Comment('Ticket-file mapping ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    ticket_id = Column(
        'ticketid',
        UInt32(),
        ForeignKey('tickets_def.ticketid', name='tickets_files_fk_ticketid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket ID'),
        nullable=False,
        info={
            'header_string': _('Ticket'),
            'column_flex': 1
        })
    file_id = Column(
        'fileid',
        UInt32(),
        ForeignKey('files_def.fileid', name='tickets_files_fk_fileid',
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
        backref=backref('linked_tickets',
                        cascade='all, delete-orphan',
                        passive_deletes=True))

    def __str__(self):
        return str(self.file)


def _wizfld_ticket_state(fld, model, req, **kwargs):
    sess = DBSession()
    data = []
    for ts in sess.query(TicketState).filter(
            TicketState.is_start.is_(True)).order_by('title', 'subtitle'):
        data.append({'id': ts.id, 'value': str(ts)})
    return {
        'xtype':          'combobox',
        'allowBlank':     False,
        'name':           'tstid',
        'format':         'string',
        'displayField':   'value',
        'valueField':     'id',
        'hiddenName':     'tstid',
        'queryMode':      'local',
        'editable':       False,
        'forceSelection': True,
        'store':          {
            'xtype':  'simplestore',
            'fields': ('id', 'value'),
            'data':   data
        },
        'fieldLabel':     req.localizer.translate(_('State'))
    }


def _wizfld_ticket_subscribe(fld, model, req, **kwargs):
    return {'xtype': 'checkbox',
            'name': 'subscribe',
            'fieldLabel': req.localizer.translate(_('Track this ticket')),
            'checked': req.settings.get('tickets.sub.default_on_new')}


def _wizfld_ticket_tpl(fld, model, req, **kwargs):
    sess = DBSession()
    data = []
    for tpl in sess.query(TicketTemplate):
        data.append({'id': tpl.id, 'value': str(tpl)})
    return {
        'xtype':          'combobox',
        'allowBlank':     False,
        'name':           'ttplid',
        'format':         'string',
        'displayField':   'value',
        'valueField':     'id',
        'hiddenName':     'ttplid',
        'queryMode':      'local',
        'editable':       False,
        'forceSelection': True,
        'store':          {
            'xtype':  'simplestore',
            'fields': ('id', 'value'),
            'data':   data
        },
        'fieldLabel':     req.localizer.translate(_('Template'))
    }


def _wizcb_ticket_submit(wiz, em, step, act, val, req):
    sess = DBSession()
    obj = Ticket(origin_id=1)
    em.set_values(obj, val, req, True)
    sess.add(obj)
    if 'parentid' in val:
        td = TicketDependency(parent_id=int(val['parentid']),
                              child=obj)
        sess.add(td)
    sess.flush()
    if val.get('subscribe'):
        tsub = UserTicketSubscription()
        tsub.user = req.user
        # TODO: allow custom flags
        tsub.notify_change = True
        tsub.ticket = obj
        tsub.is_issuer = True
        sess.add(tsub)
    req.run_hook('tickets.ticket.create', obj, req)
    return {'do': 'close',
            'affects': (('tickets', 'Ticket'),)}


def _wizcb_ticket_tpl_submit(wiz, em, step, act, val, req):
    sess = DBSession()
    if 'ttplid' not in val or 'entityid' not in val:
        raise ValueError
    tpl = sess.query(TicketTemplate).get(int(val['ttplid']))
    ent = sess.query(Entity).get(int(val['entityid']))
    if tpl is None or ent is None:
        raise KeyError
    obj = tpl.create_ticket(req, ent, None, val)
    sess.add(obj)
    if 'parentid' in val:
        td = TicketDependency(parent_id=int(val['parentid']),
                              child=obj)
        sess.add(td)
    sess.flush()
    if val.get('subscribe'):
        tsub = UserTicketSubscription()
        tsub.user = req.user
        # TODO: allow custom flags
        tsub.notify_change = True
        tsub.ticket = obj
        tsub.is_issuer = True
        sess.add(tsub)
    req.run_hook('tickets.ticket.create', obj, req)
    return {'do': 'close',
            'affects': (('tickets', 'Ticket'),)}


class Ticket(Base):
    """
    Main ticket object. Holds current ticket state.
    """
    __tablename__ = 'tickets_def'
    __table_args__ = (
        Comment('Tickets'),
        Index('tickets_def_i_entityid', 'entityid'),
        Index('tickets_def_i_name', 'name'),
        Index('tickets_def_i_tstid', 'tstid'),
        Index('tickets_def_i_cby', 'cby'),
        Index('tickets_def_i_mby', 'mby'),
        Index('tickets_def_i_tby', 'tby'),
        Index('tickets_def_i_assigned_uid', 'assigned_uid'),
        Index('tickets_def_i_assigned_gid', 'assigned_gid'),
        Index('tickets_def_i_toid', 'toid'),
        Index('tickets_def_i_archived', 'archived'),
        Trigger('before', 'insert', 't_tickets_def_bi'),
        Trigger('before', 'update', 't_tickets_def_bu'),
        Trigger('after', 'insert', 't_tickets_def_ai'),
        Trigger('after', 'update', 't_tickets_def_au'),
        Trigger('after', 'delete', 't_tickets_def_ad'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TICKETS',
                'cap_read':      'TICKETS_LIST',
                'cap_create':    'TICKETS_CREATE',
                'cap_edit':      'TICKETS_DIRECT',
                'cap_delete':    'TICKETS_DIRECT',

                'show_in_menu':  'modules',
                'menu_name':     _('Tickets'),
                'menu_main':     True,
                'default_sort':  ({'property': 'ctime', 'direction': 'DESC'},),
                'grid_view':     ('ticketid', 'entity', 'state',
                                  'ctime', 'mtime', 'assigned_time',
                                  'assigned_group', 'name'),
                'grid_hidden':   ('ticketid', 'ctime', 'mtime'),
                'form_view':     ('entity', 'name', 'state', 'flags', 'origin',
                                  'assigned_user', 'assigned_group',
                                  'assigned_time', 'dur',
                                  'archived', 'show_client', 'descr',
                                  'ctime', 'created_by',
                                  'mtime', 'modified_by',
                                  'ttime', 'transition_by'),
                'easy_search':   ('name',),
                'extra_data':    ('row_class',),
                'detail_pane':   ('netprofile_tickets.views', 'dpane_tickets'),
                'row_class_field': 'row_class',

                'create_wizard': Wizard(
                                   Step('entity', 'name',
                                        ExtJSWizardField(_wizfld_ticket_state),
                                        ExtJSWizardField(
                                            _wizfld_ticket_subscribe),
                                        'show_client', 'flags', 'descr',
                                        id='generic'),
                                   Step('assigned_user', 'assigned_group',
                                        CompositeWizardField(
                                            'assigned_time',
                                            ExtJSWizardField({
                                                'xtype':   'button',
                                                'text':    _('Schedule'),
                                                'iconCls': 'ico-schedule',
                                                'margin':  '0 0 0 2',
                                                'itemId':  'btn_sched'
                                            })),
                                        id='advanced',
                                        on_submit=_wizcb_ticket_submit),
                                   title=_('Add new ticket')),
                'wizards':       {
                    'tpl':       Wizard(
                                   Step('entity',
                                        ExtJSWizardField(_wizfld_ticket_tpl),
                                        ExtJSWizardField(
                                            _wizfld_ticket_subscribe),
                                        CompositeWizardField(
                                            'assigned_time',
                                            ExtJSWizardField({
                                                'xtype':   'button',
                                                'text':    _('Schedule'),
                                                'iconCls': 'ico-schedule',
                                                'margin':  '0 0 0 2',
                                                'itemId':  'btn_sched'
                                            })),
                                        'flags',
                                        id='generic',
                                        on_submit=_wizcb_ticket_tpl_submit),
                                   title=_('Add from template'))
                }
            }
        })
    id = Column(
        'ticketid',
        UInt32(),
        Sequence('tickets_def_ticketid_seq'),
        Comment('Ticket ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    entity_id = Column(
        'entityid',
        UInt32(),
        ForeignKey('entities_def.entityid', name='tickets_def_fk_entityid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Entity ID'),
        nullable=False,
        info={
            'header_string': _('Entity'),
            'filter_type': 'none',
            'write_cap': 'TICKETS_CHANGE_ENTITY',
            'column_flex': 1
        })
    state_id = Column(
        'tstid',
        UInt32(),
        ForeignKey('tickets_states_types.tstid', name='tickets_def_fk_tstid',
                   onupdate='CASCADE'),  # ondelete=RESTRICT
        Comment('Ticket state ID'),
        nullable=False,
        info={
            'header_string': _('State'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    origin_id = Column(
        'toid',
        UInt32(),
        ForeignKey('tickets_origins.toid', name='tickets_def_fk_toid',
                   onupdate='CASCADE'),  # ondelete=RESTRICT
        Comment('Ticket origin ID'),
        nullable=False,
        info={
            'header_string': _('Origin'),
            'filter_type': 'nplist'
        })
    assigned_user_id = Column(
        'assigned_uid',
        UInt32(),
        ForeignKey('users.uid', name='tickets_def_fk_assigned_uid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Assigned to user ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('User'),
            'filter_type': 'nplist',
            'write_cap': 'TICKETS_CHANGE_UID',
            'column_flex': 1
        })
    assigned_group_id = Column(
        'assigned_gid',
        UInt32(),
        ForeignKey('groups.gid', name='tickets_def_fk_assigned_gid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Assigned to group ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Group'),
            'filter_type': 'nplist',
            'write_cap': 'TICKETS_CHANGE_GID',
            'column_flex': 1
        })
    assigned_time = Column(
        TIMESTAMP(),
        Comment('Assigned to date'),
        nullable=True,
        default=None,
        info={
            'header_string': _('Due'),
            'write_cap': 'TICKETS_CHANGE_DATE'
        })
    duration = Column(
        'dur',
        UInt32(),
        Comment('Ticket duration (in sec)'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Duration'),
            'write_cap': 'TICKETS_CHANGE_DATE'
        })
    archived = Column(
        NPBoolean(),
        Comment('Is archived'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Archived'),
            'write_cap': 'TICKETS_ARCHIVAL'
        })
    show_client = Column(
        NPBoolean(),
        Comment('Show ticket to client'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Show to Client')
        })
    name = Column(
        Unicode(255),
        Comment('Ticket name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 2
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Ticket description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description'),
            'column_flex': 3
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
    transition_time = Column(
        'ttime',
        TIMESTAMP(),
        Comment('Last state transition timestamp'),
        nullable=True,
        default=None,
        info={
            'header_string': _('Transition'),
            'read_only': True
        })
    created_by_id = Column(
        'cby',
        UInt32(),
        ForeignKey('users.uid', name='tickets_def_fk_cby',
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
        ForeignKey('users.uid', name='tickets_def_fk_mby',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Modified by'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Modified'),
            'read_only': True
        })
    transition_by_id = Column(
        'tby',
        UInt32(),
        ForeignKey('users.uid', name='tickets_def_fk_tby',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Transition by'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Transition'),
            'read_only': True
        })

    entity = relationship(
        'Entity',
        innerjoin=True,
        lazy='joined',
        backref=backref('tickets',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    state = relationship(
        'TicketState',
        innerjoin=True,
        backref='tickets')
    origin = relationship(
        'TicketOrigin',
        innerjoin=True,
        backref='tickets')
    assigned_user = relationship(
        'User',
        foreign_keys=assigned_user_id,
        backref=backref('assigned_tickets',
                        passive_deletes=True))
    assigned_group = relationship(
        'Group',
        backref=backref('assigned_tickets',
                        passive_deletes=True))
    created_by = relationship(
        'User',
        foreign_keys=created_by_id,
        backref=backref('created_tickets',
                        passive_deletes=True))
    modified_by = relationship(
        'User',
        foreign_keys=modified_by_id,
        backref=backref('modified_tickets',
                        passive_deletes=True))
    transition_by = relationship(
        'User',
        foreign_keys=transition_by_id,
        backref=backref('transitioned_tickets',
                        passive_deletes=True))
    flagmap = relationship(
        'TicketFlag',
        backref=backref('ticket', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)
    filemap = relationship(
        'TicketFile',
        backref=backref('ticket', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)
    changes = relationship(
        'TicketChange',
        backref=backref('ticket', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)
    subscriptions = relationship(
        'TicketSubscription',
        backref=backref('ticket', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    flags = association_proxy(
        'flagmap',
        'type',
        creator=lambda v: TicketFlag(type=v))
    files = association_proxy(
        'filemap',
        'file',
        creator=lambda v: TicketFile(file=v))
    parents = association_proxy(
        'parent_map',
        'parent',
        creator=lambda v: TicketDependency(parent=v))
    children = association_proxy(
        'child_map',
        'child',
        creator=lambda v: TicketDependency(child=v))

    def __str__(self):
        return str(self.name)

    @classmethod
    def __augment_query__(cls, sess, query, params, req):
        flist = []
        if '__filter' in params:
            flist.extend(params['__filter'])
        if '__ffilter' in params:
            flist.extend(params['__ffilter'])
        for flt in flist:
            prop = flt.get('property', None)
            oper = flt.get('operator', None)
            value = flt.get('value', None)
            if prop == 'parentid':
                if oper in {'eq', '=', '==', '==='}:
                    query = query.join(
                            TicketDependency,
                            Ticket.id == TicketDependency.child_id).filter(
                                    TicketDependency.parent_id == int(value))
            if prop == 'childid':
                if oper in {'eq', '=', '==', '==='}:
                    query = query.join(
                            TicketDependency,
                            Ticket.id == TicketDependency.parent_id).filter(
                                    TicketDependency.child_id == int(value))
        # FIXME: Check TICKETS_LIST_ARCHIVED, TICKETS_OWN_LIST,
        #        TICKETS_OWNGROUP_LIST and ACLs.
        return query

    @classmethod
    def __augment_result__(cls, sess, res, params, req):
        populate_related_list(res, 'id', 'flagmap', TicketFlag,
                              sess.query(TicketFlag),
                              None, 'ticket_id')
        return res

    @property
    def end_time(self):
        if self.assigned_time and self.duration:
            return self.assigned_time + dt.timedelta(seconds=self.duration)
        return self.assigned_time

    @property
    def row_class(self):
        if self.state:
            return self.state.style

    @validates('state')
    def _set_state(self, key, new_state):
        if not self.duration and new_state.duration:
            self.duration = new_state.duration
        return new_state

    def test_time(self, d):
        if self.assigned_user and self.assigned_user.schedule_map:
            if not self.assigned_user.schedule_map.scheduler.test_time(d):
                return False
        if self.assigned_group and self.assigned_group.schedule_map:
            if not self.assigned_group.schedule_map.scheduler.test_time(d):
                return False
        return True

    def get_entity_history(self, req):
        eh = EntityHistory(self.entity,
                           req.localizer.translate(
                               _('Ticket #%d Created: %s')) % (self.id,
                                                               self.name),
                           self.creation_time,
                           (None
                            if self.created_by is None
                            else str(self.created_by)))
        if self.description:
            eh.parts.append(EntityHistoryPart('tickets:comment',
                                              self.description))
        return eh


@event.listens_for(Ticket.state_id, 'set', active_history=True)
def _on_set_ticket_state_id(tgt, value, oldvalue, initiator):
    if value is None:
        tgt.state = None
    elif value != oldvalue:
        tgt.state = DBSession().query(TicketState).get(value)
    return value


@event.listens_for(Ticket.assigned_user_id, 'set', active_history=True)
def _on_set_ticket_assigned_user_id(tgt, value, oldvalue, initiator):
    if value is None:
        tgt.assigned_user = None
    elif value != oldvalue:
        tgt.assigned_user = DBSession().query(User).get(value)
    return value


@event.listens_for(Ticket.assigned_group_id, 'set', active_history=True)
def _on_set_ticket_assigned_group_id(tgt, value, oldvalue, initiator):
    if value is None:
        tgt.assigned_group = None
    elif value != oldvalue:
        tgt.assigned_group = DBSession().query(Group).get(value)
    return value


class TicketTemplate(Base):
    """
    Template for a new ticket.
    """
    __tablename__ = 'tickets_templates'
    __table_args__ = (
        Comment('Templates for new tickets'),
        Index('tickets_templates_u_name', 'name', unique=True),
        Index('tickets_templates_i_assign_uid', 'assign_uid'),
        Index('tickets_templates_i_assign_gid', 'assign_gid'),
        Index('tickets_templates_i_tstid', 'tstid'),
        Index('tickets_templates_i_toid', 'toid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_ADMIN',
                'cap_read':      'TICKETS_CREATE',
                'cap_create':    'TICKETS_TEMPLATES_CREATE',
                'cap_edit':      'TICKETS_TEMPLATES_EDIT',
                'cap_delete':    'TICKETS_TEMPLATES_DELETE',

                'show_in_menu':  'admin',
                'menu_name':     _('Templates'),
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('ttplid', 'name'),
                'grid_hidden':   ('ttplid',),
                'form_view':     ('name',
                                  'tpl_name', 'tpl_descr',
                                  'assign_self', 'assign_owngrp',
                                  'assign_to_user', 'assign_to_group',
                                  'scheduler', 'dur',
                                  'state', 'origin',
                                  'on_create'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),

                'create_wizard': SimpleWizard(title=_('Add new template'))
            }
        })
    id = Column(
        'ttplid',
        UInt32(),
        Sequence('tickets_templates_ttplid_seq'),
        Comment('Ticket template ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Ticket template name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })
    name_template = Column(
        'tpl_name',
        Unicode(255),
        Comment('Template for new ticket name'),
        nullable=False,
        info={
            'header_string': _('Name Template')
        })
    description_template = Column(
        'tpl_descr',
        UnicodeText(),
        Comment('Template for new ticket description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description Template')
        })
    assign_to_self = Column(
        'assign_self',
        NPBoolean(),
        Comment('Assign to logged in user'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Assign to Self')
        })
    assign_to_own_group = Column(
        'assign_owngrp',
        NPBoolean(),
        Comment('Assign to user\'s group'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Assign to My Group')
        })
    assign_to_user_id = Column(
        'assign_uid',
        UInt32(),
        ForeignKey('users.uid', name='tickets_templates_fk_assign_uid',
                   onupdate='CASCADE'),  # ondelete=RESTRICT
        Comment('Assign to user ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Assign to User')
        })
    assign_to_group_id = Column(
        'assign_gid',
        UInt32(),
        ForeignKey('groups.gid', name='tickets_templates_fk_assign_gid',
                   onupdate='CASCADE'),  # ondelete=RESTRICT
        Comment('Assign to group ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Assign to Group')
        })
    scheduler_id = Column(
        'tschedid',
        UInt32(),
        ForeignKey('tickets_schedulers.tschedid',
                   name='tickets_templates_fk_tschedid',
                   onupdate='CASCADE'),  # ondelete=RESTRICT
        Comment('Ticket scheduler ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Scheduler')
        })
    duration = Column(
        'dur',
        UInt32(),
        Comment('Default ticket duration (in sec)'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Duration')
        })
    state_id = Column(
        'tstid',
        UInt32(),
        ForeignKey('tickets_states_types.tstid',
                   name='tickets_templates_fk_tstid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Initial state'),
        nullable=False,
        info={
            'header_string': _('State')
        })
    origin_id = Column(
        'toid',
        UInt32(),
        ForeignKey('tickets_origins.toid', name='tickets_templates_fk_toid',
                   onupdate='CASCADE'),  # ondelete=RESTRICT
        Comment('Ticket origin ID'),
        nullable=False,
        info={
            'header_string': _('Origin'),
            'filter_type': 'nplist'
        })
    callback_on_create = Column(
        'on_create',
        ASCIIString(255),
        Comment('Callback on ticket creation'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Creation Callback')
        })

    assign_to_user = relationship('User')
    assign_to_group = relationship('Group')
    state = relationship('TicketState', innerjoin=True)
    origin = relationship('TicketOrigin', innerjoin=True)
    scheduler = relationship('TicketScheduler')

    def __str__(self):
        return str(self.name)

    def create_ticket(self, req, entity, args=None, values=None):
        tpl_param = {
            'user':   req.user,
            'group':  req.user.group,
            'entity': entity,
            'tpl':    self
        }
        if self.assign_to_self:
            tpl_param['ass_user'] = req.user
        elif self.assign_to_user:
            tpl_param['ass_user'] = self.assign_to_user
        if self.assign_to_own_group:
            tpl_param['ass_group'] = req.user.group
        elif self.assign_to_group:
            tpl_param['ass_group'] = self.assign_to_group
        if self.state:
            tpl_param['state'] = self.state
        if self.origin:
            tpl_param['origin'] = self.origin
        if args is not None:
            tpl_param.update(args)

        t = Ticket()
        t.entity = entity
        if self.state:
            t.state = self.state
        if self.origin:
            t.origin = self.origin
        if 'ass_user' in tpl_param:
            t.assigned_user = tpl_param['ass_user']
        if 'ass_group' in tpl_param:
            t.assigned_group = tpl_param['ass_group']
        if self.duration:
            t.duration = self.duration

        if values is not None:
            em = ExtModel(Ticket)
            em.set_values(t, values, req, True)
        if self.name_template and not t.name:
            t.name = self.name_template.format(**tpl_param)
        if self.description_template and not t.description:
            t.description = self.description_template.format(**tpl_param)

        if self.callback_on_create:
            cfg = self.callback_on_create.split(':')
            if len(cfg) != 2:
                raise ValueError('Invalid callback specification')
            # FIXME: handle exceptions or pass them up?
            mod = importlib.import_module(cfg[0])
            cb = getattr(mod, cfg[1], None)
            if callable(cb):
                cb(self, t)
        return t


class TicketChangeField(Base):
    """
    Type of a ticket field change.
    """
    __tablename__ = 'tickets_changes_fields'
    __table_args__ = (
        Comment('Ticket change fields'),
        Index('tickets_changes_fields_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_ADMIN',
                'cap_read':      'TICKETS_LIST',
                'cap_create':    'ADMIN_DEV',
                'cap_edit':      'ADMIN_DEV',
                'cap_delete':    'ADMIN_DEV',

                'show_in_menu':  'admin',
                'menu_name':     _('Change Fields'),
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('tcfid', 'name'),
                'grid_hidden':   ('tcfid',),
                'easy_search':   ('name',),

                'create_wizard': SimpleWizard(title=_('Add new change field'))
            }
        })
    id = Column(
        'tcfid',
        UInt32(),
        Sequence('tickets_changes_fields_tcfid_seq', start=101, increment=1),
        Comment('Ticket change field ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Ticket change field name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })

    bits = relationship(
        'TicketChangeBit',
        backref=backref('field', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    def __str__(self):
        req = getattr(self, '__req__', None)
        if req:
            return req.localizer.translate(_(self.name))
        return str(self.name)


class TicketChange(Base):
    """
    Describes an atomic ticket change.
    """
    __tablename__ = 'tickets_changes_def'
    __table_args__ = (
        Comment('Ticket changes'),
        Index('tickets_changes_def_i_ticketid', 'ticketid'),
        Index('tickets_changes_def_i_uid', 'uid'),
        Index('tickets_changes_def_i_ts', 'ts'),
        Index('tickets_changes_def_i_ttrid', 'ttrid'),
        Index('tickets_changes_def_i_show_client', 'show_client'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TICKETS',
                'cap_read':      'TICKETS_LIST',
                'cap_create':    '__NOPRIV__',
                'cap_edit':      '__NOPRIV__',
                'cap_delete':    '__NOPRIV__',

                'menu_name':     _('Changes'),
                'default_sort':  ({'property': 'ts', 'direction': 'DESC'},),
                'grid_view':     ('tcid', 'ticket', 'ts',
                                  MarkupColumn(
                                      name='data',
                                      header_string=_('Information'),
                                      column_flex=3,
                                      template=TemplateObject(
                                          'netprofile_tickets:'
                                          'templates/tc_data.mak')),
                                  MarkupColumn(
                                      name='changes',
                                      header_string=_('Changes'),
                                      column_flex=3,
                                      template=TemplateObject(
                                          'netprofile_tickets:'
                                          'templates/tc_changes.mak')),
                                  'transition', 'user', 'comments'),
                'grid_hidden':   ('tcid', 'transition', 'user'),
                'easy_search':   ('comments',),
                'extra_data':    ('data',)
            }
        })
    id = Column(
        'tcid',
        UInt32(),
        Sequence('tickets_changes_def_tcid_seq'),
        Comment('Ticket change ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    ticket_id = Column(
        'ticketid',
        UInt32(),
        ForeignKey('tickets_def.ticketid',
                   name='tickets_changes_def_fk_ticketid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket ID'),
        nullable=False,
        info={
            'header_string': _('Ticket'),
            'filter_type': 'none'
        })
    transition_id = Column(
        'ttrid',
        UInt32(),
        ForeignKey('tickets_states_trans.ttrid',
                   name='tickets_changes_def_fk_ttrid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('Ticket transition ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Transition'),
            'filter_type': 'nplist'
        })
    user_id = Column(
        'uid',
        UInt32(),
        ForeignKey('users.uid', name='tickets_changes_def_fk_uid',
                   ondelete='SET NULL', onupdate='CASCADE'),
        Comment('User ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('User'),
            'filter_type': 'nplist'
        })
    timestamp = Column(
        'ts',
        TIMESTAMP(),
        Comment('Ticket change timestamp'),
        CurrentTimestampDefault(),
        nullable=False,
        info={
            'header_string': _('Time')
        })
    show_client = Column(
        NPBoolean(),
        Comment('Show comment to client'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Show to Client')
        })
    from_client = Column(
        NPBoolean(),
        Comment('This change is from client'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('From Client')
        })
    comments = Column(
        UnicodeText(),
        Comment('Ticket change comments'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Comments'),
            'column_flex': 5
        })

    transition = relationship(
        'TicketStateTransition',
        backref=backref('ticket_changes',
                        passive_deletes=True))
    user = relationship(
        'User',
        backref=backref('ticket_changes',
                        passive_deletes=True))
    bits = relationship(
        'TicketChangeBit',
        backref=backref('change', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)
    flagmod = relationship(
        'TicketChangeFlagMod',
        backref=backref('change', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    @property
    def data(self):
        return {'bits': self.bits}

    def get_entity_history(self, req):
        eh = EntityHistory(
            self.ticket.entity,
            req.localizer.translate(_('Ticket #%d Changed: %s')) % (
                                    self.ticket_id,
                                    self.ticket.name),
            self.timestamp,
            None if self.user is None else str(self.user))
        if self.transition:
            eh.parts.append(EntityHistoryPart('tickets:trans',
                                              str(self.transition)))
        for bit in self.bits:
            new = bit.get_new()
            old = bit.get_old()
            if new:
                eh.parts.append(new)
            if old:
                eh.parts.append(old)
        if self.comments:
            eh.parts.append(EntityHistoryPart('tickets:comment',
                                              self.comments))
        return eh

    def __str__(self):
        req = getattr(self, '__req__', None)
        tpl = _('Ticket #%d: change #%d')
        if req:
            tpl = req.localizer.translate(tpl)
        return tpl % (self.ticket_id, self.id)


class TicketChangeBit(Base):
    """
    Describes an single ticket property change.
    """
    __tablename__ = 'tickets_changes_bits'
    __table_args__ = (
        Comment('Ticket change bits'),
        Index('tickets_changes_bits_u_tcf', 'tcid', 'tcfid', unique=True),
        Index('tickets_changes_bits_i_tcfid', 'tcfid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TICKETS',
                'cap_read':      'TICKETS_LIST',
                'cap_create':    '__NOPRIV__',
                'cap_edit':      '__NOPRIV__',
                'cap_delete':    '__NOPRIV__',

                'menu_name':     _('Change Bits'),
                'default_sort':  (),
                'grid_view':     (),
                'easy_search':   ()
            }
        })
    id = Column(
        'tcbid',
        UInt32(),
        Sequence('tickets_changes_bits_tcbid_seq'),
        Comment('Ticket change bit ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    change_id = Column(
        'tcid',
        UInt32(),
        ForeignKey('tickets_changes_def.tcid',
                   name='tickets_changes_bits_fk_tcid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket change ID'),
        nullable=False,
        info={
            'header_string': _('Change'),
            'filter_type': 'none'
        })
    field_id = Column(
        'tcfid',
        UInt32(),
        ForeignKey('tickets_changes_fields.tcfid',
                   name='tickets_changes_bits_fk_tcfid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket change field ID'),
        nullable=False,
        info={
            'header_string': _('Field'),
            'filter_type': 'nplist'
        })
    old = Column(
        Unicode(255),
        Comment('Old value'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Old')
        })
    new = Column(
        Unicode(255),
        Comment('New value'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('New')
        })

    def get_object(self, obj):
        if obj is None:
            return None
        sess = DBSession()
        if self.field_id == 1:
            return sess.query(User).get(int(obj))
        if self.field_id == 2:
            return sess.query(Group).get(int(obj))
        if self.field_id == 3:
            return dparse(obj)
        if self.field_id == 4:
            return True if obj == 'Y' else False
        if self.field_id == 5:
            return sess.query(Entity).get(int(obj))

    def get_text(self, obj):
        if self.field_id == 4:
            if obj:
                return _('Archived')
            return _('Unarchived')
        return str(obj)

    def get_old(self):
        if self.field_id not in _HIST_MAP:
            return None
        if self.field_id == 4:
            return None
        name = '%s_old' % (_HIST_MAP[self.field_id],)
        obj = self.get_object(self.old)
        if obj is None:
            return None
        return EntityHistoryPart(name, self.get_text(obj))

    def get_new(self):
        if self.field_id not in _HIST_MAP:
            return None
        name = '%s_new' % (_HIST_MAP[self.field_id],)
        obj = self.get_object(self.new)
        if obj is None:
            return None
        return EntityHistoryPart(name, self.get_text(obj))

    def __json__(self, req=None):
        ret = []
        if self.field_id not in _HIST_MAP:
            return ret
        name = _HIST_MAP[self.field_id]
        if self.field_id != 4 and self.old is not None:
            ret.append({
                'icon': name[8:] + '_old',
                'text': self.get_text(self.get_object(self.old))
            })
        if self.new is not None:
            ret.append({
                'icon': name[8:] + '_new',
                'text': self.get_text(self.get_object(self.new))
            })
        return ret


class TicketScheduler(Base):
    """
    A helper object to automatically schedule tickets.
    """
    __tablename__ = 'tickets_schedulers'
    __table_args__ = (
        Comment('Ticket scheduling presets'),
        Index('tickets_schedulers_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_ADMIN',
                'cap_read':      'TICKETS_CREATE',
                'cap_create':    'TICKETS_SCHEDULES_CREATE',
                'cap_edit':      'TICKETS_SCHEDULES_EDIT',
                'cap_delete':    'TICKETS_SCHEDULES_DELETE',

                'show_in_menu':  'admin',
                'menu_name':     _('Schedulers'),
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('tschedid', 'name'),
                'grid_hidden':   ('tschedid',),
                'form_view':     ('name',
                                  'sim_user', 'sim_group', 'ov_dur',
                                  'hour_start', 'hour_end',
                                  'wdays', 'spacing'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),

                'create_wizard': SimpleWizard(
                                    title=_('Add new scheduling preset'))
            }
        })
    id = Column(
        'tschedid',
        UInt32(),
        Sequence('tickets_schedulers_tschedid_seq'),
        Comment('Ticket scheduler ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    name = Column(
        Unicode(255),
        Comment('Ticket scheduler name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 1
        })
    sim_user = Column(
        UInt32(),
        Comment('Max. simultaneous per user'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Max. Simultaneous per User')
        })
    sim_group = Column(
        UInt32(),
        Comment('Max. simultaneous per group'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Max. Simultaneous per Group')
        })
    # FIXME: add option: max. group sim = num. of group members
    override_duration = Column(
        'ov_dur',
        UInt32(),
        Comment('Overridden ticket duration (in sec)'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Force Duration')
        })
    start_hour = Column(
        'hour_start',
        UInt8(),
        Comment('Allowed starting hour'),
        nullable=False,
        default=0,
        server_default=text('0'),
        info={
            'header_string': _('Start Hour'),
            'max_value': 23
        })
    end_hour = Column(
        'hour_end',
        UInt8(),
        Comment('Allowed ending hour'),
        nullable=False,
        default=23,
        server_default=text('23'),
        info={
            'header_string': _('End Hour'),
            'max_value': 23
        })
    allowed_weekdays = Column(
        'wdays',
        UInt8(),
        Comment('Weekdays bitmask'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Weekdays'),
            'editor_xtype': 'weekdays'
        })
    spacing = Column(
        UInt32(),
        Comment('Ticket spacing (in sec)'),
        nullable=False,
        default=3600,
        server_default=text('3600'),
        info={
            'header_string': _('Ticket Spacing')
        })

    def __str__(self):
        return str(self.name)

    def test_time(self, d):
        if self.start_hour is not None and d.hour < self.start_hour:
            return False
        if self.end_hour is not None and d.hour > self.end_hour:
            return False
        if self.allowed_weekdays:
            if not self.allowed_weekdays & (1 << d.weekday()):
                return False
        # TODO: add exclusion periods
        return True

    @classmethod
    def find_schedule(cls, tkt, sched, from_dt, to_dt, user=None, group=None,
                      max_dates=5, duration=None):
        if not sched:
            return [from_dt]
        sess = DBSession()
        found = []
        expr = False
        sim_user = sim_group = spacing = None
        if user:
            if group:
                expr = or_(Ticket.assigned_user == user,
                           Ticket.assigned_group == group)
            else:
                expr = (Ticket.assigned_user == user)
        elif group:
            expr = (Ticket.assigned_group == group)
        for s in sched:
            if s.sim_user and (sim_user is None or sim_user > s.sim_user):
                sim_user = s.sim_user
            if s.sim_group and (sim_group is None or sim_group > s.sim_group):
                sim_group = s.sim_group
            if spacing is None or spacing > s.spacing:
                spacing = s.spacing
        if duration is None:
            if tkt and tkt.duration:
                duration = tkt.duration
            else:
                duration = 0
        cur_dt = from_dt
        while cur_dt < to_dt:
            is_ok = True
            end_dt = cur_dt
            if duration:
                end_dt += dt.timedelta(seconds=duration)
            for s in sched:
                if not s.test_time(cur_dt):
                    is_ok = False
                    break
            if is_ok:
                found_user = found_group = 0
                oldq = sess.query(Ticket).options(lazyload('entity')).filter(
                        Ticket.assigned_time < end_dt,
                        IntervalSeconds(Ticket.assigned_time,
                                        Ticket.duration) > cur_dt,
                        expr)
                if tkt and tkt.id:
                    oldq = oldq.filter(Ticket.id != tkt.id)
                for oldtkt in oldq:
                    if oldtkt.assigned_user == user:
                        found_user += 1
                    if oldtkt.assigned_group == group:
                        found_group += 1
                if user and sim_user and found_user >= sim_user:
                    is_ok = False
                if group and sim_group and found_group >= sim_group:
                    is_ok = False
                if is_ok:
                    found.append(cur_dt)
                    if len(found) >= max_dates:
                        break
            cur_dt += dt.timedelta(seconds=spacing)
        return found

    def find(self, tkt, from_dt, to_dt, user=None, group=None,
             max_dates=5, duration=None):
        sess = DBSession()
        found = []
        expr = False
        if user:
            if group:
                expr = or_(Ticket.assigned_user == user,
                           Ticket.assigned_group == group)
            else:
                expr = (Ticket.assigned_user == user)
        elif group:
            expr = (Ticket.assigned_group == group)
        if duration is None:
            if tkt and tkt.duration:
                duration = tkt.duration
            else:
                duration = 0
        cur_dt = from_dt
        while cur_dt < to_dt:
            is_ok = True
            end_dt = cur_dt
            if duration:
                end_dt += dt.timedelta(seconds=duration)
            if self.test_time(cur_dt) and (tkt is None
                                           or tkt.test_time(cur_dt)):
                found_user = found_group = 0
                oldq = sess.query(Ticket).options(lazyload('entity')).filter(
                        Ticket.assigned_time < end_dt,
                        IntervalSeconds(Ticket.assigned_time,
                                        Ticket.duration) > cur_dt,
                        expr)
                if tkt and tkt.id:
                    oldq = oldq.filter(Ticket.id != tkt.id)
                for oldtkt in oldq:
                    if oldtkt.assigned_user == user:
                        found_user += 1
                    if oldtkt.assigned_group == group:
                        found_group += 1
                if user and self.sim_user and found_user >= self.sim_user:
                    is_ok = False
                if group and self.sim_group and found_group >= self.sim_group:
                    is_ok = False
                if is_ok:
                    found.append(cur_dt)
                    if len(found) >= max_dates:
                        break
            cur_dt += dt.timedelta(seconds=self.spacing)
        return found


class TicketSchedulerUserAssignment(Base):
    """
    """
    __tablename__ = 'tickets_sched_assign_users'
    __table_args__ = (
        Comment('Ticket scheduling assignments for users'),
        Index('tickets_sched_assign_users_u_uid', 'uid', unique=True),
        Index('tickets_sched_assign_users_i_tschedid', 'tschedid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_ADMIN',
                'cap_read':      'TICKETS_CREATE',
                'cap_create':    'TICKETS_SCHEDULES_EDIT',
                'cap_edit':      'TICKETS_SCHEDULES_EDIT',
                'cap_delete':    'TICKETS_SCHEDULES_EDIT',

                'menu_name':     _('Scheduler Assignments for Users'),
                'grid_view':     ('tschedassid', 'user', 'scheduler'),
                'grid_hidden':   ('tschedassid',),

                'create_wizard': SimpleWizard(
                                    title=_('Add new scheduling assignment'))
            }
        })
    id = Column(
        'tschedassid',
        UInt32(),
        Sequence('tickets_sched_assign_users_tschedassid_seq'),
        Comment('Scheduler assignment ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    user_id = Column(
        'uid',
        UInt32(),
        ForeignKey('users.uid', name='tickets_sched_assign_users_fk_uid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('User ID'),
        nullable=False,
        info={
            'header_string': _('User'),
            'column_flex': 1
        })
    scheduler_id = Column(
        'tschedid',
        UInt32(),
        ForeignKey('tickets_schedulers.tschedid',
                   name='tickets_sched_assign_users_fk_tschedid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket scheduler ID'),
        nullable=False,
        info={
            'header_string': _('Scheduler'),
            'column_flex': 1
        })

    user = relationship(
        'User',
        innerjoin=True,
        backref=backref('schedule_map', uselist=False))
    scheduler = relationship(
        'TicketScheduler',
        innerjoin=True,
        backref='users')

    def __str__(self):
        return str(self.scheduler)


class TicketSchedulerGroupAssignment(Base):
    """
    """
    __tablename__ = 'tickets_sched_assign_groups'
    __table_args__ = (
        Comment('Ticket scheduling assignments for groups'),
        Index('tickets_sched_assign_groups_u_gid', 'gid', unique=True),
        Index('tickets_sched_assign_groups_i_tschedid', 'tschedid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_ADMIN',
                'cap_read':      'TICKETS_CREATE',
                'cap_create':    'TICKETS_SCHEDULES_EDIT',
                'cap_edit':      'TICKETS_SCHEDULES_EDIT',
                'cap_delete':    'TICKETS_SCHEDULES_EDIT',

                'menu_name':     _('Scheduler Assignments for Groups'),
                'grid_view':     ('tschedassid', 'group', 'scheduler'),
                'grid_hidden':   ('tschedassid',),

                'create_wizard': SimpleWizard(
                                    title=_('Add new scheduling assignment'))
            }
        })
    id = Column(
        'tschedassid',
        UInt32(),
        Sequence('tickets_sched_assign_groups_tschedassid_seq'),
        Comment('Scheduler assignment ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    group_id = Column(
        'gid',
        UInt32(),
        ForeignKey('groups.gid', name='tickets_sched_assign_groups_fk_gid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Group ID'),
        nullable=False,
        info={
            'header_string': _('Group'),
            'column_flex': 1
        })
    scheduler_id = Column(
        'tschedid',
        UInt32(),
        ForeignKey('tickets_schedulers.tschedid',
                   name='tickets_sched_assign_groups_fk_tschedid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket scheduler ID'),
        nullable=False,
        info={
            'header_string': _('Scheduler'),
            'column_flex': 1
        })

    group = relationship(
        'Group',
        innerjoin=True,
        backref=backref('schedule_map', uselist=False))
    scheduler = relationship(
        'TicketScheduler',
        innerjoin=True,
        backref='groups')

    def __str__(self):
        return str(self.scheduler)


class TicketChangeFlagMod(Base):
    """
    Describes a single change in ticket flag state.
    """
    __tablename__ = 'tickets_changes_flagmod'
    __table_args__ = (
        Comment('Ticket change bits modifying flags'),
        Index('tickets_changes_flagmod_u_tcflag', 'tcid', 'tftid',
              unique=True),
        Index('tickets_changes_flagmod_i_tftid', 'tftid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TICKETS',
                'cap_read':      'TICKETS_LIST',
                'cap_create':    '__NOPRIV__',
                'cap_edit':      '__NOPRIV__',
                'cap_delete':    '__NOPRIV__',

                'menu_name':     _('Flag Bits'),
                'default_sort':  (),
                'grid_view':     (),
                'easy_search':   ()
            }
        })
    id = Column(
        'tcfmodid',
        UInt32(),
        Sequence('tickets_changes_flagmod_tcfmodid_seq'),
        Comment('Ticket change flag modification ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    change_id = Column(
        'tcid',
        UInt32(),
        ForeignKey('tickets_changes_def.tcid',
                   name='tickets_changes_flagmod_fk_tcid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket change ID'),
        nullable=False,
        info={
            'header_string': _('Change')
        })
    flag_type_id = Column(
        'tftid',
        UInt32(),
        ForeignKey('tickets_flags_types.tftid',
                   name='tickets_changes_flagmod_fk_tftid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket flag type ID'),
        nullable=False,
        info={
            'header_string': _('Flag')
        })
    new_state = Column(
        'newstate',
        NPBoolean(),
        Comment('Resulting flag state'),
        nullable=False,
        info={
            'header_string': _('State')
        })


class TicketDependency(Base):
    """
    Describes a parent-child relationship between tickets.
    """
    __tablename__ = 'tickets_dependencies'
    __table_args__ = (
        Comment('Ticket resolution dependencies'),
        Index('tickets_dependencies_i_ticketid_child', 'ticketid_child'),
        Trigger('before', 'insert', 't_tickets_dependencies_bi'),
        Trigger('before', 'update', 't_tickets_dependencies_bu'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TICKETS',
                'cap_read':      'TICKETS_LIST',
                'cap_create':    '__NOPRIV__',
                'cap_edit':      '__NOPRIV__',
                'cap_delete':    '__NOPRIV__',

                'menu_name':     _('Dependencies'),
                'default_sort':  (),
                'grid_view':     (),
                'easy_search':   ()
            }
        })
    parent_id = Column(
        'ticketid_parent',
        UInt32(),
        ForeignKey('tickets_def.ticketid',
                   name='tickets_dependencies_fk_ticketid_parent',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket which is dependent on'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('Parent'),
            'filter_type': 'none'
        })
    child_id = Column(
        'ticketid_child',
        UInt32(),
        ForeignKey('tickets_def.ticketid',
                   name='tickets_dependencies_fk_ticketid_child',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket which depends on a parent'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('Child'),
            'filter_type': 'none'
        })

    parent = relationship(
        'Ticket',
        foreign_keys=parent_id,
        innerjoin=True,
        backref=backref('child_map',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    child = relationship(
        'Ticket',
        foreign_keys=child_id,
        innerjoin=True,
        backref=backref('parent_map',
                        cascade='all, delete-orphan',
                        passive_deletes=True))


class TicketSubscriptionType(DeclEnum):
    """
    Type of subscribed entity.
    """
    user = 'U', _('User'), 10
    group = 'G', _('Group'), 20
    entity = 'E', _('Entity'), 30
    address = 'A', _('Address'), 40


class TicketSubscription(Base):
    """
    Describes one link between a ticket and a user, a group or
    an external address.
    """
    __tablename__ = 'tickets_subscriptions'
    __table_args__ = (
        Comment('Ticket subscriptions'),
        Index('tickets_subscriptions_i_ticketid', 'ticketid'),
        Index('tickets_subscriptions_i_uid', 'uid'),
        Index('tickets_subscriptions_i_gid', 'gid'),
        Index('tickets_subscriptions_i_entityid', 'entityid'),
        Index('tickets_subscriptions_u_sub',
              'ticketid', 'uid', 'gid', 'entityid', 'addr',
              unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TICKETS',
                'cap_read':      'TICKETS_LIST',

                'menu_name':     _('Subscriptions'),
                'grid_view':     ('tsubid', 'type', 'ticket',
                                  'user', 'group', 'entity', 'address'),
                'grid_hidden':   ('tsubid',),
                'form_view':     ('type', 'ticket',
                                  'user', 'group', 'entity', 'address',
                                  'issuer',
                                  'notify_change',
                                  'notify_transition',
                                  'notify_close'),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),

                'create_wizard': SimpleWizard(
                                    title=_('Add new ticket subscription'))
            }
        })
    id = Column(
        'tsubid',
        UInt32(),
        Sequence('tickets_subscriptions_tsubid_seq'),
        Comment('Ticket subscription ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    type = Column(
        TicketSubscriptionType.db_type(),
        Comment('Ticket subscription type'),
        nullable=False,
        default=TicketSubscriptionType.user,
        server_default=TicketSubscriptionType.user,
        info={
            'header_string': _('Type'),
            'column_flex': 2
        })
    ticket_id = Column(
        'ticketid',
        UInt32(),
        ForeignKey('tickets_def.ticketid',
                   name='tickets_subscriptions_fk_ticketid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket ID'),
        nullable=False,
        info={
            'header_string': _('Ticket'),
            'filter_type': 'none'
        })
    user_id = Column(
        'uid',
        UInt32(),
        ForeignKey('users.uid', name='tickets_subscriptions_fk_uid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('User ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('User'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    group_id = Column(
        'gid',
        UInt32(),
        ForeignKey('groups.gid', name='tickets_subscriptions_fk_gid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Group ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Group'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    entity_id = Column(
        'entityid',
        UInt32(),
        ForeignKey('entities_def.entityid',
                   name='tickets_subscriptions_fk_entityid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Entity ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Entity'),
            'filter_type': 'none',
            'column_flex': 1
        })
    address = Column(
        'addr',
        Unicode(255),
        Comment('E-mail address'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Address'),
            'vtype': 'email',
            'column_flex': 3
        })
    notify_change = Column(
        NPBoolean(),
        Comment('Notify on any ticket change'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('On Change')
        })
    notify_transition = Column(
        NPBoolean(),
        Comment('Notify on ticket state transition'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('On Transition')
        })
    notify_close = Column(
        NPBoolean(),
        Comment('Notify when ticket is closed (reaches end state)'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('On Close')
        })
    is_issuer = Column(
        'issuer',
        NPBoolean(),
        Comment('Is ticket issued by this subscriber'),
        nullable=False,
        default=False,
        server_default=npbool(False),
        info={
            'header_string': _('Issuer')
        })
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'X',
        'with_polymorphic': '*'
    }

    user = relationship(
        'User',
        backref=backref('ticket_subscriptions',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    group = relationship(
        'Group',
        backref=backref('ticket_subscriptions',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    entity = relationship(
        'Entity',
        backref=backref('ticket_subscriptions',
                        cascade='all, delete-orphan',
                        passive_deletes=True))

    def check(self, ticket, change=None):
        if change:
            if self.notify_change:
                return True
            if change.transition:
                if self.notify_transition:
                    return True
                tr = change.transition
                if self.notify_close and tr.to_state.is_end:
                    return True
        if self.notify_close and ticket.archived:
            return True
        return False

    def get_addresses(self):
        raise NotImplementedError

    @property
    def template_vars(self):
        return {}

    @classmethod
    def __augment_query__(cls, sess, query, params, req):
        if not req.has_permission('TICKETS_SUBSCRIPTIONS_LIST'):
            query = query.filter(or_(
                TicketSubscription.user_id == req.user.id,
                TicketSubscription.group_id == req.user.group_id))
        return query

    @classmethod
    def __augment_create__(cls, sess, obj, values, req):
        if req.has_permission('TICKETS_SUBSCRIPTIONS_CREATE'):
            return True
        return obj.user_id == req.user.id

    @classmethod
    def __augment_update__(cls, sess, obj, values, req):
        if req.has_permission('TICKETS_SUBSCRIPTIONS_EDIT'):
            return True
        return obj.user_id == req.user.id

    @classmethod
    def __augment_delete__(cls, sess, obj, values, req):
        if req.has_permission('TICKETS_SUBSCRIPTIONS_DELETE'):
            return True
        return obj.user_id == req.user.id


class UserTicketSubscription(TicketSubscription):
    """
    Describes one link between a ticket and a user.
    """
    __mapper_args__ = {
        'polymorphic_identity': TicketSubscriptionType.user
    }

    def get_addresses(self):
        if not self.user:
            raise StopIteration
        for addr in self.user.email_addresses:
            yield addr.address

    @property
    def template_vars(self):
        if self.user:
            return {'recipient_type': 'user',
                    'user': self.user}
        return {}


class GroupTicketSubscription(TicketSubscription):
    """
    Describes one link between a ticket and a group.
    """
    __mapper_args__ = {
        'polymorphic_identity': TicketSubscriptionType.group
    }

    def get_addresses(self):
        if not self.group:
            raise StopIteration
        for user in self.group.users:
            for addr in user.email_addresses:
                yield addr.address

    @property
    def template_vars(self):
        if self.group:
            return {'recipient_type': 'group',
                    'group': self.group}
        return {}


class EntityTicketSubscription(TicketSubscription):
    """
    Describes one link between a ticket and an entity.
    """
    __mapper_args__ = {
        'polymorphic_identity': TicketSubscriptionType.entity
    }

    def get_addresses(self):
        if not self.entity:
            raise StopIteration
        if isinstance(self.entity, PhysicalEntity):
            if self.entity.email:
                yield self.entity.email
        elif isinstance(self.entity, LegalEntity):
            if self.entity.contact_email:
                yield self.entity.contact_email
        raise StopIteration

    @property
    def template_vars(self):
        if self.entity:
            return {'recipient_type': 'entity',
                    'entity': self.entity}
        return {}


class AddressTicketSubscription(TicketSubscription):
    """
    Describes one link between a ticket and an external address.
    """
    __mapper_args__ = {
        'polymorphic_identity': TicketSubscriptionType.address
    }

    def get_addresses(self):
        if self.address:
            yield self.address

    @property
    def template_vars(self):
        if self.address:
            return {'recipient_type': 'address',
                    'address': self.address}
        return {}


class TicketStateSubscription(Base):
    """
    Automatic ticket subscriptions based on initial state.
    """
    __tablename__ = 'tickets_states_subscriptions'
    __table_args__ = (
        Comment('Ticket state subscriptions'),
        Index('tickets_states_subscriptions_i_tstid', 'tstid'),
        Index('tickets_states_subscriptions_i_uid', 'uid'),
        Index('tickets_states_subscriptions_i_gid', 'gid'),
        Index('tickets_states_subscriptions_i_entityid', 'entityid'),
        Index('tickets_states_subscriptions_u_sub',
              'tstid', 'uid', 'gid', 'entityid', 'addr',
              unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TICKETS',
                'cap_read':      'TICKETS_SUBSCRIPTIONS_LIST',
                'cap_create':    'TICKETS_SUBSCRIPTIONS_CREATE',
                'cap_edit':      'TICKETS_SUBSCRIPTIONS_EDIT',
                'cap_delete':    'TICKETS_SUBSCRIPTIONS_DELETE',

                'menu_name':     _('State Subscriptions'),
                'grid_view':     ('tstsubid', 'type', 'state',
                                  'user', 'group', 'entity', 'address'),
                'grid_hidden':   ('tstsubid',),
                'form_view':     ('type', 'state',
                                  'user', 'group', 'entity', 'address'),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),

                'create_wizard': SimpleWizard(
                                    title=_('Add new state subscription'))
            }
        })
    id = Column(
        'tstsubid',
        UInt32(),
        Sequence('tickets_states_subscriptions_tstsubid_seq'),
        Comment('Ticket state subscription ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    type = Column(
        TicketSubscriptionType.db_type(),
        Comment('Ticket state subscription type'),
        nullable=False,
        default=TicketSubscriptionType.user,
        server_default=TicketSubscriptionType.user,
        info={
            'header_string': _('Type'),
            'column_flex': 2
        })
    state_id = Column(
        'tstid',
        UInt32(),
        ForeignKey('tickets_states_types.tstid',
                   name='tickets_states_subscriptions_fk_tstid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Ticket state ID'),
        nullable=False,
        info={
            'header_string': _('State'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    user_id = Column(
        'uid',
        UInt32(),
        ForeignKey('users.uid', name='tickets_states_subscriptions_fk_uid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('User ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('User'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    group_id = Column(
        'gid',
        UInt32(),
        ForeignKey('groups.gid', name='tickets_states_subscriptions_fk_gid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Group ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Group'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    entity_id = Column(
        'entityid',
        UInt32(),
        ForeignKey('entities_def.entityid',
                   name='tickets_states_subscriptions_fk_entityid',
                   ondelete='CASCADE', onupdate='CASCADE'),
        Comment('Entity ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Entity'),
            'filter_type': 'none',
            'column_flex': 1
        })
    address = Column(
        'addr',
        Unicode(255),
        Comment('E-mail address'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Address'),
            'vtype': 'email',
            'column_flex': 3
        })
    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'X',
        'with_polymorphic': '*'
    }

    user = relationship(
        'User',
        backref=backref('ticket_state_subscriptions',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    group = relationship(
        'Group',
        backref=backref('ticket_state_subscriptions',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    entity = relationship(
        'Entity',
        backref=backref('ticket_state_subscriptions',
                        cascade='all, delete-orphan',
                        passive_deletes=True))

    def get_addresses(self):
        raise NotImplementedError

    @property
    def template_vars(self):
        return {}


class UserTicketStateSubscription(TicketStateSubscription):
    """
    Describes one link between a ticket state and a user.
    """
    __mapper_args__ = {
        'polymorphic_identity': TicketSubscriptionType.user
    }

    def get_addresses(self):
        if not self.user:
            raise StopIteration
        for addr in self.user.email_addresses:
            yield addr.address

    @property
    def template_vars(self):
        if self.user:
            return {'recipient_type': 'user',
                    'user': self.user}
        return {}


class GroupTicketStateSubscription(TicketStateSubscription):
    """
    Describes one link between a ticket state and a group.
    """
    __mapper_args__ = {
        'polymorphic_identity': TicketSubscriptionType.group
    }

    def get_addresses(self):
        if not self.group:
            raise StopIteration
        for user in self.group.users:
            for addr in user.email_addresses:
                yield addr.address

    @property
    def template_vars(self):
        if self.group:
            return {'recipient_type': 'group',
                    'group': self.group}
        return {}


class EntityTicketStateSubscription(TicketStateSubscription):
    """
    Describes one link between a ticket state and an entity.
    """
    __mapper_args__ = {
        'polymorphic_identity': TicketSubscriptionType.entity
    }

    def get_addresses(self):
        if not self.entity:
            raise StopIteration
        if isinstance(self.entity, PhysicalEntity):
            if self.entity.email:
                yield self.entity.email
        elif isinstance(self.entity, LegalEntity):
            if self.entity.contact_email:
                yield self.entity.contact_email
        raise StopIteration

    @property
    def template_vars(self):
        if self.entity:
            return {'recipient_type': 'entity',
                    'entity': self.entity}
        return {}


class AddressTicketStateSubscription(TicketStateSubscription):
    """
    Describes one link between a ticket state and an external address.
    """
    __mapper_args__ = {
        'polymorphic_identity': TicketSubscriptionType.address
    }

    def get_addresses(self):
        if self.address:
            yield self.address

    @property
    def template_vars(self):
        if self.address:
            return {'recipient_type': 'address',
                    'address': self.address}
        return {}
