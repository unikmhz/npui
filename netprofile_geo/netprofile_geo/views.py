#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
	tabs.append({
		'title'          : loc.translate(_('Districts')),
		'xtype'          : 'grid_geo_District',
		'stateId'        : None,
		'stateful'       : False,
		'hideColumns'    : ('city',),
		'extraParamProp' : 'cityid'
	})

@register_hook('core.dpanetabs.geo.District')
def _dpane_district_streets(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'          : loc.translate(_('Streets')),
		'xtype'          : 'grid_geo_Street',
		'stateId'        : None,
		'stateful'       : False,
		'hideColumns'    : ('district',),
		'extraParamProp' : 'districtid'
	})

@register_hook('core.dpanetabs.geo.Street')
def _dpane_street_houses(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'          : loc.translate(_('Houses')),
		'xtype'          : 'grid_geo_House',
		'stateId'        : None,
		'stateful'       : False,
		'hideColumns'    : ('street',),
		'extraParamProp' : 'streetid'
	})

@register_hook('core.dpanetabs.geo.House')
def _dpane_house_places(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'          : loc.translate(_('Places')),
		'xtype'          : 'grid_geo_Place',
		'stateId'        : None,
		'stateful'       : False,
		'hideColumns'    : ('house',),
		'extraParamProp' : 'houseid'
	})

