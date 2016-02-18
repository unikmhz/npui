#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Devices module - Views
# © Copyright 2013-2016 Alex 'Unik' Unigovsky
# © Copyright 2014 Sergey Dikunov
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

from pyramid.security import has_permission
from pyramid.i18n import TranslationStringFactory
from netprofile.common.hooks import register_hook

_ = TranslationStringFactory('netprofile_devices')

@register_hook('core.dpanetabs.devices.NetworkDevice')
def _dpane_netdev_ifaces(tabs, model, req):
	loc = req.localizer
	tabs.append({
		'title'             : loc.translate(_('Interfaces')),
		'iconCls'           : 'ico-mod-networkdeviceinterface',
		'xtype'             : 'grid_devices_NetworkDeviceInterface',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('device',),
		'extraParamProp'    : 'did',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('np.model.actions.hosts.Host')
def _action_probe_hosts(actions, req, model):
	if has_permission('HOSTS_PROBE', req.context, req):
		actions.append({
			'iconCls' : 'ico-netmon',
			'tooltip' : _('Probe this host'),
			'itemId'  : 'probe'
		})

@register_hook('np.model.actions.entities.Entity')
@register_hook('np.model.actions.entities.PhysicalEntity')
@register_hook('np.model.actions.entities.LegalEntity')
@register_hook('np.model.actions.entities.StructuralEntity')
def _action_probe_entities(actions, req, model):
	if has_permission('HOSTS_PROBE', req.context, req):
		actions.append({
			'iconCls' : 'ico-netmon',
			'tooltip' : _('Probe this entity'),
			'itemId'  : 'probe'
		})

@register_hook('np.model.actions.domains.Domain')
def _action_probe_domains(actions, req, model):
	if has_permission('HOSTS_PROBE', req.context, req):
		actions.append({
			'iconCls' : 'ico-netmon',
			'tooltip' : _('Probe this domain'),
			'itemId'  : 'probe'
		})

