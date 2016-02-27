#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Entities module - Views
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

import datetime as dt
from dateutil.parser import parse as dparse
from pyramid.i18n import TranslationStringFactory

from netprofile.common.modules import IModuleManager
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession
from netprofile.ext.direct import extdirect_method

from .models import (
	Entity,
	EntityType
)

_ = TranslationStringFactory('netprofile_entities')

@register_hook('core.dpanetabs.entities.Entity')
@register_hook('core.dpanetabs.entities.PhysicalEntity')
@register_hook('core.dpanetabs.entities.LegalEntity')
@register_hook('core.dpanetabs.entities.StructuralEntity')
@register_hook('core.dpanetabs.entities.ExternalEntity')
def _dpane_entities(tabs, model, req):
	loc = req.localizer
	tabs.extend([{
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
	}]);

@register_hook('core.validators.CreateEntity')
def new_entity_validator(ret, values, request):
	# FIXME: handle permissions
	if 'etypeid' not in values:
		return
	sess = DBSession()
	try:
		ent_type = sess.query(EntityType).get(int(values['etypeid']))
	except (TypeError, ValueError):
		ent_type = None
	# FIXME: error out on non-existent types
	if ent_type is None:
		return
	parent_id = values.get('parentid')
	if not parent_id and not ent_type.root:
		ret['errors']['parent'].append(request.localizer.translate(_('This entity requires a parent.')))
	if parent_id:
		try:
			parent = sess.query(Entity).get(int(parent_id))
			if parent and parent.type.leaf:
				ret['errors']['parent'].append(request.localizer.translate(_('This entity can\'t have children.')))
		except (TypeError, ValueError):
			pass
	mod = request.registry.getUtility(IModuleManager).get_module_browser()[ent_type.module.name]
	em = mod[ent_type.model]
	xret = em.validate_fields(values, request)
	if 'errors' in xret:
		ret['errors'].update(xret['errors'])

@register_hook('documents.gen.object')
def _doc_gen_obj(tpl_vars, objid, objtype, req):
	if objtype != 'entity':
		return
	obj = DBSession().query(Entity).get(objid)
	if not obj:
		return
	v = obj.template_vars(req)
	if v:
		tpl_vars.update({ 'entity' : v })

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
	e = DBSession().query(Entity).get(int(eid))
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

