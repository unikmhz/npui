#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from sqlalchemy.orm import joinedload

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession

from netprofile_core.models import User
from .models import ICDHistory

_ = TranslationStringFactory('netprofile_medical')

@register_hook('core.dpanetabs.tickets.Ticket')
def _dpane_ticket_tabs(tabs, model, req):
	loc = get_localizer(req)
	tabs.extend(({
		'title'             : loc.translate(_('Diseases')),
		'iconCls'           : 'ico-mod-icdmapping',
		'xtype'             : 'grid_medical_ICDMapping',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('entity', 'ticket'),
		'extraParamProp'    : 'ticketid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('Tests')),
		'iconCls'           : 'ico-mod-medicaltest',
		'xtype'             : 'grid_medical_MedicalTest',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('ticket',),
		'extraParamProp'    : 'ticketid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}))

@register_hook('core.dpanetabs.entities.PhysicalEntity')
def _dpane_entity_mappings(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Diseases')),
		'iconCls'           : 'ico-mod-icdmapping',
		'xtype'             : 'grid_medical_ICDMapping',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('entity',),
		'extraParamProp'    : 'entityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.medical.ICDClass')
def _dpane_icdclass_blocks(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Blocks')),
		'iconCls'           : 'ico-mod-icdblock',
		'xtype'             : 'grid_medical_ICDBlock',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('class',),
		'extraParamProp'    : 'icdcid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.medical.ICDBlock')
def _dpane_icdblock_entries(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Entries')),
		'iconCls'           : 'ico-mod-icdentry',
		'xtype'             : 'grid_medical_ICDEntry',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('block',),
		'extraParamProp'    : 'icdbid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('entities.history.get.all')
@register_hook('entities.history.get.diseases')
def _ent_hist_diseases(hist, ent, req, begin, end, max_num):
	sess = DBSession()

	# TODO: check permissions
	q = sess.query(ICDHistory).options(joinedload(ICDHistory.user)).filter(ICDHistory.entity == ent)
	if begin is not None:
		q = q.filter(ICDHistory.timestamp >= begin)
	if end is not None:
		q = q.filter(ICDHistory.timestamp <= end)
	if max_num:
		q = q.limit(max_num)
	for ih in q:
		pass
		eh = ih.get_entity_history(req)
		if eh:
			hist.append(eh)

