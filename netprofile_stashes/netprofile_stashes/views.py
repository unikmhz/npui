#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Stashes module - Views
# © Copyright 2013 Alex 'Unik' Unigovsky
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

from pyramid.security import authenticated_userid

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPFound,
    HTTPNotFound,
    HTTPSeeOther
)

from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession

from .models import FuturePayment
from netprofile_rates.models import Rate

_ = TranslationStringFactory('netprofile_stashes')

@register_hook('core.dpanetabs.entities.Entity')
@register_hook('core.dpanetabs.entities.PhysicalEntity')
@register_hook('core.dpanetabs.entities.LegalEntity')
@register_hook('core.dpanetabs.entities.StructuralEntity')
@register_hook('core.dpanetabs.entities.ExternalEntity')
def _dpane_entity_stashes(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Stashes')),
		'iconCls'           : 'ico-mod-stash',
		'xtype'             : 'grid_stashes_Stash',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('entity',),
		'extraParamProp'    : 'entityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.stashes.Stash')
def _dpane_stash_futures(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Futures')),
		'iconCls'           : 'ico-mod-stashio',
		'xtype'             : 'grid_stashes_FuturePayment',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('stash',),
		'extraParamProp'    : 'stashid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('core.dpanetabs.stashes.Stash')
def _dpane_stash_ios(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Operations')),
		'iconCls'           : 'ico-mod-stashio',
		'xtype'             : 'grid_stashes_StashIO',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('stash',),
		'extraParamProp'    : 'stashid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@view_config(route_name='access.cl.stashes', renderer='netprofile_stashes:templates/client_stashes.mak')
def client_stashes(request):

	if authenticated_userid(request) is None:
		return HTTPSeeOther(location=request.route_url('access.cl.login'))

	sess = DBSession()

	q = sess.query(Rate).filter(Rate.user_selectable == True)

	tpldef = {}
	tpldef = {
		'rates'	: q
	}

	request.run_hook('access.cl.tpldef', tpldef, request)
	request.run_hook('access.cl.tpldef.home', tpldef, request)

	return tpldef

@view_config(route_name='access.cl.chrate', renderer='netprofile_stashes:templates/client_stashes.mak')
def client_chrate(request):

	loc = get_localizer(request)
	csrf = request.POST.get('csrf', '')
	rateid = int(request.POST.get('rate', 1))

	if 'submit' in request.POST:
		sess = DBSession()
		if csrf != request.get_csrf():
			request.session.flash({
				'text' : loc.translate(_('Error submitting form')),
				'class' : 'danger'
			})
			return HTTPSeeOther(location=request.route_url('access.cl.stashes'))

		request.user.next_rate_id = rateid
	
		request.session.flash({
			'text' : loc.translate(_('Future paments done.'))
		})
		return HTTPSeeOther(location=request.route_url('access.cl.stashes'))

	request.session.flash({
		'text' : loc.translate(_('Error')),
		'class' : 'danger'
	})

@view_config(route_name='access.cl.dofuture', renderer='netprofile_stashes:templates/client_stashes.mak')
def client_futures(request):

	if authenticated_userid(request) is None:
		return HTTPSeeOther(location=request.route_url('access.cl.login'))

	loc = get_localizer(request)
	csrf = request.POST.get('csrf', '')
	stashid = int(request.POST.get('stashid', 1))
	diff = request.POST.get('diff', '')

	if 'submit' in request.POST:
		sess = DBSession()
		#FIXME add stash id checking
		if csrf != request.get_csrf():
			request.session.flash({
				'text' : loc.translate(_('Error submitting form')),
				'class' : 'danger'
			})
			return HTTPSeeOther(location=request.route_url('access.cl.stashes'))
	
		fp = FuturePayment()
		fp.stash_id = stashid
		fp.entity_id = authenticated_userid(request)
		fp.origin = 'user' 
		fp.difference = diff
		sess.add(fp)
		request.session.flash({
			'text' : loc.translate(_('Future paments done.'))
		})
		return HTTPSeeOther(location=request.route_url('access.cl.stashes'))

	request.session.flash({
		'text' : loc.translate(_('Error')),
		'class' : 'danger'
	})

	return HTTPSeeOther(location=request.route_url('access.cl.stashes'))

@view_config(route_name='access.cl.stats', renderer='netprofile_stashes:templates/client_stats.mak')
@view_config(route_name='access.cl.statsid', renderer='netprofile_stashes:templates/client_stats.mak')
def client_stats(request):

	if authenticated_userid(request) is None:
		return HTTPSeeOther(location=request.route_url('access.cl.login'))
	stash_id = request.matchdict.get('stash_id', 0)

	tpldef = {}
	tpldef = {
		'stash_id': stash_id,
	}

	request.run_hook('access.cl.tpldef', tpldef, request)
	request.run_hook('access.cl.tpldef.home', tpldef, request)

	return tpldef

@register_hook('access.cl.menu')
def _gen_menu(menu, req):
	menu.extend(({
		'route' : 'access.cl.stashes',
		'text'  : _('Stashes')
	},))

