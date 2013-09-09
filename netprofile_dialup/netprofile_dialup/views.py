#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

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

_ = TranslationStringFactory('netprofile_dialup')

@register_hook('core.dpanetabs.dialup.NAS')
def _dpane_nas_pools(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Pools')),
		'iconCls'           : 'ico-mod-naspool',
		'xtype'             : 'grid_dialup_NASPool',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('nas',),
		'extraParamProp'    : 'nasid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

