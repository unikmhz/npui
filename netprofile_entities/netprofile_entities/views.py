#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import datetime as dt
from dateutil.parser import parse as dparse

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)
from netprofile.common.modules import IModuleManager
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession
from netprofile.ext.direct import extdirect_method

from .models import Entity

_ = TranslationStringFactory('netprofile_entities')

def dpane_entities(model, request):
	loc = get_localizer(request)
	tabs = [{
		'title'             : loc.translate(_('Addresses')),
		'iconCls'           : 'ico-mod-address',
		'xtype'             : 'grid_entities_Address',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('entity',),
		'extraParamProp'    : 'entityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('Phones')),
		'iconCls'           : 'ico-mod-phone',
		'xtype'             : 'grid_entities_Phone',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('entity',),
		'extraParamProp'    : 'entityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('Children')),
		'iconCls'           : 'ico-mod-entity',
		'xtype'             : 'grid_entities_Entity',
		'stateId'           : None,
		'stateful'          : False,
		'extraParamProp'    : 'parentid',
		'extraParamRelProp' : 'entityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('Files')),
		'iconCls'           : 'ico-attach',
		'componentCls'      : 'file-attach',
		'xtype'             : 'grid_entities_EntityFile',
		'stateId'           : None,
		'stateful'          : False,
		'rowEditing'        : False,
		'hideColumns'       : ('entity',),
		'extraParamProp'    : 'entityid',
		'viewConfig'        : {
			'plugins' : ({
				'ptype'           : 'gridviewdragdrop',
				'dropGroup'       : 'ddFile',
				'enableDrag'      : False,
				'enableDrop'      : True,
				'containerScroll' : True
			},)
		},
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('History')),
		'iconCls'           : 'ico-entity-history',
		'xtype'             : 'historygrid'
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

@extdirect_method('Entity', 'get_history', request_as_last_param=True, permission='ENTITIES_LIST')
def dyn_entity_history(params, request):
	eid = params.get('eid')
	if not eid:
		raise ValueError('No entity ID specified')
	begin = params.get('begin')
	end = params.get('end')
	cat = params.get('cat')
	maxnum = params.get('maxnum')
	sort = params.get('sort')
	sdir = params.get('dir')
	sess = DBSession()
	e = sess.query(Entity).get(int(eid))
	if not e:
		raise KeyError('No such entity found')
	if begin:
		xbegin = dparse(begin)
		if xbegin:
			begin = dt.datetime(
				xbegin.year,
				xbegin.month,
				xbegin.day,
				0, 0, 0
			)
		else:
			begin = None
	else:
		begin = None
	if end:
		xend = dparse(end)
		if xend:
			end = dt.datetime(
				xend.year,
				xend.month,
				xend.day,
				23, 59, 59
			)
		else:
			end = None
	else:
		end = None
	if maxnum:
		maxnum = int(maxnum)
	else:
		maxnum = 20
	ret = {
		'success' : True,
		'history' : e.get_history(request, begin, end, cat, maxnum, sort, sdir)
	}
	ret['total'] = len(ret['history'])
	return ret

