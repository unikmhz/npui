#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: TV subscription module - Models
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
    'TVSource',
    'TVChannel',
    'TVSubscriptionType',
    'TVSubscriptionChannel',
    'TVSubscription',
    'TVAccessCard'
]

import pkg_resources
from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Sequence,
    Unicode,
    UnicodeText,
    event,
    text
)
from sqlalchemy.orm import (
    backref,
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
    NPBoolean,
    UInt16,
    UInt32,
    npbool
)
from netprofile.db.ddl import (
    Comment,
    Trigger
)
from netprofile.ext.wizards import SimpleWizard
from netprofile_entities.models import Entity
from netprofile_access.models import AccessEntity

_ = TranslationStringFactory('netprofile_tv')


def _tv_handler_choices(col, req):
    ret = {}
    for itp in pkg_resources.iter_entry_points('netprofile.tv.handlers'):
        ret[itp.name] = itp.name
    return ret


class TVSource(Base):
    """
    TV broadcasting sources.
    """
    __tablename__ = 'tv_sources_def'
    __table_args__ = (
        Comment('Defined TV broadcast sources'),
        Index('tv_sources_def_i_hostid', 'hostid'),
        Index('tv_sources_def_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TV_SOURCES',
                'cap_read':      'TV_SOURCES_LIST',
                'cap_create':    'TV_SOURCES_CREATE',
                'cap_edit':      'TV_SOURCES_EDIT',
                'cap_delete':    'TV_SOURCES_DELETE',

                'menu_name':     _('Sources'),
                'show_in_menu':  'admin',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('tvsourceid', 'name',
                                  'gateway_host', 'port'),
                'grid_hidden':   ('tvsourceid',
                                  'gateway_host', 'port'),
                'form_view':     ('name',
                                  'gateway_host', 'port',
                                  'handler', 'enc',
                                  'realtime', 'polled',
                                  'authuser', 'authpass',
                                  'descr'),
                'easy_search':   ('name',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new source'))
            }
        })
    id = Column(
        'tvsourceid',
        UInt32(),
        Sequence('tv_sources_def_tvsourceid_seq'),
        Comment('TV source ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    gateway_host_id = Column(
        'hostid',
        UInt32(),
        ForeignKey('hosts_def.hostid', name='tv_sources_def_fk_hostid',
                   onupdate='CASCADE', ondelete='SET NULL'),
        Comment('Gateway host ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Gateway'),
            'filter_type': 'none',
            'column_flex': 2
        })
    gateway_port = Column(
        'port',
        UInt16(),
        Comment('Gateway port number'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Port')
        })
    name = Column(
        Unicode(255),
        Comment('TV source name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 3
        })
    text_encoding = Column(
        'enc',
        ASCIIString(32),
        Comment('Used text encoding'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Encoding')
        })
    handler = Column(
        ASCIIString(255),
        Comment('Gateway handler class'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Handler'),
            'choices': _tv_handler_choices,
            'editor_config': {
                'editable': False,
                'forceSelection': True
            }
        })
    realtime = Column(
        NPBoolean(),
        Comment('Update gateway in real time'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string': _('Real time')
        })
    polled = Column(
        NPBoolean(),
        Comment('Update gateway in bulk'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string': _('Polled')
        })
    auth_username = Column(
        'authuser',
        ASCIIString(255),
        Comment('Gateway username'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Username')
        })
    auth_passphrase = Column(
        'authpass',
        ASCIIString(255),
        Comment('Gateway passphrase'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Passphrase'),
            'secret_value': True,
            'editor_xtype': 'passwordfield'
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    gateway_host = relationship(
        'Host',
        backref=backref('tv_sources', passive_deletes=True))
    channels = relationship(
        'TVChannel',
        backref=backref('source', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)
    cards = relationship(
        'TVAccessCard',
        backref=backref('source', innerjoin=True),
        passive_deletes=True)

    def __str__(self):
        return str(self.name)

    def get_handler(self):
        hdlname = self.handler
        if not hdlname:
            return None
        itp = list(pkg_resources.iter_entry_points(
                'netprofile.tv.handlers', hdlname))
        if len(itp) == 0:
            return None
        cls = itp[0].load()
        return cls(self)


class TVChannel(Base):
    """
    Individual TV channels.
    """
    __tablename__ = 'tv_channels'
    __table_args__ = (
        Comment('TV channels'),
        Index('tv_channels_u_channel', 'tvsourceid', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TV_SOURCES',
                'cap_read':      'TV_SOURCES_LIST',
                'cap_create':    'TV_SOURCES_EDIT',
                'cap_edit':      'TV_SOURCES_EDIT',
                'cap_delete':    'TV_SOURCES_EDIT',

                'menu_name':     _('Channels'),
                'show_in_menu':  'admin',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('tvchanid', 'name', 'source', 'extid'),
                'grid_hidden':   ('tvchanid', 'extid'),
                'form_view':     ('name', 'source', 'extid', 'descr'),
                'easy_search':   ('name', 'extid'),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new channel'))
            }
        })
    id = Column(
        'tvchanid',
        UInt32(),
        Sequence('tv_channels_tvchanid_seq'),
        Comment('TV channel ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    source_id = Column(
        'tvsourceid',
        UInt32(),
        ForeignKey('tv_sources_def.tvsourceid',
                   name='tv_channels_fk_tvsourceid',
                   onupdate='CASCADE', ondelete='CASCADE'),
        Comment('TV source ID'),
        nullable=False,
        info={
            'header_string': _('Source'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    external_id = Column(
        'extid',
        ASCIIString(255),
        Comment('TV channel external ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('External ID')
        })
    name = Column(
        Unicode(255),
        Comment('TV channel name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 3
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    subscription_type_map = relationship(
        'TVSubscriptionChannel',
        backref=backref('channel', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)

    subscription_types = association_proxy(
        'subscription_type_map',
        'type',
        creator=lambda v: TVSubscriptionChannel(type=v))

    def __str__(self):
        return str(self.name)


class TVSubscriptionType(Base):
    """
    TV channel packages.
    """
    __tablename__ = 'tv_subscriptions_types'
    __table_args__ = (
        Comment('TV subscription types'),
        Index('tv_subscriptions_types_i_paidid', 'paidid'),
        Index('tv_subscriptions_types_u_name', 'name', unique=True),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TV_PKG',
                'cap_read':      'TV_PKG_LIST',
                'cap_create':    'TV_PKG_CREATE',
                'cap_edit':      'TV_PKG_EDIT',
                'cap_delete':    'TV_PKG_DELETE',

                'menu_name':     _('Subscription Types'),
                'show_in_menu':  'admin',
                'default_sort':  ({'property': 'name', 'direction': 'ASC'},),
                'grid_view':     ('tvsubtid', 'name',
                                  'paid_service_type', 'extid',
                                  'enabled'),
                'grid_hidden':   ('tvsubtid', 'extid'),
                'form_view':     ('name', 'paid_service_type', 'extid',
                                  'enabled', 'descr'),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'easy_search':   ('name', 'extid'),
                'create_wizard': SimpleWizard(
                                    title=_('Add new subscription type'))
            }
        })
    id = Column(
        'tvsubtid',
        UInt32(),
        Sequence('tv_subscriptions_types_tvsubtid_seq'),
        Comment('TV subscription type ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    paid_service_type_id = Column(
        'paidid',
        UInt32(),
        ForeignKey('paid_types.paidid',
                   name='tv_subscriptions_types_fk_paidid',
                   onupdate='CASCADE', ondelete='SET NULL'),
        Comment('Paid service type ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Paid Service'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    external_id = Column(
        'extid',
        ASCIIString(255),
        Comment('TV subscription external ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('External ID')
        })
    name = Column(
        Unicode(255),
        Comment('TV subscription type name'),
        nullable=False,
        info={
            'header_string': _('Name'),
            'column_flex': 3
        })
    enabled = Column(
        NPBoolean(),
        Comment('Is subscription type enabled'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string': _('Enabled')
        })
    description = Column(
        'descr',
        UnicodeText(),
        Comment('Description'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Description')
        })

    paid_service_type = relationship(
        'PaidServiceType',
        backref=backref('tv_subscription_types', passive_deletes=True))
    channel_map = relationship(
        'TVSubscriptionChannel',
        backref=backref('type', innerjoin=True),
        cascade='all, delete-orphan',
        passive_deletes=True)
    subscriptions = relationship(
        'TVSubscription',
        backref=backref('type', innerjoin=True),
        passive_deletes=True)

    channels = association_proxy(
        'channel_map',
        'channel',
        creator=lambda v: TVSubscriptionChannel(channel=v))

    def __str__(self):
        return str(self.name)


class TVSubscriptionChannel(Base):
    """
    Link between a channel and a subscription package.
    """
    __tablename__ = 'tv_subscriptions_channels'
    __table_args__ = (
        Comment('Subscription memberships for TV channels'),
        Index('tv_subscriptions_channels_u_link',
              'tvsubtid', 'tvchanid',
              unique=True),
        Index('tv_subscriptions_channels_i_tvchanid', 'tvchanid'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TV_PKG',
                'cap_read':      'TV_PKG_EDIT',
                'cap_create':    'TV_PKG_EDIT',
                'cap_edit':      'TV_PKG_EDIT',
                'cap_delete':    'TV_PKG_EDIT',

                'default_sort':  ({'property': 'tvsubtid',
                                   'direction': 'ASC'},
                                  {'property': 'tvchanid',
                                   'direction': 'ASC'}),
                'grid_view':     ('tvsubchanid', 'type', 'channel'),
                'grid_hidden':   ('tvsubchanid',),
                'create_wizard': SimpleWizard(title=_('Add new channel'))
            }
        })
    id = Column(
        'tvsubchanid',
        UInt32(),
        Sequence('tv_subscriptions_channels_tvsubchanid_seq'),
        Comment('TV subscription channel ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    type_id = Column(
        'tvsubtid',
        UInt32(),
        ForeignKey('tv_subscriptions_types.tvsubtid',
                   name='tv_subscriptions_channels_fk_tvsubtid',
                   onupdate='CASCADE', ondelete='CASCADE'),
        Comment('TV subscription type ID'),
        nullable=False,
        info={
            'header_string': _('Type'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    channel_id = Column(
        'tvchanid',
        UInt32(),
        ForeignKey('tv_channels.tvchanid',
                   name='tv_subscriptions_channels_fk_tvchanid',
                   onupdate='CASCADE', ondelete='CASCADE'),
        Comment('TV channel ID'),
        nullable=False,
        info={
            'header_string': _('Channel'),
            'filter_type': 'nplist',
            'column_flex': 1
        })


class TVAccessCard(Base):
    """
    Numbered CA cards, or other methods to differentiate customers.
    """
    __tablename__ = 'tv_cards_def'
    __table_args__ = (
        Comment('TV access cards'),
        Index('tv_cards_def_i_aeid', 'aeid'),
        Index('tv_cards_def_u_card', 'tvsourceid', 'extid', unique=True),
        Index('tv_cards_def_i_enabled', 'enabled'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TV_CARDS',
                'cap_read':      'TV_CARDS_LIST',
                'cap_create':    'TV_CARDS_CREATE',
                'cap_edit':      'TV_CARDS_EDIT',
                'cap_delete':    'TV_CARDS_DELETE',

                'menu_name':     _('TV Cards'),
                'show_in_menu':  'modules',
                'default_sort':  ({'property': 'extid', 'direction': 'ASC'},),
                'grid_view':     ('tvcardid', 'source',
                                  'access_entity', 'extid', 'enabled'),
                'grid_hidden':   ('tvcardid',),
                'form_view':     ('source', 'access_entity', 'extid',
                                  'enabled'),
                'easy_search':   ('extid',),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new card'))
            }
        })
    id = Column(
        'tvcardid',
        UInt32(),
        Sequence('tv_cards_def_tvcardid_seq'),
        Comment('TV card ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    access_entity_id = Column(
        'aeid',
        UInt32(),
        ForeignKey('entities_access.entityid', name='tv_cards_def_fk_aeid',
                   onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Access entity ID'),
        nullable=False,
        info={
            'header_string': _('Access Entity'),
            'filter_type': 'none',
            'column_flex': 2
        })
    source_id = Column(
        'tvsourceid',
        UInt32(),
        ForeignKey('tv_sources_def.tvsourceid',
                   name='tv_cards_def_fk_tvsourceid',
                   onupdate='CASCADE'),  # ondelete='RESTRICT'
        Comment('TV source ID'),
        nullable=False,
        info={
            'header_string': _('Source'),
            'filter_type': 'nplist',
            'column_flex': 2
        })
    external_id = Column(
        'extid',
        ASCIIString(255),
        Comment('TV card external ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('External ID'),
            'column_flex': 1
        })
    enabled = Column(
        NPBoolean(),
        Comment('Is card enabled'),
        nullable=False,
        default=True,
        server_default=npbool(True),
        info={
            'header_string': _('Enabled')
        })

    access_entity = relationship(
        'AccessEntity',
        innerjoin=True,
        backref=backref('tv_cards',
                        cascade='all, delete-orphan',
                        passive_deletes=True))

    def __str__(self):
        return str(self.external_id)


class TVSubscription(Base):
    """
    Channel package subscriptions.
    """
    __tablename__ = 'tv_subscriptions_def'
    __table_args__ = (
        Comment('TV subscriptions'),
        Index('tv_subscriptions_def_i_tvsubtid', 'tvsubtid'),
        Index('tv_subscriptions_def_i_entityid', 'entityid'),
        Index('tv_subscriptions_def_u_epid', 'epid', unique=True),
        Trigger('before', 'insert', 't_tv_subscriptions_def_bi'),
        Trigger('before', 'update', 't_tv_subscriptions_def_bu'),
        Trigger('after', 'insert', 't_tv_subscriptions_def_ai'),
        Trigger('after', 'update', 't_tv_subscriptions_def_au'),
        Trigger('after', 'delete', 't_tv_subscriptions_def_ad'),
        {
            'mysql_engine':  'InnoDB',
            'mysql_charset': 'utf8',
            'info':          {
                'cap_menu':      'BASE_TV_PKG',
                'cap_read':      'TV_PKG_LIST',
                'cap_create':    'TV_PKG_ASSIGN',
                'cap_edit':      'TV_PKG_ASSIGN',
                'cap_delete':    'TV_PKG_ASSIGN',

                'menu_main':     True,
                'menu_name':     _('TV Subscriptions'),
                'show_in_menu':  'modules',
                'default_sort':  ({'property': 'tvsubtid',
                                   'direction': 'ASC'},),
                'grid_view':     ('tvsubid', 'type',
                                  'entity', 'access_entity',
                                  'paid_service'),
                'grid_hidden':   ('tvsubid', 'entity',
                                  'paid_service'),
                'form_view':     ('type', 'access_entity', 'type',
                                  'paid_service'),
                'detail_pane':   ('netprofile_core.views', 'dpane_simple'),
                'create_wizard': SimpleWizard(title=_('Add new subscriptions'))
            }
        })
    id = Column(
        'tvsubid',
        UInt32(),
        Sequence('tv_subscriptions_def_tvsubid_seq'),
        Comment('TV subscription ID'),
        primary_key=True,
        nullable=False,
        info={
            'header_string': _('ID')
        })
    type_id = Column(
        'tvsubtid',
        UInt32(),
        ForeignKey('tv_subscriptions_types.tvsubtid',
                   name='tv_subscriptions_def_fk_tvsubtid',
                   onupdate='CASCADE'),  # ondelete='RESTRICT'
        Comment('TV subscription type ID'),
        nullable=False,
        info={
            'header_string': _('Type'),
            'filter_type': 'nplist',
            'column_flex': 1
        })
    entity_id = Column(
        'entityid',
        UInt32(),
        ForeignKey('entities_def.entityid',
                   name='tv_subscriptions_def_fk_entityid',
                   onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Entity ID'),
        nullable=False,
        info={
            'header_string': _('Entity'),
            'filter_type': 'none',
            'column_flex': 2
        })
    access_entity_id = Column(
        'aeid',
        UInt32(),
        ForeignKey('entities_access.entityid',
                   name='tv_subscriptions_def_fk_aeid',
                   onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Access entity ID'),
        nullable=False,
        info={
            'header_string': _('Access Entity'),
            'filter_type': 'none',
            'column_flex': 2
        })
    paid_service_id = Column(
        'epid',
        UInt32(),
        ForeignKey('paid_def.epid', name='tv_subscriptions_def_fk_epid',
                   onupdate='CASCADE', ondelete='CASCADE'),
        Comment('Paid service mapping ID'),
        nullable=True,
        default=None,
        server_default=text('NULL'),
        info={
            'header_string': _('Paid Service'),
            'filter_type': 'none',
            'read_only': True,
            'column_flex': 2
        })

    entity = relationship(
        'Entity',
        foreign_keys=entity_id,
        innerjoin=True,
        backref=backref('tv_subscriptions',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    access_entity = relationship(
        'AccessEntity',
        foreign_keys=access_entity_id,
        innerjoin=True,
        backref=backref('tv_subscriptions_access',
                        cascade='all, delete-orphan',
                        passive_deletes=True))
    paid_service = relationship(
        'PaidService',
        backref=backref('tv_subscription',
                        uselist=False,
                        cascade='all, delete-orphan',
                        passive_deletes=True))

    @validates('access_entity', 'access_entity_id')
    def _autoset_entity(self, k, v):
        if k == 'access_entity':
            ent = v
        else:
            sess = DBSession()
            ent = sess.query(AccessEntity).get(int(v))
            self.access_entity = ent

        while isinstance(ent, AccessEntity):
            ent = ent.parent
        if isinstance(ent, Entity):
            self.entity = ent
        return v

    @property
    def active(self):
        if not self.type.enabled:
            return False
        if self.paid_service is None:
            return True
        return self.paid_service.is_paid

    def __str__(self):
        return '%s: %s' % (str(self.type),
                           str(self.access_entity))


@event.listens_for(TVSubscription, 'after_insert')
@event.listens_for(TVSubscription, 'after_update')
@event.listens_for(TVSubscription, 'after_delete')
def _tvsub_modified(mapper, conn, tgt):
    from .tasks import update_aent
    if not tgt.access_entity_id:
        return
    # Wait a reasonable amount of time to allow transaction to complete.
    # TODO: make countdown configurable
    update_aent.apply_async(args=(tgt.access_entity_id,),
                            countdown=8)
