#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Hosts module - Views
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

_ = TranslationStringFactory('netprofile_hosts')

@register_hook('core.dpanetabs.hosts.Host')
def _dpane_host_services(tabs, model, req):
	loc = get_localizer(req)
	tabs.extend(({
		'title'             : loc.translate(_('Services')),
		'iconCls'           : 'ico-mod-service',
		'xtype'             : 'grid_hosts_Service',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('host',),
		'extraParamProp'    : 'hostid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('Aliases')),
		'iconCls'           : 'ico-mod-hostalias',
		'xtype'             : 'grid_hosts_Host',
		'stateId'           : None,
		'stateful'          : False,
		'extraParamProp'    : 'aliasid',
		'extraParamRelProp' : 'hostid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}))

@register_hook('core.dpanetabs.entities.Entity')
@register_hook('core.dpanetabs.entities.PhysicalEntity')
@register_hook('core.dpanetabs.entities.LegalEntity')
@register_hook('core.dpanetabs.entities.StructuralEntity')
@register_hook('core.dpanetabs.entities.ExternalEntity')
def _dpane_entity_hosts(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Hosts')),
		'iconCls'           : 'ico-mod-host',
		'xtype'             : 'grid_hosts_Host',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('entity',),
		'extraParamProp'    : 'entityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.domains.Domain')
def _dpane_domain_services(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Services')),
		'iconCls'           : 'ico-mod-domainservice',
		'xtype'             : 'grid_hosts_DomainService',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('domain',),
		'extraParamProp'    : 'domainid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

