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
from netprofile.common.modules import IModuleManager
from netprofile.common.hooks import register_hook

_ = TranslationStringFactory('netprofile_entities')

def dpane_entities(model, request):
	loc = get_localizer(request)
	tabs = [{
		'title'             : loc.translate(_('Children')),
		'iconCls'           : 'ico-mod-entity',
		'xtype'             : 'grid_entities_Entity',
		'stateId'           : None,
		'stateful'          : False,
		'extraParamProp'    : 'parentid',
		'extraParamRelProp' : 'entityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}]
	request.run_hook(
		'core.dpanetabs.%s.%s' % (model.__parent__.moddef, model.name),
		tabs, model, request
	)
	cont = {
		'border' : 0,
		'layout' : {
			'type'    : 'hbox',
			'align'   : 'stretch',
			'padding' : 4
		},
		'items' : [{
			'xtype' : 'npform',
			'flex'  : 2
		}, {
			'xtype' : 'splitter'
		}, {
			'xtype'  : 'tabpanel',
			'flex'   : 3,
			'items'  : tabs
		}]
	}
	request.run_hook(
		'core.dpane.%s.%s' % (model.__parent__.moddef, model.name),
		cont, model, request
	)
	return cont

@register_hook('core.validators.CreateEntity')
def new_entity_validator(ret, values, request):
	# FIXME: handle permissions
	if 'etype' not in values:
		return
	mod = request.registry.getUtility(IModuleManager).get_module_browser()['entities']
	em = None
	etype = values['etype']
	if etype == 'physical':
		em = mod['PhysicalEntity']
	elif etype == 'legal':
		em = mod['LegalEntity']
	elif etype == 'structural':
		em = mod['StructuralEntity']
	elif etype == 'external':
		em = mod['ExternalEntity']
	else:
		return
	xret = em.validate_fields(values, request)
	if 'errors' in xret:
		ret['errors'].update(xret['errors'])

