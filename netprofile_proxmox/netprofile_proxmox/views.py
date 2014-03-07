#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Proxmox VE integration module - Views
# © Copyright 2013-2014 Alex 'Unik' Unigovsky
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

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

import pyproxmox 
import requests 
from pyramid.view import view_config
from pyramid.httpexceptions import (
	HTTPForbidden,
	HTTPSeeOther
)
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

from netprofile.common.factory import RootFactory
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession

from netprofile_access.models import AccessEntity

_ = TranslationStringFactory('netprofile_proxmox')
@view_config(
	route_name='proxmox.cl.vmachines',
	permission='USAGE',
	renderer='netprofile_proxmox:templates/client_vm.mak'
)
def virtual_machines(request):
	cfg = request.registry.settings
	sess = DBSession()
	errmess = None
	tpldef = {'errmessage':errmess}
	request.run_hook('access.cl.tpldef', tpldef, request)
	access_user = sess.query(AccessEntity).filter_by(nick=str(request.user)).first()
	proxmox_host = cfg.get('netprofile.client.proxmox.host')
	proxmox_auth = cfg.get('netprofile.client.proxmox.auth_method')
	try:
		vm = pyproxmox.pyproxmox(proxmox_host, "{0}@{1}".format(access_user.nick, proxmox_auth), access_user.password)
	except TypeError:
		vm = None
	except requests.exceptions.ConnectionError as e:
		vm = None
		errmess = "Can't connect to server"
	
	vmachines = []
	resp = False
	if vm:
		cluster_resources = vm.getClusterResources()
		for el in cluster_resources['data']:
			vmname = el.get('name', None)
			if vmname and vmname.split('.')[0] == access_user.nick:
				vmid = el.get('vmid', None)
				node = el.get('node', None)
				el['ip'] = vm.getContainerStatus(node, vmid)['data']['ip']
				vmachines.append(el)

		if request.GET.get('action', None):
			action = request.GET.get('action', None)
			vmid = request.GET.get('vmid', None)
			node = request.GET.get('node', None)
			vmtype = request.GET.get('type', None)
			vmindex = [vmachines.index(x) for x in vmachines if x['vmid'] == int(vmid)][-1]
			if vmtype == 'openvz':
				if action == 'start':
					resp = vm.startOpenvzContainer(node,vmid)
				elif action == 'stop':
					resp = vm.stopOpenvzContainer(node,vmid)
				else:
					pass
		
			elif vmtype == 'kvm':
				if action == 'stop':
					resp = vm.stopVirtualMachine(node,vmid)
				elif action == 'start':
					resp = vm.startVirtualMachine(node,vmid)
				else:
					pass
			#обновляем статус машины
			if action == 'start' and resp:
				vmachines[vmindex]['status'] = 'running'
			elif action == 'stop' and resp:
				vmachines[vmindex]['status'] = 'stopped'
			
			tpldef.update({
			'vmachines':vmachines,
			})
			return tpldef

		
	tpldef.update({
			'vmachines':vmachines,
			'errmessage':errmess
			})
		
	return tpldef


@register_hook('access.cl.menu')
def _gen_menu(menu, req):
	menu.append({
		'route' : 'proxmox.cl.vmachines',
		'text'  : _('Virtual Machines')
	})

