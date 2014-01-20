#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Stashes module - Views
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

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPSeeOther

from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession

from .models import (
	FuturePayment,
	FuturePaymentOrigin
)
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

@view_config(route_name='stashes.cl.stashes', renderer='netprofile_stashes:templates/client_stashes.mak', permission='USAGE')
def client_stashes(request):
	sess = DBSession()
	# FIXME: add classes etc.
	q = sess.query(Rate).filter(Rate.user_selectable == True)

	tpldef = {
		'rates'	: q
	}
	request.run_hook('access.cl.tpldef', tpldef, request)
	request.run_hook('access.cl.tpldef.stashes', tpldef, request)
	return tpldef

@view_config(
	route_name='stashes.cl.chrate',
	request_method='POST',
	permission='USAGE'
)
def client_chrate(request):
	from netprofile_access.models import AccessEntity
	loc = get_localizer(request)
	csrf = request.POST.get('csrf', '')
	rate_id = int(request.POST.get('rateid'), 0)
	aent_id = int(request.POST.get('entityid'))
	ent = request.user.parent
	err = True

	if csrf == request.get_csrf():
		sess = DBSession()
		aent = sess.query(AccessEntity).get(aent_id)
		if ent and aent and (aent.parent == ent):
			err = False
			if 'clear' in request.POST:
				rate_id = None
				aent.next_rate_id = None
			elif rate_id > 0:
				aent.next_rate_id = rate_id

	if err:
		request.session.flash({
			'text' : loc.translate(_('Error scheduling rate change')),
			'class' : 'danger'
		})
	elif rate_id:
		request.session.flash({
			'text' : loc.translate(_('Rate change successfully scheduled'))
		})
	else:
		request.session.flash({
			'text' : loc.translate(_('Rate change successfully cancelled'))
		})
	return HTTPSeeOther(location=request.route_url('stashes.cl.stashes'))

@view_config(
	route_name='stashes.cl.dofuture',
	request_method='POST',
	permission='USAGE'
)
def client_futures(request):
	loc = get_localizer(request)
	csrf = request.POST.get('csrf', '')
	stashid = int(request.POST.get('stashid'))
	diff = request.POST.get('diff', '')

	if 'submit' in request.POST:
		sess = DBSession()
		#FIXME add stash id checking
		if csrf != request.get_csrf():
			request.session.flash({
				'text' : loc.translate(_('Error submitting form')),
				'class' : 'danger'
			})
			return HTTPSeeOther(location=request.route_url('stashes.cl.stashes'))
		fp = FuturePayment()
		fp.stash_id = stashid
		fp.entity = request.user.parent
		fp.origin = FuturePaymentOrigin.user
		fp.difference = diff
		sess.add(fp)
		request.session.flash({
			'text' : loc.translate(_('Successfully added new promised payment'))
		})
		return HTTPSeeOther(location=request.route_url('stashes.cl.stashes'))

	request.session.flash({
		'text' : loc.translate(_('Error submitting form')),
		'class' : 'danger'
	})

	return HTTPSeeOther(location=request.route_url('stashes.cl.stashes'))

@view_config(route_name='stashes.cl.stats', renderer='netprofile_stashes:templates/client_stats.mak', permission='USAGE')
@view_config(route_name='stashes.cl.statsid', renderer='netprofile_stashes:templates/client_stats.mak', permission='USAGE')
def client_stats(request):
	stash_id = request.matchdict.get('stash_id', 0)

	tpldef = {}
	tpldef = {
		'stash_id': stash_id,
	}

	request.run_hook('access.cl.tpldef', tpldef, request)
	request.run_hook('access.cl.tpldef.stash.stats', tpldef, request)
	return tpldef

@register_hook('access.cl.menu')
def _gen_menu(menu, req):
	menu.append({
		'route' : 'stashes.cl.stashes',
		'text'  : _('Accounts')
	})

