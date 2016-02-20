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
from sqlalchemy.orm import with_polymorphic
from netprofile.db.connection import DBSession
from netprofile.common.hooks import register_hook

from .models import NetworkDevice
from netprofile_hosts.models import Host
from netprofile_entities.models import (
	Address,
	Entity
)
from netprofile_geo.models import (
	House,
	HouseGroupMapping,
	Street
)

_ = TranslationStringFactory('netprofile_devices')

@register_hook('core.dpanetabs.devices.NetworkDevice')
def _dpane_netdev_ifaces(tabs, model, req):
	loc = req.localizer
	tabs.extend(({
		'title'             : loc.translate(_('Interfaces')),
		'iconCls'           : 'ico-mod-networkdeviceinterface',
		'xtype'             : 'grid_devices_NetworkDeviceInterface',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('device',),
		'extraParamProp'    : 'did',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}, {
		'title'             : loc.translate(_('Bindings')),
		'iconCls'           : 'ico-mod-networkdevicebinding',
		'xtype'             : 'grid_devices_NetworkDeviceBinding',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('device',),
		'extraParamProp'    : 'did',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	}))

@register_hook('core.dpanetabs.devices.NetworkDeviceInterface')
def _dpane_iface_bindings(tabs, model, req):
	loc = req.localizer
	tabs.append({
		'title'             : loc.translate(_('Bindings')),
		'iconCls'           : 'ico-mod-networkdevicebinding',
		'xtype'             : 'grid_devices_NetworkDeviceBinding',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('device', 'interface'),
		'extraParamProp'    : 'ifid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.hosts.Host')
def _dpane_host_bindings(tabs, model, req):
	loc = req.localizer
	tabs.append({
		'title'             : loc.translate(_('Bindings')),
		'iconCls'           : 'ico-mod-networkdevicebinding',
		'xtype'             : 'grid_devices_NetworkDeviceBinding',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('host',),
		'extraParamProp'    : 'hostid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('np.model.actions.hosts.Host')
def _action_probe_host(actions, req, model):
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
def _action_probe_entity(actions, req, model):
	if has_permission('HOSTS_PROBE', req.context, req):
		actions.append({
			'iconCls' : 'ico-netmon',
			'tooltip' : _('Probe this entity\'s hosts'),
			'itemId'  : 'probe'
		})

@register_hook('np.model.actions.domains.Domain')
def _action_probe_domain(actions, req, model):
	if has_permission('HOSTS_PROBE', req.context, req):
		actions.append({
			'iconCls' : 'ico-netmon',
			'tooltip' : _('Probe hosts in this domain'),
			'itemId'  : 'probe'
		})

@register_hook('np.model.actions.geo.House')
def _action_probe_house(actions, req, model):
	if has_permission('HOSTS_PROBE', req.context, req):
		actions.append({
			'iconCls' : 'ico-netmon',
			'tooltip' : _('Probe hosts in this house'),
			'itemId'  : 'probe'
		})

@register_hook('np.model.actions.geo.Street')
def _action_probe_street(actions, req, model):
	if has_permission('HOSTS_PROBE', req.context, req):
		actions.append({
			'iconCls' : 'ico-netmon',
			'tooltip' : _('Probe hosts on this street'),
			'itemId'  : 'probe'
		})

@register_hook('np.model.actions.geo.District')
def _action_probe_district(actions, req, model):
	if has_permission('HOSTS_PROBE', req.context, req):
		actions.append({
			'iconCls' : 'ico-netmon',
			'tooltip' : _('Probe hosts in this district'),
			'itemId'  : 'probe'
		})

@register_hook('np.model.actions.geo.City')
def _action_probe_city(actions, req, model):
	if has_permission('HOSTS_PROBE', req.context, req):
		actions.append({
			'iconCls' : 'ico-netmon',
			'tooltip' : _('Probe hosts in this city'),
			'itemId'  : 'probe'
		})

@register_hook('np.model.actions.geo.HouseGroup')
def _action_probe_housegroup(actions, req, model):
	if has_permission('HOSTS_PROBE', req.context, req):
		actions.append({
			'iconCls' : 'ico-netmon',
			'tooltip' : _('Probe hosts in this house group'),
			'itemId'  : 'probe'
		})

@register_hook('np.model.actions.geo.Place')
def _action_probe_place(actions, req, model):
	if has_permission('HOSTS_PROBE', req.context, req):
		actions.append({
			'iconCls' : 'ico-netmon',
			'tooltip' : _('Probe network devices located here'),
			'itemId'  : 'probe'
		})

@register_hook('devices.probe_hosts')
def _probe_query_hosts(probe_type, ids, cfg, hm, queries):
	if probe_type == 'hosts':
		queries.append(DBSession().query(Host)\
			.filter(Host.id.in_(ids))
		)
	elif probe_type == 'entities':
		queries.append(DBSession().query(Host)\
			.filter(Host.entity_id.in_(ids))
		)
	elif probe_type == 'domains':
		queries.append(DBSession().query(Host)\
			.filter(Host.domain_id.in_(ids))
		)
	elif probe_type == 'houses':
		queries.append(DBSession().query(Host)\
			.join(with_polymorphic(Entity, Entity))\
			.join(Address)\
			.filter(Address.house_id.in_(ids))
		)
	elif probe_type == 'streets':
		queries.append(DBSession().query(Host)\
			.join(with_polymorphic(Entity, Entity))\
			.join(Address)\
			.join(House)\
			.filter(House.street_id.in_(ids))
		)
	elif probe_type == 'districts':
		queries.append(DBSession().query(Host)\
			.join(with_polymorphic(Entity, Entity))\
			.join(Address)\
			.join(House)\
			.join(Street)\
			.filter(Street.district_id.in_(ids))
		)
	elif probe_type == 'cities':
		queries.append(DBSession().query(Host)\
			.join(with_polymorphic(Entity, Entity))\
			.join(Address)\
			.join(House)\
			.join(Street)\
			.filter(Street.city_id.in_(ids))
		)
	elif probe_type == 'housegroups':
		queries.append(DBSession().query(Host)\
			.join(with_polymorphic(Entity, Entity))\
			.join(Address)\
			.join(House)\
			.join(HouseGroupMapping)\
			.filter(HouseGroupMapping.group_id.in_(ids))
		)
	elif probe_type == 'places':
		queries.append(DBSession().query(Host)\
			.join(NetworkDevice)\
			.filter(NetworkDevice.place_id.in_(ids))
		)

