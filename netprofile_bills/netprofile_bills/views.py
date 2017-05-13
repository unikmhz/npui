#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Bills module - Views
# © Copyright 2017 Alex 'Unik' Unigovsky
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

_ = TranslationStringFactory('netprofile_bills')

@register_hook('core.dpanetabs.bills.BillType')
def _dpane_billtype_bills(tabs, model, req):
	loc = req.localizer
	if req.has_permission('BILLS_LIST'):
		tabs.append({
			'title'             : loc.translate(_('Bills')),
			'iconCls'           : 'ico-mod-bill',
			'xtype'             : 'grid_bills_Bill',
			'stateId'           : None,
			'stateful'          : False,
			'hideColumns'       : ('type',),
			'extraParamProp'    : 'btypeid',
			'createControllers' : 'NetProfile.core.controller.RelatedWizard'
		})

@register_hook('core.dpanetabs.entities.Entity')
@register_hook('core.dpanetabs.entities.PhysicalEntity')
@register_hook('core.dpanetabs.entities.LegalEntity')
@register_hook('core.dpanetabs.entities.StructuralEntity')
@register_hook('core.dpanetabs.entities.ExternalEntity')
def _dpane_entity_bills(tabs, model, req):
	loc = req.localizer
	if req.has_permission('BILLS_LIST'):
		tabs.append({
			'title'             : loc.translate(_('Bills')),
			'iconCls'           : 'ico-mod-bill',
			'xtype'             : 'grid_bills_Bill',
			'stateId'           : None,
			'stateful'          : False,
			'hideColumns'       : ('entity',),
			'extraParamProp'    : 'entityid',
			'createControllers' : 'NetProfile.core.controller.RelatedWizard'
		})

