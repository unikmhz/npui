#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: TV subscription module - Views
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

from pyramid.i18n import TranslationStringFactory

from netprofile.common.hooks import register_hook

_ = TranslationStringFactory('netprofile_tv')


@register_hook('core.dpanetabs.entities.Entity')
@register_hook('core.dpanetabs.entities.PhysicalEntity')
@register_hook('core.dpanetabs.entities.LegalEntity')
@register_hook('core.dpanetabs.entities.StructuralEntity')
@register_hook('core.dpanetabs.entities.ExternalEntity')
def _dpane_entity_subscriptions(tabs, model, req):
    if not req.has_permission('TV_PKG_LIST'):
        return
    tabs.append({
        'title':             req.localizer.translate(_('TV Subscriptions')),
        'iconCls':           'ico-mod-tvsubscription',
        'xtype':             'grid_tv_TVSubscription',
        'stateId':           None,
        'stateful':          False,
        'hideColumns':       ('entity',),
        'extraParamProp':    'entityid',
        'createControllers': 'NetProfile.core.controller.RelatedWizard'
    })


@register_hook('core.dpanetabs.access.AccessEntity')
def _dpane_access_tv(tabs, model, req):
    loc = req.localizer
    if req.has_permission('TV_PKG_LIST'):
        tabs.append({
            'title':             loc.translate(_('TV Subscriptions')),
            'iconCls':           'ico-mod-tvsubscription',
            'xtype':             'grid_tv_TVSubscription',
            'stateId':           None,
            'stateful':          False,
            'hideColumns':       ('entity', 'access_entity'),
            'extraParamProp':    'aeid',
            'extraParamRelProp': 'entityid',
            'createControllers': 'NetProfile.core.controller.RelatedWizard'
        })
    if req.has_permission('TV_CARDS_LIST'):
        tabs.append({
            'title':             loc.translate(_('TV Cards')),
            'iconCls':           'ico-mod-tvaccesscard',
            'xtype':             'grid_tv_TVAccessCard',
            'stateId':           None,
            'stateful':          False,
            'hideColumns':       ('access_entity',),
            'extraParamProp':    'aeid',
            'extraParamRelProp': 'entityid',
            'createControllers': 'NetProfile.core.controller.RelatedWizard'
        })


@register_hook('core.dpanetabs.tv.TVSourceType')
def _dpane_sourcetype_sources(tabs, model, req):
    tabs.append({
        'title':             req.localizer.translate(_('Sources')),
        'iconCls':           'ico-mod-tvsource',
        'xtype':             'grid_tv_TVSource',
        'stateId':           None,
        'stateful':          False,
        'hideColumns':       ('type',),
        'extraParamProp':    'tvstid',
        'createControllers': 'NetProfile.core.controller.RelatedWizard'
    })


@register_hook('core.dpanetabs.tv.TVSource')
def _dpane_source_tabs(tabs, model, req):
    loc = req.localizer
    tabs.append({
        'title':             loc.translate(_('Channels')),
        'iconCls':           'ico-mod-tvchannel',
        'xtype':             'grid_tv_TVChannel',
        'stateId':           None,
        'stateful':          False,
        'hideColumns':       ('source',),
        'extraParamProp':    'tvsourceid',
        'createControllers': 'NetProfile.core.controller.RelatedWizard'
    })
    if req.has_permission('TV_CARDS_LIST'):
        tabs.append({
            'title':             loc.translate(_('TV Cards')),
            'iconCls':           'ico-mod-tvaccesscard',
            'xtype':             'grid_tv_TVAccessCard',
            'stateId':           None,
            'stateful':          False,
            'hideColumns':       ('source',),
            'extraParamProp':    'tvsourceid',
            'createControllers': 'NetProfile.core.controller.RelatedWizard'
        })
