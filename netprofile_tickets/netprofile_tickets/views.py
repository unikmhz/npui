#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Tickets module - Views
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

from netprofile import PY3
if PY3:
	from html import escape as html_escape
else:
	from cgi import escape as html_escape

import datetime as dt
from dateutil.parser import parse as dparse

from sqlalchemy.orm import joinedload

from netprofile.ext.wizards import (
	CompositeWizardField,
	ExternalWizardField,
	ExtJSWizardField,
	Step,
	Wizard
)
from netprofile.db.fields import npbool
from netprofile.db.clauses import SetVariable
from netprofile.db.connection import DBSession
from netprofile.ext.data import ExtModel
from netprofile.ext.direct import extdirect_method

from netprofile_core.models import (
	Group,
	User
)

from .models import (
	Ticket,
	TicketChange,
	TicketScheduler,
	TicketState,
	TicketStateTransition,
	TicketTemplate
)

from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)
from netprofile.common.hooks import register_hook
from pyramid.security import has_permission

_ = TranslationStringFactory('netprofile_tickets')

def dpane_tickets(model, request):
	loc = get_localizer(request)
	tabs = [{
		'title'          : loc.translate(_('Update')),
		'iconCls'        : 'ico-ticket-update',
		'xtype'          : 'npwizard',
		'wizardCls'      : 'Ticket',
		'submitApi'      : 'update_ticket',
		'createApi'      : 'get_update_wizard',
		'resetOnClose'   : True,
		'extraParamProp' : 'ticketid'
	}, {
		'title'             : loc.translate(_('Files')),
		'iconCls'           : 'ico-attach',
		'componentCls'      : 'file-attach',
		'xtype'             : 'grid_tickets_TicketFile',
		'stateId'           : None,
		'stateful'          : False,
		'rowEditing'        : False,
		'hideColumns'       : ('ticket',),
		'extraParamProp'    : 'ticketid',
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
		'title'             : loc.translate(_('Dependent')),
		'iconCls'           : 'ico-ticket-related',
		'xtype'             : 'grid_tickets_Ticket',
		'stateId'           : None,
		'stateful'          : False,
		'extraParamProp'    : 'parentid',
		'extraParamRelProp' : 'ticketid',
		'createControllers' : 'NetProfile.tickets.controller.DependentTicket'
	}]
	request.run_hook(
		'core.dpanetabs.%s.%s' % (model.__parent__.moddef, model.name),
		tabs, model, request
	)
	cont = {
		'border' : 0,
		'layout' : {
			'type'    : 'hbox',
			'align'   : 'stretch',
			'padding' : 4
		},
		'items' : [{
			'xtype' : 'npform',
			'flex'  : 2
		}, {
			'xtype' : 'splitter'
		}, {
			'xtype'  : 'tabpanel',
			'flex'   : 3,
			'items'  : tabs
		}]
	}
	request.run_hook(
		'core.dpane.%s.%s' % (model.__parent__.moddef, model.name),
		cont, model, request
	)
	return cont

