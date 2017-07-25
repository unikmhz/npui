#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: XOP module
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

from sqlalchemy.orm.exc import NoResultFound
from pyramid.i18n import TranslationStringFactory

from netprofile.common.modules import (
    IModuleManager,
    ModuleBase
)

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

_ = TranslationStringFactory('netprofile_xop')


class Module(ModuleBase):
    def __init__(self, mmgr):
        self.mmgr = mmgr
        mmgr.cfg.add_translation_dirs('netprofile_xop:locale/')
        mmgr.cfg.add_route('xop.cl.home',
                           '/*traverse',
                           factory='netprofile_xop.views.ClientRootFactory',
                           vhost='xop')

    @classmethod
    def get_deps(cls):
        return ('stashes',)

    @classmethod
    def get_models(cls):
        from netprofile_xop import models
        return (models.ExternalOperation,
                models.ExternalOperationProvider)

    @classmethod
    def get_sql_data(cls, modobj, vpair, sess):
        from netprofile_core.models import (
            Group,
            GroupCapability,
            Privilege
        )

        if not vpair.is_install:
            return

        privs = (Privilege(code='BASE_XOP',
                           name=_('Menu: External operations')),)
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
        return ('netprofile_xop:static/css/main.css',)

    @property
    def name(self):
        return _('External Operations')


def includeme(config):
    mmgr = config.registry.getUtility(IModuleManager)
    mmgr.load('core')
    for mod in ('stashes', 'entities', 'access', 'rates', 'networks',
                'hosts', 'ipaddresses'):
        mmgr.load(mod)
