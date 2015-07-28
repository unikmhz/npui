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

import collections
import datetime as dt
from dateutil.parser import parse as dparse

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from netprofile.ext.wizards import (
	CompositeWizardField,
	ExternalWizardField,
	ExtJSWizardField,
	Step,
	Wizard
)
from netprofile.common.factory import RootFactory
from netprofile.db.fields import npbool
from netprofile.db.clauses import (
	IntervalSeconds,
	SetVariable
)
from netprofile.db.connection import DBSession
from netprofile.ext.data import ExtModel
from netprofile.ext.direct import extdirect_method

from netprofile_core.models import (
	Group,
	User
)
from netprofile_core.views import generate_calendar

from .models import (
	Ticket,
	TicketChange,
	TicketFile,
	TicketScheduler,
	TicketState,
	TicketStateTransition,
	TicketTemplate
)

from pyramid.view import view_config
from pyramid.settings import asbool
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)
from netprofile.common.hooks import register_hook
from pyramid.security import has_permission
from pyramid.httpexceptions import (
	HTTPForbidden,
	HTTPSeeOther
)

_ = TranslationStringFactory('netprofile_tickets')
_a = TranslationStringFactory('netprofile_access')

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
			'padding' : 0
		},
		'items' : [{
			'xtype'   : 'npform',
			'flex'    : 2,
			'padding' : '4 0 4 4'
		}, {
			'xtype'   : 'splitter'
		}, {
			'xtype'   : 'tabpanel',
			'cls'     : 'np-subtab',
			'border'  : False,
			'flex'    : 3,
			'items'   : tabs
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
		ExternalWizardField(ch_model, 'show_client', value=False)
	))
	if has_permission('TICKETS_COMMENT', request.context, request):
		fields.append(ExternalWizardField(ch_model, 'comments'))
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
	if ('comments' in params) and has_permission('TICKETS_COMMENT', request.context, request):
		sess.execute(SetVariable('comments', params['comments']))
		del params['comments']
	else:
		sess.execute(SetVariable('comments', None))
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

_cal = generate_calendar(_('Tickets'), 22)
_cal['cancreate'] = False

@register_hook('core.calendar.calendars.read')
def _cal_calendars(cals, params, req):
	if not has_permission('TICKETS_LIST', req.context, req):
		return
	cals.append(_cal)

@register_hook('core.calendar.events.read')
def _cal_events(evts, params, req):
	if not has_permission('TICKETS_LIST', req.context, req):
		return
	# TODO: fancy permissions/ACLs
	ts_from = params.get('startDate')
	ts_to = params.get('endDate')
	if (not ts_from) or (not ts_to):
		return
	cals = params.get('cals')
	if cals:
		if isinstance(cals, collections.Iterable):
			if _cal['id'] not in cals:
				return
		else:
			return
	ts_from = dparse(ts_from).replace(hour=0, minute=0, second=0, microsecond=0)
	ts_to = dparse(ts_to).replace(hour=23, minute=59, second=59, microsecond=999999)
	sess = DBSession()
	q = sess.query(Ticket)\
		.filter(
			Ticket.assigned_time <= ts_to,
			IntervalSeconds(Ticket.assigned_time, Ticket.duration) >= ts_from
		)
	for tkt in q:
		ev = {
			'id'       : 'ticket-%d' % tkt.id,
			'cid'      : _cal['id'],
			'title'    : tkt.name,
			'start'    : tkt.assigned_time,
			'end'      : tkt.end_time,
			'notes'    : tkt.description,
			'apim'     : 'tickets',
			'apic'     : 'Ticket',
			'apiid'    : tkt.id,
			'caned'    : False
		}
		evts.append(ev)

@register_hook('core.calendar.events.update')
def _cal_events_update(params, req):
	if 'EventId' not in params:
		return
	evtype, evid = params['EventId'].split('-')
	if evtype != 'ticket':
		return
	evid = int(evid)
	if not has_permission('TICKETS_UPDATE', req.context, req):
		return
	# TODO: fancy permissions/ACLs
	sess = DBSession()
	tkt = sess.query(Ticket).get(evid)
	if tkt is None:
		return
	sess.execute(SetVariable('ticketid', tkt.id))
	if 'StartDate' in params:
		new_ts = dparse(params['StartDate']).replace(tzinfo=None, microsecond=0)
		if new_ts:
			tkt.assigned_time = new_ts
	if ('EndDate' in params) and tkt.assigned_time:
		new_ts = dparse(params['EndDate']).replace(tzinfo=None, microsecond=0)
		if new_ts:
			delta = new_ts - tkt.assigned_time
			tkt.duration = delta.seconds

