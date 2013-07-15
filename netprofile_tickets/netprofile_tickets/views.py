#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from netprofile.ext.wizards import (
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

from .models import (
	Ticket,
	TicketChange,
	TicketStateTransition
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
def _dpane_ticket_order(tabs, model, req):
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
		ExternalWizardField(
			model, 'assigned_time',
			value=ticket.assigned_time,
			extra_config={
				'readOnly' : not bool(has_permission('TICKETS_CHANGE_DATE', request.context, request))
			}
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

#	ENTITIES_LIST
	if not has_permission('TICKETS_CHANGE_STATE', request.context, request):
		if 'ttrid' in params:
			del params['ttrid']
	if not has_permission('TICKETS_CHANGE_FLAGS', request.context, request):
		if 'flags' in params:
			del params['flags']
#	USERS_LIST
#	GROUPS_LIST

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

