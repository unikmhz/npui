#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Dial-Up module - Views
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

from pyramid.i18n import TranslationStringFactory

from netprofile.common.hooks import register_hook

_ = TranslationStringFactory('netprofile_dialup')


@register_hook('core.dpanetabs.dialup.NAS')
def _dpane_nas_pools(tabs, model, req):
    tabs.append({
        'title':             req.localizer.translate(_('Pools')),
        'iconCls':           'ico-mod-naspool',
        'xtype':             'grid_dialup_NASPool',
        'stateId':           None,
        'stateful':          False,
        'hideColumns':       ('nas',),
        'extraParamProp':    'nasid',
        'createControllers': 'NetProfile.core.controller.RelatedWizard'
    })


@register_hook('core.dpanetabs.dialup.IPPool')
def _dpane_ippool_pools(tabs, model, req):
    if not req.has_permission('NAS_LIST'):
        return
    tabs.append({
        'title':             req.localizer.translate(_('NASes')),
        'iconCls':           'ico-mod-naspool',
        'xtype':             'grid_dialup_NASPool',
        'stateId':           None,
        'stateful':          False,
        'hideColumns':       ('pool',),
        'extraParamProp':    'poolid',
        'createControllers': 'NetProfile.core.controller.RelatedWizard'
    })
