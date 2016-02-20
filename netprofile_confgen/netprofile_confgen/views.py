#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Config Generation module - Views
# © Copyright 2014-2016 Alex 'Unik' Unigovsky
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

_ = TranslationStringFactory('netprofile_confgen')

@register_hook('core.dpanetabs.confgen.ServerType')
def _dpane_srvtype_servers(tabs, model, req):
	tabs.append({
		'title'             : req.localizer.translate(_('Servers')),
		'iconCls'           : 'ico-mod-server',
		'xtype'             : 'grid_confgen_Server',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('type',),
		'extraParamProp'    : 'srvtypeid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.confgen.Server')
def _dpane_srv_params(tabs, model, req):
	tabs.append({
		'title'             : req.localizer.translate(_('Parameters')),
		'iconCls'           : 'ico-mod-serverparameter',
		'xtype'             : 'grid_confgen_ServerParameter',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('server',),
		'extraParamProp'    : 'srvid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.hosts.Host')
def _dpane_district_streets(tabs, model, req):
	if not req.has_permission('SRV_LIST'):
		return
	tabs.append({
		'title'             : req.localizer.translate(_('Servers')),
		'iconCls'           : 'ico-mod-server',
		'xtype'             : 'grid_confgen_Server',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('host',),
		'extraParamProp'    : 'hostid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