class ClientRootFactory(RootFactory):
	def __getitem__(self, name):
		if not self.req.user:
			raise KeyError('Not logged in')
		try:
			name = int(name, base=10)
			ent = self.req.user.parent
			sess = DBSession()
			try:
				tkt = sess.query(Ticket).filter(
					Ticket.entity == ent,
					Ticket.id == name,
					Ticket.show_client == True
				).one()
				tkt.__parent__ = self
				tkt.__name__ = str(name)
				return tkt
			except NoResultFound:
				raise KeyError('Invalid ticket ID')
		except (TypeError, ValueError):
			pass
		raise KeyError('Invalid URL')

@register_hook('access.cl.menu')
def _tickets_menu(menu, req):
	cfg = req.registry.settings
	if asbool(cfg.get('netprofile.client.ticket.enabled', True)):
		menu.append({
			'route' : 'tickets.cl.issues',
			'text'  : _('Issues')
		})

@register_hook('access.cl.upload')
def _tickets_upload_file(obj, mode, req, sess, tpldef):
	if mode != 'ticket':
		return False
	try:
		ticket_id = int(req.POST.get('ticketid', ''))
	except (TypeError, ValueError):
		return False
	tkt = sess.query(Ticket).get(ticket_id)
	if not tkt:
		return False
	ent = req.user.parent
	if tkt.archived or (tkt.entity != ent):
		return False
	link = TicketFile()
	link.file = obj
	link.ticket = tkt
	sess.add(link)
	sess.flush()
	url = req.route_url('access.cl.download', mode='ticket', id=link.id)
	tpldef.append({
		'name'       : obj.filename,
		'size'       : obj.size,
		'url'        : url,
		'deleteUrl'  : url,
		'deleteType' : 'DELETE'
	})
	return True

@register_hook('access.cl.file_list')
def _tickets_list_files(mode, req, sess, tpldef):
	if mode != 'ticket':
		return False
	try:
		ticket_id = int(req.GET.get('ticketid', ''))
	except (TypeError, ValueError):
		return False
	tkt = sess.query(Ticket).get(ticket_id)
	if not tkt:
		return False
	ent = req.user.parent
	if tkt.entity != ent:
		return False
	for link in tkt.filemap:
		url = req.route_url('access.cl.download', mode='ticket', id=link.id)
		tpldef.append({
			'name'       : link.file.filename,
			'size'       : link.file.size,
			'url'        : url,
			'deleteUrl'  : url,
			'deleteType' : 'DELETE'
		})

@register_hook('access.cl.download')
def _tickets_download_file(mode, objid, req, sess):
	if mode != 'ticket':
		return False
	link = sess.query(TicketFile).get(objid)
	if not link:
		return False
	if link.ticket.archived and (req.method == 'DELETE'):
		return False
	ent = req.user.parent
	if link.ticket.entity != ent:
		return False
	return link.file

@view_config(
	route_name='tickets.cl.issues',
	name='',
	context=ClientRootFactory,
	permission='USAGE',
	renderer='netprofile_tickets:templates/client_list.mak'
)
def client_issue_list(ctx, req):
	cfg = req.registry.settings
	if not asbool(cfg.get('netprofile.client.ticket.enabled', True)):
		raise HTTPForbidden(detail=_('Issues view is disabled'))
	sess = DBSession()
	ent = req.user.parent
	q = sess.query(Ticket)\
		.filter(Ticket.entity == ent, Ticket.show_client == True)\
		.order_by(Ticket.creation_time.desc())
	tpldef = {
		'sess'    : DBSession(),
		'tickets' : q.all()
	}
	req.run_hook('access.cl.tpldef', tpldef, req)
	req.run_hook('access.cl.tpldef.issue.list', tpldef, req)
	return tpldef

