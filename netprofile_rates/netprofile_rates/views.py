#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Rates module - Views
# © Copyright 2013 Alex 'Unik' Unigovsky
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

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)
from netprofile.common.hooks import register_hook

_ = TranslationStringFactory('netprofile_rates')

@register_hook('core.dpanetabs.rates.Rate')
def _dpane_rate_mods(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Modifiers')),
		'iconCls'           : 'ico-mod-ratemodifiertype',
		'xtype'             : 'grid_rates_GlobalRateModifier',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('rate',),
		'extraParamProp'    : 'rateid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.rates.RateClass')
def _dpane_rc_entities(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Entity Types')),
		'iconCls'           : 'ico-mod-entity',
		'xtype'             : 'grid_rates_EntityTypeRateClass',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('class',),
		'extraParamProp'    : 'rcid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.rates.DestinationSet')
def _dpane_destset_contents(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Contents')),
		'iconCls'           : 'ico-mod-destination',
		'xtype'             : 'grid_rates_Destination',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('set',),
		'extraParamProp'    : 'dsid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.rates.FilterSet')
def _dpane_filterset_contents(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Contents')),
		'iconCls'           : 'ico-mod-filter',
		'xtype'             : 'grid_rates_Filter',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('set',),
		'extraParamProp'    : 'fsid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

