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

_ = TranslationStringFactory('netprofile_domains')

@register_hook('core.dpanetabs.domains.Domain')
def _dpane_domain_aliases(tabs, model, req):
	loc = get_localizer(req)
	tabs.extend(({
		'title'             : loc.translate(_('Subdomains')),
		'xtype'             : 'grid_domains_Domain',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('parent',),
		'extraParamProp'    : 'parentid',
		'extraParamRelProp' : 'domainid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('Aliases')),
		'xtype'             : 'grid_domains_DomainAlias',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('domain',),
		'extraParamProp'    : 'domainid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('TXT Records')),
		'xtype'             : 'grid_domains_DomainTXTRecord',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('domain',),
		'extraParamProp'    : 'domainid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}))