@view_config(
	route_name='tickets.cl.issues',
	name='new',
	context=ClientRootFactory,
	permission='USAGE',
	renderer='netprofile_tickets:templates/client_create.mak'
)
def client_issue_new(ctx, req):
	loc = get_localizer(req)
	cfg = req.registry.settings
	if not asbool(cfg.get('netprofile.client.ticket.enabled', True)):
		raise HTTPForbidden(detail=_('Issues view is disabled'))
	origin_id = int(cfg.get('netprofile.client.ticket.origin_id', 0))
	user_id = int(cfg.get('netprofile.client.ticket.assign_uid', 0))
	group_id = int(cfg.get('netprofile.client.ticket.assign_gid', 0))
	errors = {}
	sess = DBSession()
	ent = req.user.parent
	states = sess.query(TicketState)\
		.filter(TicketState.is_start == True, TicketState.allow_client == True)
	if 'submit' in req.POST:
		csrf = req.POST.get('csrf', '')
		name = req.POST.get('name', '')
		descr = req.POST.get('descr', '')
		state = int(req.POST.get('state', 0))
		if csrf != req.get_csrf():
			errors['csrf'] = _a('Error submitting form')
		else:
			l = len(name)
			if (l == 0) or (l > 254):
				errors['name'] = _a('Invalid field length')
			for s in states:
				if s.id == state:
					state = s
					break
			else:
				errors['state'] = _('Invalid issue type')
		if len(errors) == 0:
			tkt = Ticket()
			tkt.name = name
			tkt.state = state
			tkt.entity = ent
			tkt.show_client = True
			if descr:
				tkt.description = descr
			if origin_id:
				tkt.origin_id = origin_id
			if user_id:
				tkt.assigned_user_id = user_id
			if group_id:
				tkt.assigned_group_id = group_id
			sess.add(tkt)
			sess.flush()

			req.session.flash({
				'text' : loc.translate(_('New issue successfully created'))
			})
			return HTTPSeeOther(location=req.route_url('tickets.cl.issues', traverse=(tkt.id, 'view')))
	tpldef = {
		'states' : states,
		'crumbs' : [{
			'text' : loc.translate(_('My Issues')),
			'url'  : req.route_url('tickets.cl.issues', traverse=())
		}, {
			'text' : loc.translate(_('New Issue'))
		}],
		'errors' : {err: loc.translate(errors[err]) for err in errors}
	}
	req.run_hook('access.cl.tpldef', tpldef, req)
	req.run_hook('access.cl.tpldef.issue.new', tpldef, req)
	return tpldef

@view_config(
	route_name='tickets.cl.issues',
	name='append',
	context=Ticket,
	permission='USAGE',
	renderer='netprofile_tickets:templates/client_append.mak'
)
def client_issue_append(ctx, req):
	loc = get_localizer(req)
	cfg = req.registry.settings
	if not asbool(cfg.get('netprofile.client.ticket.enabled', True)):
		raise HTTPForbidden(detail=_('Issues view is disabled'))
	errors = {}
	if ctx.archived:
		req.session.flash({
			'class' : 'danger',
			'text'  : loc.translate(_('This ticket is archived. You can\'t append to it.'))
		})
		return HTTPSeeOther(location=req.route_url('tickets.cl.issues', traverse=(ctx.id, 'view')))
	if 'submit' in req.POST:
		csrf = req.POST.get('csrf', '')
		comments = req.POST.get('comments', '')
		if csrf != req.get_csrf():
			errors['csrf'] = _a('Error submitting form')
		elif not comments:
			errors['comments'] = _a('Invalid field length')
		if len(errors) == 0:
			sess = DBSession()
			ch = TicketChange()
			ch.ticket = ctx
			ch.from_client = True
			ch.show_client = True
			ch.comments = comments
			sess.add(ch)

			req.session.flash({
				'text' : loc.translate(_('Your comment was successfully appended to the issue'))
			})
			return HTTPSeeOther(location=req.route_url('tickets.cl.issues', traverse=(ctx.id, 'view')))
	tpldef = {
		'crumbs' : [{
			'text' : loc.translate(_('My Issues')),
			'url'  : req.route_url('tickets.cl.issues', traverse=())
		}, {
			'text' : loc.translate(_('View Issue #%d')) % ctx.id,
			'url'  : req.route_url('tickets.cl.issues', traverse=(ctx.id, 'view'))
		}, {
			'text' : loc.translate(_('Append Comment to Issue #%d')) % ctx.id
		}],
		'ticket' : ctx,
		'errors' : {err: loc.translate(errors[err]) for err in errors}
	}
	req.run_hook('access.cl.tpldef', tpldef, req)
	req.run_hook('access.cl.tpldef.issue.append', tpldef, req)
	return tpldef

@view_config(
	route_name='tickets.cl.issues',
	name='',
	context=Ticket,
	permission='USAGE',
	renderer='netprofile_tickets:templates/client_view.mak'
)
@view_config(
	route_name='tickets.cl.issues',
	name='view',
	context=Ticket,
	permission='USAGE',
	renderer='netprofile_tickets:templates/client_view.mak'
)
def client_issue_view(ctx, req):
	loc = get_localizer(req)
	cfg = req.registry.settings
	if not asbool(cfg.get('netprofile.client.ticket.enabled', True)):
		raise HTTPForbidden(detail=_('Issues view is disabled'))
	tpldef = {
		'crumbs' : [{
			'text' : loc.translate(_('My Issues')),
			'url'  : req.route_url('tickets.cl.issues', traverse=())
		}, {
			'text' : loc.translate(_('View Issue #%d')) % ctx.id
		}],
		'trans'  : (
			_('Begin'),
			_('Cancel'),
			_('Delete'),
			_('Error'),
			_('Processing…')
		),
		'ticket' : ctx
	}
	req.run_hook('access.cl.tpldef', tpldef, req)
	req.run_hook('access.cl.tpldef.issue.view', tpldef, req)
	return tpldef

