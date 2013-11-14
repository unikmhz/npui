#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Networks module - Views
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

_ = TranslationStringFactory('netprofile_networks')

@register_hook('core.dpanetabs.networks.Network')
def _dpane_network_services(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Services')),
		'iconCls'           : 'ico-mod-networkservice',
		'xtype'             : 'grid_networks_NetworkService',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('network',),
		'extraParamProp'    : 'netid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.networks.NetworkGroup')
def _dpane_netgroup_nets(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Networks')),
		'iconCls'           : 'ico-mod-network',
		'xtype'             : 'grid_networks_Network',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('group',),
		'extraParamProp'    : 'netgid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.networks.RoutingTable')
def _dpane_rt_bits(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Entries')),
		'iconCls'           : 'ico-mod-routingtableentry',
		'xtype'             : 'grid_networks_RoutingTableEntry',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('table',),
		'extraParamProp'    : 'rtid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

