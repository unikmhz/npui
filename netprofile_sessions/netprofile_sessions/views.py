#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Sessions module - Views
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

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)

import math
import datetime as dt
from dateutil.parser import parse as dparse
from dateutil.relativedelta import relativedelta

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from sqlalchemy import func
from netprofile.common.hooks import register_hook
from netprofile.db.connection import DBSession

from netprofile_stashes.models import Stash
from netprofile_access.models import AccessEntity
from .models import (
	AccessSession,
	AccessSessionHistory
)

_ = TranslationStringFactory('netprofile_sessions')
_st = TranslationStringFactory('netprofile_stashes')

@register_hook('core.dpanetabs.access.AccessEntity')
def _dpane_access_sessions(tabs, model, req):
	loc = get_localizer(req)
	tabs.extend(({
		'title'             : loc.translate(_('Active Sessions')),
		'iconCls'           : 'ico-mod-accesssession',
		'xtype'             : 'grid_sessions_AccessSession',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('entity',),
		'extraParamProp'    : 'entityid'
	}, {
		'title'             : loc.translate(_('Past Sessions')),
		'iconCls'           : 'ico-mod-accesssessionhistory',
		'xtype'             : 'grid_sessions_AccessSessionHistory',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('entity',),
		'extraParamProp'    : 'entityid'
	}))

@view_config(
	route_name='stashes.cl.accounts',
	name='sessions',
	context=Stash,
	renderer='netprofile_sessions:templates/client_sessions.mak',
	permission='USAGE'
)
def client_sessions(ctx, request):
	loc = get_localizer(request)
	page = int(request.params.get('page', 1))
	# FIXME: make per_page configurable
	per_page = 30
	ts_from = request.params.get('from')
	ts_to = request.params.get('to')
	ts_now = dt.datetime.now()
	sess = DBSession()
	ent_ids = tuple()
	cls = AccessSession
	cls_name = _('Active Sessions')
	show_active = True
	entity_name = None
	tsfield = AccessSession.update_timestamp
	if request.matchdict and ('traverse' in request.matchdict):
		tr = request.matchdict.get('traverse')
		if len(tr) > 3:
			eid = int(tr[2])
			ent = sess.query(AccessEntity).get(eid)
			if (not ent) or (ent.stash != ctx):
				raise HTTPForbidden()
			entity_name = ent.nick
			ent_ids = (eid,)
			if tr[3] == 'past':
				cls = AccessSessionHistory
				cls_name = _('Past Sessions')
				show_active = False
				tsfield = AccessSessionHistory.end_timestamp
	if not len(ent_ids):
		ent_ids = [e.id for e in ctx.access_entities]
	if ts_from:
		try:
			ts_from = dparse(ts_from)
		except ValueError:
			ts_from = None
	else:
		ts_from = None
	if ts_to:
		try:
			ts_to = dparse(ts_to)
		except ValueError:
			ts_to = None
	else:
		ts_to = None
	if ts_from is None:
		ts_from = request.session.get('sessions_ts_from')
	if ts_to is None:
		ts_to = request.session.get('sessions_ts_to')
	if ts_from is None:
		ts_from = ts_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
	if ts_to is None:
		ts_to = ts_from\
			.replace(hour=23, minute=59, second=59, microsecond=999999)\
			+ relativedelta(months=1, days=-1)
	request.session['sessions_ts_from'] = ts_from
	request.session['sessions_ts_to'] = ts_to

	total = sess.query(func.count('*')).select_from(cls)\
		.filter(
			cls.entity_id.in_(ent_ids),
			tsfield.between(ts_from, ts_to)
		)\
		.scalar()
	max_page = int(math.ceil(total / per_page))
	if max_page <= 0:
		max_page = 1
	if page <= 0:
		page = 1
	elif page > max_page:
		page = max_page
	sessions = sess.query(cls)\
		.filter(
			cls.entity_id.in_(ent_ids),
			tsfield.between(ts_from, ts_to)
		)\
		.order_by(tsfield.desc())
	if total > per_page:
		sessions = sessions\
			.offset((page - 1) * per_page)\
			.limit(per_page)

	crumbs = [{
		'text' : loc.translate(_st('My Accounts')),
		'url'  : request.route_url('stashes.cl.accounts', traverse=())
	}, {
		'text' : ctx.name,
		'url'  : request.route_url('stashes.cl.accounts', traverse=(ctx.id,))
	}]
	if entity_name:
		crumbs.append({ 'text' : entity_name })
	crumbs.append({ 'text' : loc.translate(cls_name) })
	tpldef = {
		'ts_from'  : ts_from,
		'ts_to'    : ts_to,
		'ename'    : entity_name,
		'active'   : show_active,
		'page'     : page,
		'perpage'  : per_page,
		'maxpage'  : max_page,
		'sessions' : sessions.all(),
		'crumbs'   : crumbs
	}

	request.run_hook('access.cl.tpldef', tpldef, request)
	request.run_hook('access.cl.tpldef.accounts.sessions', tpldef, request)
	return tpldef

