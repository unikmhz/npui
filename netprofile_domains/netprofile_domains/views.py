#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Domains module - Views
# © Copyright 2013 Nikita Andriyanov
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

_ = TranslationStringFactory('netprofile_domains')

@register_hook('core.dpanetabs.domains.Domain')
def _dpane_domain_aliases(tabs, model, req):
	loc = req.localizer
	tabs.extend(({
		'title'             : loc.translate(_('Subdomains')),
		'iconCls'           : 'ico-mod-domain',
		'xtype'             : 'grid_domains_Domain',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('parent',),
		'extraParamProp'    : 'parentid',
		'extraParamRelProp' : 'domainid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('Aliases')),
		'iconCls'           : 'ico-mod-domainalias',
		'xtype'             : 'grid_domains_DomainAlias',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('domain',),
		'extraParamProp'    : 'domainid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('TXT Records')),
		'iconCls'           : 'ico-mod-domaintxtrecord',
		'xtype'             : 'grid_domains_DomainTXTRecord',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('domain',),
		'extraParamProp'    : 'domainid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}))

