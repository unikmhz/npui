#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Config Generation module
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

import base64
from sqlalchemy.orm.exc import NoResultFound
from pyramid.i18n import TranslationStringFactory

from netprofile.common.modules import ModuleBase
from netprofile.common.crypto import get_salt_bytes

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

_ = TranslationStringFactory('netprofile_confgen')


def _gen_tsig(length):
    return base64.b64encode(get_salt_bytes(length, None)).decode('ascii')


class Module(ModuleBase):
    def __init__(self, mmgr):
        self.mmgr = mmgr
        mmgr.cfg.add_translation_dirs('netprofile_confgen:locale/')

    @classmethod
    def get_deps(cls):
        return ('hosts',)

    @classmethod
    def get_models(cls):
        from netprofile_confgen import models
        return (models.Server,
                models.ServerParameter,
                models.ServerType)

    @classmethod
    def get_sql_data(cls, modobj, vpair, sess):
        from netprofile_confgen.models import ServerType
        from netprofile_core.models import (
            Group,
            GroupCapability,
            Privilege
        )

        if not vpair.is_install:
            return

        privs = (Privilege(code='SRV_LIST',
                           name=_('Servers: List')),
                 Privilege(code='SRV_CREATE',
                           name=_('Servers: Create')),
                 Privilege(code='SRV_EDIT',
                           name=_('Servers: Edit')),
                 Privilege(code='SRV_DELETE',
                           name=_('Servers: Delete')),
                 Privilege(code='SRV_CONFGEN',
                           name=_('Servers: Generate configuration')),
                 Privilege(code='SRVTYPES_CREATE',
                           name=_('Servers: Create types')),
                 Privilege(code='SRVTYPES_EDIT',
                           name=_('Servers: Edit types')),
                 Privilege(code='SRVTYPES_DELETE',
                           name=_('Servers: Delete types')))
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

        bind_defaults = {
            'key_name_gen':          'nslink.',
            'key_name_int':          'nsexternal.',
            'key_name_ext':          'nsinternal.',
            'key_value_gen':         _gen_tsig(32),
            'key_value_int':         _gen_tsig(32),
            'key_value_ext':         _gen_tsig(32),
            'key_algo_gen':          'hmac-sha256',
            'key_algo_int':          'hmac-sha256',
            'key_algo_ext':          'hmac-sha256',
            'revzone_refresh':       3600,
            'revzone_retry':         300,
            'revzone_expire':        1814400,
            'revzone_minimum':       3600,
            # 'default_domain':        None,
            # 'hostmaster':            None,
            'dnssec':                'true',
            'dnssec_accept_expired': 'false',
            'split_dns':             'false',
            'only_external':         'false',
            'gen_spf':               'true',
            'gen_dkim':              'false',
            'gen_dmarc':             'false'
        }
        dhcp_defaults = {
            'dir_dhcp': '/etc/dhcp'
        }

        stypes = (
            ServerType(id=1,
                       name='ISC DHCP 3+',
                       generator_name='iscdhcp',
                       parameter_defaults=dhcp_defaults,
                       description='ISC DHCP server version 3+.'),
            ServerType(id=2,
                       name='ISC BIND 9.0-9.2',
                       generator_name='iscbind9',
                       parameter_defaults=bind_defaults,
                       description='ISC BIND DNS server versions 9.0-9.2.'),
            ServerType(id=3,
                       name='ISC BIND 9.3',
                       generator_name='iscbind93',
                       parameter_defaults=bind_defaults,
                       description='ISC BIND DNS server version 9.3.'),
            ServerType(id=4,
                       name='ISC BIND 9.4-9.8',
                       generator_name='iscbind94',
                       parameter_defaults=bind_defaults,
                       description='ISC BIND DNS server versions 9.4-9.8.'),
            ServerType(id=5,
                       name='Samba 3',
                       generator_name='samba3',
                       description='Samba NT domain server version 3.'),
            ServerType(id=6,
                       name='OpenSLP',
                       generator_name='openslp',
                       description='OpenSLP server.'),
            ServerType(id=7,
                       name='ISC BIND 9.9+',
                       generator_name='iscbind99',
                       parameter_defaults=bind_defaults,
                       description='ISC BIND DNS server versions 9.9+.'))

        for st in stypes:
            sess.add(st)

    def get_css(self, request):
        return ('netprofile_confgen:static/css/main.css',)

    def get_local_js(self, request, lang):
        return ('netprofile_confgen:static/webshell/locale/webshell-lang-'
                + lang + '.js',)

    def get_task_imports(self):
        return ('netprofile_confgen.tasks',)

    def get_controllers(self, request):
        return ('NetProfile.confgen.controller.ConfGen',)

    @property
    def name(self):
        return _('Config Generation')
