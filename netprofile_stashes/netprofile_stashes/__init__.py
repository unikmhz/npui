#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Stashes module
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

_ = TranslationStringFactory('netprofile_stashes')


class Module(ModuleBase):
    def __init__(self, mmgr):
        self.mmgr = mmgr
        mmgr.cfg.add_route(
            'stashes.cl.accounts',
            '/accounts/*traverse',
            factory='netprofile_stashes.views.ClientRootFactory',
            vhost='client')
        mmgr.cfg.add_translation_dirs('netprofile_stashes:locale/')

    @classmethod
    def get_deps(cls):
        return ('entities',)

    @classmethod
    def get_models(cls):
        from netprofile_stashes import models
        return (models.Currency,
                models.FuturePayment,
                models.Stash,
                models.StashIO,
                models.StashIOType,
                models.StashOperation)

    @classmethod
    def get_sql_functions(cls):
        from netprofile_stashes import models
        return (models.FuturesPollProcedure,)

    @classmethod
    def get_sql_events(cls):
        from netprofile_stashes import models
        return (models.FuturesPollEvent,)

    @classmethod
    def get_sql_data(cls, modobj, vpair, sess):
        from netprofile_stashes.models import (
            IOOperationType,
            IOFunctionType,
            OperationClass,
            StashIOType
        )
        from netprofile_core.models import (
            Group,
            GroupCapability,
            LogType,
            Privilege
        )

        if not vpair.is_install:
            return

        sess.add(LogType(id=12,
                         name='Stashes'))
        sess.add(LogType(id=16,
                         name='Promised Payments'))

        privs = (Privilege(code='BASE_STASHES',
                           name=_('Menu: Stashes')),
                 Privilege(code='STASHES_LIST',
                           name=_('Stashes: List')),
                 Privilege(code='STASHES_CREATE',
                           name=_('Stashes: Create')),
                 Privilege(code='STASHES_EDIT',
                           name=_('Stashes: Edit')),
                 Privilege(code='STASHES_DELETE',
                           name=_('Stashes: Delete')),
                 Privilege(code='STASHES_IO',
                           name=_('Stashes: Operations')),
                 Privilege(code='STASHES_IOTYPES_CREATE',
                           name=_('Stashes: Create op. types')),
                 Privilege(code='STASHES_IOTYPES_EDIT',
                           name=_('Stashes: Edit op. types')),
                 Privilege(code='STASHES_IOTYPES_DELETE',
                           name=_('Stashes: Delete op. types')),
                 Privilege(code='STASHES_CURRENCIES_CREATE',
                           name=_('Stashes: Create currencies')),
                 Privilege(code='STASHES_CURRENCIES_EDIT',
                           name=_('Stashes: Edit currencies')),
                 Privilege(code='STASHES_CURRENCIES_DELETE',
                           name=_('Stashes: Delete currencies')),
                 Privilege(code='BASE_FUTURES',
                           name=_('Menu: Promised payments')),
                 Privilege(code='FUTURES_LIST',
                           name=_('Promised payments: List')),
                 Privilege(code='FUTURES_CREATE',
                           name=_('Promised payments: Create')),
                 Privilege(code='FUTURES_EDIT',
                           name=_('Promised payments: Edit')),
                 Privilege(code='FUTURES_APPROVE',
                           name=_('Promised payments: Approve')),
                 Privilege(code='FUTURES_CANCEL',
                           name=_('Promised payments: Cancel')))
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

        siotypes = (
            StashIOType(
                id=1,
                name=_('Prepaid subscription fee'),
                io_class=OperationClass.system,
                type=IOOperationType.outgoing,
                function_type=IOFunctionType.rate_quota_prepaid,
                visible_to_operator=False,
                visible_to_user=True,
                description=_('Periodic withdrawal of funds for '
                              'an active service.')),
            StashIOType(
                id=2,
                name=_('Postpaid service fee'),
                io_class=OperationClass.system,
                type=IOOperationType.outgoing,
                function_type=IOFunctionType.rate_quota_postpaid,
                visible_to_operator=False,
                visible_to_user=True,
                description=_('Withdrawal of funds for used service.')),
            StashIOType(
                id=3,
                name=_('Reimbursement on rate conversion'),
                io_class=OperationClass.system,
                type=IOOperationType.incoming,
                function_type=IOFunctionType.rate_rollback,
                visible_to_operator=False,
                visible_to_user=True,
                description=_('Addition of funds that is a result of tariff '
                              'recalculation or operator action.')),
            # XXX: following one might be deprecated.
            StashIOType(
                id=4,
                name=_('Confirmation of promised payment'),
                io_class=OperationClass.system,
                type=IOOperationType.bidirectional,
                function_type=IOFunctionType.future_confirm,
                visible_to_operator=False,
                visible_to_user=True,
                fulfills_futures=True,
                description=_('This operation is a result of a payment '
                              'promise being fulfilled.')),
            StashIOType(
                id=5,
                name=_('Transfer from another account'),
                io_class=OperationClass.system,
                type=IOOperationType.incoming,
                function_type=IOFunctionType.transfer_deposit,
                visible_to_operator=False,
                visible_to_user=True,
                description=_('Addition of funds that were transferred '
                              'from another account.')),
            StashIOType(
                id=6,
                name=_('Transfer to another account'),
                io_class=OperationClass.system,
                type=IOOperationType.outgoing,
                function_type=IOFunctionType.transfer_withdrawal,
                visible_to_operator=False,
                visible_to_user=True,
                description=_('Withdrawal of funds that were transferred '
                              'to another account.')),
            StashIOType(
                id=7,
                name=_('Service activation fee'),
                io_class=OperationClass.system,
                type=IOOperationType.outgoing,
                function_type=IOFunctionType.service_initial,
                visible_to_operator=False,
                visible_to_user=True,
                description=_('Initial payment for activation of '
                              'an auxiliary service.')),
            StashIOType(
                id=8,
                name=_('Service subscription fee'),
                io_class=OperationClass.system,
                type=IOOperationType.outgoing,
                function_type=IOFunctionType.service_quota,
                visible_to_operator=False,
                visible_to_user=True,
                description=_('Periodic payment for maintaining '
                              'an auxiliary service.')))

        for siotype in siotypes:
            sess.add(siotype)

    def get_css(self, request):
        return ('netprofile_stashes:static/css/main.css',)

    def get_settings(self, vhost='MAIN', scope='global'):
        if vhost == 'MAIN' and scope == 'global':
            return (
                SettingSection(
                    'future_payments',
                    Setting(
                        'duration',
                        title=_('Duration of promised payments'),
                        help_text=_('Default maximum duration of promised '
                                    'payments that are created by customer.'),
                        type='int',
                        write_cap='FUTURES_EDIT',
                        default=5),
                    title=_('Administrative'),
                    help_text=_('Future payments settings.'),
                    read_cap='BASE_FUTURES')
            )

    @property
    def name(self):
        return _('Stashes')
