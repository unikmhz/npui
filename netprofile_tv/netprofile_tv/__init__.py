#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: TV subscription module
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

from sqlalchemy.orm.exc import NoResultFound
from pyramid.i18n import TranslationStringFactory

from netprofile.common.modules import ModuleBase

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

_ = TranslationStringFactory('netprofile_tv')


class Module(ModuleBase):
    def __init__(self, mmgr):
        self.mmgr = mmgr
        mmgr.cfg.add_translation_dirs('netprofile_tv:locale/')

    @classmethod
    def get_deps(cls):
        return ('paidservices', 'hosts')

    @classmethod
    def get_models(cls):
        from netprofile_tv import models
        return (models.TVSource,
                models.TVChannel,
                models.TVSubscriptionType,
                models.TVSubscriptionChannel,
                models.TVSubscription,
                models.TVAccessCard)

    @classmethod
    def get_sql_data(cls, modobj, vpair, sess):
        from netprofile_core.models import (
            Group,
            GroupCapability,
            Privilege
        )

        if not vpair.is_install:
            return

        privs = (Privilege(code='BASE_TV_SOURCES',
                           name=_('Menu: TV sources')),
                 Privilege(code='TV_SOURCES_LIST',
                           name=_('TV sources: List')),
                 Privilege(code='TV_SOURCES_CREATE',
                           name=_('TV sources: Create')),
                 Privilege(code='TV_SOURCES_EDIT',
                           name=_('TV sources: Edit')),
                 Privilege(code='TV_SOURCES_DELETE',
                           name=_('TV sources: Delete')),
                 Privilege(code='BASE_TV_PKG',
                           name=_('Menu: TV subscriptions')),
                 Privilege(code='TV_PKG_LIST',
                           name=_('TV subscriptions: List')),
                 Privilege(code='TV_PKG_CREATE',
                           name=_('TV subscriptions: Create')),
                 Privilege(code='TV_PKG_EDIT',
                           name=_('TV subscriptions: Edit')),
                 Privilege(code='TV_PKG_DELETE',
                           name=_('TV subscriptions: Delete')),
                 Privilege(code='TV_PKG_ASSIGN',
                           name=_('TV subscriptions: Assign')),
                 Privilege(code='BASE_TV_CARDS',
                           name=_('Menu: TV cards')),
                 Privilege(code='TV_CARDS_LIST',
                           name=_('TV cards: List')),
                 Privilege(code='TV_CARDS_CREATE',
                           name=_('TV cards: Create')),
                 Privilege(code='TV_CARDS_EDIT',
                           name=_('TV cards: Edit')),
                 Privilege(code='TV_CARDS_DELETE',
                           name=_('TV cards: Delete')))
        for priv in privs:
            priv.module = modobj
            sess.add(priv)
        try:
            grp_admins = sess.query(Group).filter(
                    Group.name == 'Administrators').one()
            for priv in privs:
                cap = GroupCapability()
                cap.group = grp_admins
                cap.privilege = priv
        except NoResultFound:
            pass

    def get_css(self, request):
        return ('netprofile_tv:static/css/main.css',)

    @property
    def name(self):
        return _('TV Service')
