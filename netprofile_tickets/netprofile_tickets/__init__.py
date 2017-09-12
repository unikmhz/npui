#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Tickets module
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

from sqlalchemy.orm.exc import NoResultFound
from pyramid.i18n import TranslationStringFactory

from netprofile.common.modules import ModuleBase
from netprofile.common.settings import (
    Setting,
    SettingSection
)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

_ = TranslationStringFactory('netprofile_tickets')


class Module(ModuleBase):
    def __init__(self, mmgr):
        self.mmgr = mmgr
        mmgr.cfg.add_route(
            'tickets.cl.issues',
            '/issues/*traverse',
            factory='netprofile_tickets.views.ClientRootFactory',
            vhost='client')
        mmgr.cfg.add_translation_dirs('netprofile_tickets:locale/')

    @classmethod
    def get_deps(cls):
        return ('entities',)

    @classmethod
    def get_models(cls):
        from netprofile_tickets import models
        return (models.Ticket,
                models.TicketChange,
                models.TicketChangeBit,
                models.TicketChangeField,
                models.TicketChangeFlagMod,
                models.TicketDependency,
                models.TicketFile,
                models.TicketFlag,
                models.TicketFlagType,
                models.TicketOrigin,
                models.TicketState,
                models.TicketStateTransition,
                models.TicketTemplate,
                models.TicketScheduler,
                models.TicketSchedulerUserAssignment,
                models.TicketSchedulerGroupAssignment,
                models.TicketSubscription)

    @classmethod
    def get_sql_data(cls, modobj, vpair, sess):
        from netprofile_tickets.models import (
            TicketChangeField,
            TicketOrigin
        )
        from netprofile_core.models import (
            Group,
            GroupCapability,
            LogType,
            Privilege
        )

        if not vpair.is_install:
            return

        sess.add(LogType(id=3,
                 name='Tickets'))

        privs = (Privilege(code='BASE_TICKETS',
                           name=_('Menu: Tickets')),
                 Privilege(code='ADMIN_TICKETS',
                           name=_('Administrative: Tickets')),
                 Privilege(code='TICKETS_LIST',
                           name=_('Tickets: List')),
                 Privilege(code='TICKETS_LIST_ARCHIVED',
                           name=_('Tickets: List archived')),
                 Privilege(code='TICKETS_CREATE',
                           name=_('Tickets: Create')),
                 Privilege(code='TICKETS_UPDATE',
                           name=_('Tickets: Update')),
                 Privilege(code='TICKETS_COMMENT',
                           name=_('Tickets: Comment')),
                 Privilege(code='TICKETS_ARCHIVAL',
                           name=_('Tickets: Archival')),
                 Privilege(code='TICKETS_DIRECT',
                           name=_('Tickets: Direct access'),
                           can_be_set=False),
                 Privilege(code='TICKETS_OWN_LIST',
                           name=_('Tickets: List assigned to user')),
                 Privilege(code='TICKETS_OWNGROUP_LIST',
                           name=_('Tickets: List assigned to group')),
                 Privilege(code='TICKETS_CHANGE_DATE',
                           name=_('Tickets: Change date')),
                 Privilege(code='TICKETS_CHANGE_UID',
                           name=_('Tickets: Change assigned user')),
                 Privilege(code='TICKETS_CHANGE_GID',
                           name=_('Tickets: Change assigned group')),
                 Privilege(code='TICKETS_CHANGE_STATE',
                           name=_('Tickets: Change state')),
                 Privilege(code='TICKETS_CHANGE_FLAGS',
                           name=_('Tickets: Change flags')),
                 Privilege(code='TICKETS_CHANGE_ENTITY',
                           name=_('Tickets: Change entity')),
                 Privilege(code='TICKETS_DEPENDENCIES',
                           name=_('Tickets: Edit dependencies')),
                 Privilege(code='FILES_ATTACH_2TICKETS',
                           name=_('Files: Attach to tickets')),
                 Privilege(code='TICKETS_STATES_CREATE',
                           name=_('Tickets: Create states')),
                 Privilege(code='TICKETS_STATES_EDIT',
                           name=_('Tickets: Edit states')),
                 Privilege(code='TICKETS_STATES_DELETE',
                           name=_('Tickets: Delete states')),
                 Privilege(code='TICKETS_FLAGTYPES_CREATE',
                           name=_('Tickets: Create flag types')),
                 Privilege(code='TICKETS_FLAGTYPES_EDIT',
                           name=_('Tickets: Edit flag types')),
                 Privilege(code='TICKETS_FLAGTYPES_DELETE',
                           name=_('Tickets: Delete flag types')),
                 Privilege(code='TICKETS_ORIGINS_CREATE',
                           name=_('Tickets: Create origins')),
                 Privilege(code='TICKETS_ORIGINS_EDIT',
                           name=_('Tickets: Edit origins')),
                 Privilege(code='TICKETS_ORIGINS_DELETE',
                           name=_('Tickets: Delete origins')),
                 Privilege(code='TICKETS_TRANSITIONS_CREATE',
                           name=_('Tickets: Create transitions')),
                 Privilege(code='TICKETS_TRANSITIONS_EDIT',
                           name=_('Tickets: Edit transitions')),
                 Privilege(code='TICKETS_TRANSITIONS_DELETE',
                           name=_('Tickets: Delete transitions')),
                 Privilege(code='TICKETS_TEMPLATES_CREATE',
                           name=_('Tickets: Create templates')),
                 Privilege(code='TICKETS_TEMPLATES_EDIT',
                           name=_('Tickets: Edit templates')),
                 Privilege(code='TICKETS_TEMPLATES_DELETE',
                           name=_('Tickets: Delete templates')),
                 Privilege(code='TICKETS_SCHEDULES_CREATE',
                           name=_('Tickets: Create schedules')),
                 Privilege(code='TICKETS_SCHEDULES_EDIT',
                           name=_('Tickets: Edit schedules')),
                 Privilege(code='TICKETS_SCHEDULES_DELETE',
                           name=_('Tickets: Delete schedules')),
                 Privilege(code='TICKETS_SUBSCRIPTIONS_LIST',
                           name=_('Tickets: List subscriptions')),
                 Privilege(code='TICKETS_SUBSCRIPTIONS_CREATE',
                           name=_('Tickets: Create subscriptions')),
                 Privilege(code='TICKETS_SUBSCRIPTIONS_EDIT',
                           name=_('Tickets: Edit subscriptions')),
                 Privilege(code='TICKETS_SUBSCRIPTIONS_DELETE',
                           name=_('Tickets: Delete subscriptions')))
        for priv in privs:
            priv.module = modobj
            sess.add(priv)
        try:
            grp_admins = sess.query(Group).filter(
                    Group.name == 'Administrators').one()
            for priv in privs:
                if priv.code in {'TICKETS_OWN_LIST',
                                 'TICKETS_OWNGROUP_LIST',
                                 'TICKETS_DIRECT'}:
                    continue
                cap = GroupCapability()
                cap.group = grp_admins
                cap.privilege = priv
        except NoResultFound:
            pass

        origins = (
            TicketOrigin(
                id=1,
                name=_('Operator'),
                description=_('Added manually via an administrative UI.')),
            TicketOrigin(
                id=2,
                name=_('Via site'),
                description=_('Added via client portal.')),
            TicketOrigin(
                id=3,
                name=_('Via e-mail'),
                description=_('Added via incoming e-mail message.')),
            TicketOrigin(
                id=4,
                name=_('Via voicemail'),
                description=_('Added via incoming voicemail message.')))

        for obj in origins:
            sess.add(obj)

        chfields = (TicketChangeField(id=1, name=_('User')),
                    TicketChangeField(id=2, name=_('Group')),
                    TicketChangeField(id=3, name=_('Time')),
                    TicketChangeField(id=4, name=_('Archived')),
                    TicketChangeField(id=5, name=_('Entity')))

        for obj in chfields:
            sess.add(obj)

    def get_css(self, request):
        return ('netprofile_tickets:static/css/main.css',)

    def get_local_js(self, request, lang):
        return ('netprofile_tickets:static/webshell/locale/webshell-lang-'
                + lang + '.js',)

    def get_autoload_js(self, request):
        return ('NetProfile.form.field.WeekDayField',)

    def get_controllers(self, request):
        return ('NetProfile.tickets.controller.TicketGrid',)

    def get_settings(self, vhost='MAIN', scope='global'):
        if vhost == 'MAIN' and scope == 'global':
            return (
                SettingSection(
                    'sub',
                    Setting('default_uid',
                            title=_('Subscribe to user by default'),
                            help_text=_('Subscribe this user to '
                                        'all new tickets'),
                            type='int',
                            nullable=True,
                            write_cap='ADMIN_TICKETS'),
                    Setting('default_gid',
                            title=_('Subscribe to group by default'),
                            help_text=_('Subscribe this group to '
                                        'all new tickets'),
                            type='int',
                            nullable=True,
                            write_cap='ADMIN_TICKETS'),
                    title=_('Subscriptions'),
                    help_text=_('Default subscriptions for tickets'),
                    read_cap='ADMIN_TICKETS'),)
        if vhost == 'MAIN' and scope == 'user':
            return ()
        return ()

    @property
    def name(self):
        return _('Tickets')