@register_hook('core.dpanetabs.entities.Entity')
@register_hook('core.dpanetabs.entities.PhysicalEntity')
@register_hook('core.dpanetabs.entities.LegalEntity')
@register_hook('core.dpanetabs.entities.StructuralEntity')
def _dpane_entity_tickets(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Tickets')),
		'iconCls'           : 'ico-mod-ticket',
		'xtype'             : 'grid_tickets_Ticket',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('entity',),
		'extraParamProp'    : 'entityid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

# FIXME: use something more sane?
@register_hook('core.dpanetabs.core.User')
def _dpane_user_sched(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Scheduler')),
		'iconCls'           : 'ico-mod-ticketscheduler',
		'xtype'             : 'grid_tickets_TicketSchedulerUserAssignment',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('user',),
		'extraParamProp'    : 'uid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

# FIXME: use something more sane?
@register_hook('core.dpanetabs.core.Group')
def _dpane_group_sched(tabs, model, req):
	loc = get_localizer(req)
	tabs.append({
		'title'             : loc.translate(_('Scheduler')),
		'iconCls'           : 'ico-mod-ticketscheduler',
		'xtype'             : 'grid_tickets_TicketSchedulerGroupAssignment',
		'stateId'           : None,
		'stateful'          : False,
		'hideColumns'       : ('group',),
		'extraParamProp'    : 'gid',
		'createControllers' : 'NetProfile.core.controller.RelatedWizard'
	})

@register_hook('entities.history.get.all')
@register_hook('entities.history.get.tickets')
def _ent_hist_tickets(hist, ent, req, begin, end, max_num):
	sess = DBSession()

	# TODO: check permissions
	qc = sess.query(TicketChange).options(joinedload(TicketChange.user)).join(Ticket).filter(Ticket.entity == ent)
	qt = sess.query(Ticket).options(joinedload(Ticket.created_by)).filter(Ticket.entity == ent)
	if begin is not None:
		qc = qc.filter(TicketChange.timestamp >= begin)
		qt = qt.filter(Ticket.creation_time >= begin)
	if end is not None:
		qc = qc.filter(TicketChange.timestamp <= end)
		qt = qt.filter(Ticket.creation_time <= end)
	if max_num:
		qc = qc.limit(max_num)
		qt = qt.limit(max_num)
	for tc in qc:
		eh = tc.get_entity_history(req)
		if eh:
			hist.append(eh)
	for tkt in qt:
		eh = tkt.get_entity_history(req)
		if eh:
			hist.append(eh)

@extdirect_method('Ticket', 'get_update_wizard', request_as_last_param=True, permission='TICKETS_UPDATE')
def dyn_ticket_uwiz(params, request):
	tid = int(params['ticketid'])
	sess = DBSession()
	loc = get_localizer(request)
	trans = [{
		'name'       : 'ttrid',
		'boxLabel'   : '<div class="np-xradiolabel"><div class="title">%s</div>%s</div>' % (
			html_escape(loc.translate(_('No changes')), True),
			html_escape(loc.translate(_('Do not change ticket state.')), True)
		),
		'inputValue' : '',
		'checked'    : True
	}]
	ticket = sess.query(Ticket).get(tid)
	if ticket is None:
		raise KeyError('Invalid ticket ID')
	model = ExtModel(Ticket)
	ch_model = ExtModel(TicketChange)
	fields = []
	if has_permission('ENTITIES_LIST', request.context, request):
		fields.append(ExternalWizardField(
			model, 'entity',
			value=ticket.entity,
			extra_config={
				'readOnly' : not bool(has_permission('TICKETS_CHANGE_ENTITY', request.context, request))
			}
		))
	if has_permission('TICKETS_CHANGE_STATE', request.context, request):
		for tr in ticket.state.transitionmap_to:
			label = '<div class="np-xradiolabel"><div class="title">%s</div>%s</div>' % (
				html_escape(tr.name, True),
				html_escape((tr.description if tr.description else ''), True)
			)
			trans.append({
				'name'       : 'ttrid',
				'boxLabel'   : label,
				'inputValue' : tr.id
			})
		fields.append(ExtJSWizardField({
			'xtype'      : 'radiogroup',
			'fieldLabel' : loc.translate(_('Transition')),
			'vertical'   : True,
			'columns'    : 1,
			'items'      : trans
		}))
	if has_permission('TICKETS_CHANGE_FLAGS', request.context, request):
		fields.append(ExternalWizardField(
			model, 'flags',
			value=ticket.flags
		))
	if has_permission('USERS_LIST', request.context, request):
		fields.append(ExternalWizardField(
			model, 'assigned_user',
			value=ticket.assigned_user,
			extra_config={
				'readOnly' : not bool(has_permission('TICKETS_CHANGE_UID', request.context, request))
			}
		))
	if has_permission('GROUPS_LIST', request.context, request):
		fields.append(ExternalWizardField(
			model, 'assigned_group',
			value=ticket.assigned_group,
			extra_config={
				'readOnly' : not bool(has_permission('TICKETS_CHANGE_GID', request.context, request))
			}
		))
	fields.extend((
		ExternalWizardField(
			model, 'ticketid',
			value=ticket.id
		),
		CompositeWizardField(
			ExternalWizardField(
				model, 'assigned_time',
				value=ticket.assigned_time,
				extra_config={
					'readOnly' : not bool(has_permission('TICKETS_CHANGE_DATE', request.context, request))
				}
			),
			ExtJSWizardField({
				'xtype'   : 'button',
				'text'    : 'Schedule',
				'iconCls' : 'ico-schedule',
				'margin'  : '0 0 0 2',
				'itemId'  : 'btn_sched'
			})
		),
		ExternalWizardField(
			model, 'archived',
			value=ticket.archived,
			extra_config={
				'readOnly' : not bool(has_permission('TICKETS_ARCHIVAL', request.context, request))
			}
		),
		ExternalWizardField(ch_model, 'show_client', value=False),
		ExternalWizardField(ch_model, 'comments')
	))
	wiz = Wizard(Step(*fields), title=_('Update ticket'))
	ret = {
		'success' : True,
		'fields'  : wiz.get_cfg(model, request, use_defaults=True)
	}
	return ret

@extdirect_method('Ticket', 'update_ticket', request_as_last_param=True, permission='TICKETS_UPDATE')
def dyn_ticket_uwiz_update(params, request):
	tid = int(params['ticketid'])
	del params['ticketid']
	sess = DBSession()
	model = ExtModel(Ticket)
	ticket = sess.query(Ticket).get(tid)
	if ticket is None:
		raise KeyError('Invalid ticket ID')

	for param in ('tstid', 'toid', 'name', 'descr'):
		if param in params:
			del params[param]

#	TODO: ENTITIES_LIST
	if not has_permission('TICKETS_CHANGE_STATE', request.context, request):
		if 'ttrid' in params:
			del params['ttrid']
	if not has_permission('TICKETS_CHANGE_FLAGS', request.context, request):
		if 'flags' in params:
			del params['flags']
#	TODO: USERS_LIST
#	TODO: GROUPS_LIST

	sess.execute(SetVariable('ticketid', ticket.id))
	if 'ttrid' in params:
		ttr_id = params['ttrid']
		if ttr_id:
			ttr_id = int(ttr_id)
			trans = sess.query(TicketStateTransition).get(ttr_id)
			if trans:
				sess.execute(SetVariable('ttrid', trans.id))
				trans.apply(ticket)
		del params['ttrid']
	if 'show_client' in params:
		show_cl = params['show_client'].lower()
		if show_cl in {'true', '1', 'on'}:
			show_cl = True
		else:
			show_cl = False
		del params['show_client']
	else:
		show_cl = False
	sess.execute(SetVariable('show_client', npbool(show_cl)))
	if 'comments' in params:
		sess.execute(SetVariable('comments', params['comments']))
		del params['comments']
	model.set_values(ticket, params, request)
	sess.flush()
	sess.execute(SetVariable('tcid', None))
	return {
		'success' : True,
		'action'  : {
			'do'     : 'close',
			'redraw' : []
		}
	}

@extdirect_method('Ticket', 'schedule_date', request_as_last_param=True, permission='TICKETS_UPDATE')
def dyn_ticket_sched_find(params, request):
	if 'date' not in params:
		raise ValueError('No date given')
	dur = 0
	tkt = None
	tpl = None
	sess = DBSession()
	if params.get('ticketid'):
		tkt = sess.query(Ticket).get(int(params['ticketid']))
		if not tkt:
			raise KeyError('No matching ticket found')
		dur = tkt.duration
	elif params.get('tstid'):
		tst = sess.query(TicketState).get(int(params['tstid']))
		if not tst:
			raise KeyError('No matching ticket state found')
		dur = tst.duration
	elif params.get('ttplid'):
		tpl = sess.query(TicketTemplate).get(int(params['ttplid']))
		if not tpl:
			raise KeyError('No matching ticket template found')
		dur = tpl.duration
	else:
		raise ValueError('No ticket or ticket state ID given')
	p_dt = dparse(params['date'])
	from_dt = dt.datetime(p_dt.year, p_dt.month, p_dt.day, 0, 0, 0)
	to_dt = dt.datetime(p_dt.year, p_dt.month, p_dt.day, 23, 59, 59)
	sched = []
	if params.get('tschedid'):
		xs = sess.query(TicketScheduler).get(int(params['tschedid']))
		if xs:
			sched.append(xs)
	if params.get('xtschedid'):
		xs = sess.query(TicketScheduler).get(int(params['xtschedid']))
		if xs:
			sched.append(xs)
	if tpl and tpl.scheduler:
		sched.append(tpl.scheduler)
	user = None
	group = None
	numdates = int(params.get('numdates', 5))
	if 'uid' in params:
		user = sess.query(User).get(int(params['uid']))
	elif tpl:
		if tpl.assign_to_self:
			user = request.user
		elif tpl.assign_to_user:
			user = tpl.assign_to_user
	if user and user.schedule_map:
		sched.append(user.schedule_map.scheduler)
	if 'gid' in params:
		group = sess.query(Group).get(int(params['gid']))
	elif tpl:
		if tpl.assign_to_own_group:
			group = request.user.group
		elif tpl.assign_to_group:
			group = tpl.assign_to_group
	if group and group.schedule_map:
		sched.append(group.schedule_map.scheduler)
	dates = TicketScheduler.find_schedule(tkt, sched, from_dt, to_dt, user, group, max_dates=numdates, duration=dur)
	return {
		'success' : True,
		'dates'   : dates
	}

