#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Geo module - Views
# © Copyright 2013 Nikita Andriyanov
# © Copyright 2013-2015 Alex 'Unik' Unigovsky
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

_ = TranslationStringFactory('netprofile_geo')

@register_hook('core.dpanetabs.geo.City')
def _dpane_city_districts(tabs, model, req):
	loc = get_localizer(req)
	tabs.extend(({
		'title'             : loc.translate(_('Districts')),
		'iconCls'           : 'ico-mod-district',
		'xtype'             : 'grid_geo_District',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('city',),
		'extraParamProp'    : 'cityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('Streets')),
		'iconCls'           : 'ico-mod-street',
		'xtype'             : 'grid_geo_Street',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('city',),
		'extraParamProp'    : 'cityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}))

@register_hook('core.dpanetabs.geo.District')
def _dpane_district_streets(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Streets')),
		'iconCls'           : 'ico-mod-street',
		'xtype'             : 'grid_geo_Street',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('district',),
		'extraParamProp'    : 'districtid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.geo.Street')
def _dpane_street_houses(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Houses')),
		'iconCls'           : 'ico-mod-house',
		'xtype'             : 'grid_geo_House',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('street',),
		'extraParamProp'    : 'streetid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.geo.House')
def _dpane_house_places(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Places')),
		'iconCls'           : 'ico-mod-place',
		'xtype'             : 'grid_geo_Place',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('house',),
		'extraParamProp'    : 'houseid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

