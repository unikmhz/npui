#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Paid Service module - Views
# © Copyright 2014-2017 Alex 'Unik' Unigovsky
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

_ = TranslationStringFactory('netprofile_paidservices')

@register_hook('core.dpanetabs.entities.Entity')
@register_hook('core.dpanetabs.entities.PhysicalEntity')
@register_hook('core.dpanetabs.entities.LegalEntity')
@register_hook('core.dpanetabs.entities.StructuralEntity')
@register_hook('core.dpanetabs.entities.ExternalEntity')
def _dpane_entity_paidservices(tabs, model, req):
	if not req.has_permission('PAIDSERVICES_LIST'):
		return
	tabs.append({
		'title'             : req.localizer.translate(_('Paid Services')),
		'iconCls'           : 'ico-mod-paidservice',
		'xtype'             : 'grid_paidservices_PaidService',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('entity',),
		'extraParamProp'    : 'entityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.stashes.Stash')
def _dpane_stash_futures(tabs, model, req):
	if not req.has_permission('PAIDSERVICES_LIST'):
		return
	tabs.append({
		'title'             : req.localizer.translate(_('Paid Services')),
		'iconCls'           : 'ico-mod-paidservice',
		'xtype'             : 'grid_paidservices_PaidService',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('stash',),
		'extraParamProp'    : 'stashid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

