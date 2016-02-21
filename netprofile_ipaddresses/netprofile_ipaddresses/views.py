#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: IP addresses module - Views
# © Copyright 2013-2016 Alex 'Unik' Unigovsky
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

from pyramid.i18n import TranslationStringFactory
from netprofile.common.hooks import register_hook

_ = TranslationStringFactory('netprofile_ipaddresses')

@register_hook('core.dpanetabs.hosts.Host')
def _dpane_host_ipaddrs(tabs, model, req):
	if not req.has_permission('IPADDR_LIST'):
		return
	loc = req.localizer
	tabs.extend(({
		'title'             : loc.translate(_('IPv4')),
		'iconCls'           : 'ico-mod-ipv4address',
		'xtype'             : 'grid_ipaddresses_IPv4Address',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('host',),
		'extraParamProp'    : 'hostid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('IPv6')),
		'iconCls'           : 'ico-mod-ipv6address',
		'xtype'             : 'grid_ipaddresses_IPv6Address',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('host',),
		'extraParamProp'    : 'hostid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}))

@register_hook('core.dpanetabs.dialup.IPPool')
def _dpane_pool_ipaddrs(tabs, model, req):
	if not req.has_permission('IPADDR_LIST'):
		return
	loc = req.localizer
	tabs.extend(({
		'title'             : loc.translate(_('IPv4')),
		'iconCls'           : 'ico-mod-ipv4address',
		'xtype'             : 'grid_ipaddresses_IPv4Address',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('pool',),
		'extraParamProp'    : 'poolid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('IPv6')),
		'iconCls'           : 'ico-mod-ipv6address',
		'xtype'             : 'grid_ipaddresses_IPv6Address',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('pool',),
		'extraParamProp'    : 'poolid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}))

