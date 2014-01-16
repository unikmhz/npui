## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>\
<%namespace module="netprofile.tpl.filters" import="date_fmt" />\
<%block name="title">${_('View Issue #%d') % ticket.id}</%block>

% if not ticket.archived:
<a role="button" class="btn btn-primary pull-right" href="${req.route_url('tickets.cl.issues', traverse=(ticket.id, 'append'))}" title="${_('Add your comment to issue')}">
	<span class="glyphicon glyphicon-pencil"></span>
	${_('Append Comment')}
</a>
% endif

<h1>${ticket.name} <small class="single-line">${_('ID: %d') % ticket.id}</small></h1>

<div class="row">
	<p class="col-sm-3">${_('Filed:')}</p>
	<p class="col-sm-9">${ticket.creation_time | n,date_fmt}</p>
</div>
% if ticket.assigned_time:
<div class="row">
	<p class="col-sm-3">${_('Assigned:')}</p>
	<p class="col-sm-9">${ticket.assigned_time | n,date_fmt}</p>
</div>
% endif
<div class="row">
	<p class="col-sm-3">${_('State:')}</p>
	<p class="col-sm-9">
		${str(ticket.state)}
% if ticket.archived:
		<span class="label label-danger">${_('In Archive')}</span>
% endif
	</p>
</div>

% if ticket.description:
<p>${ticket.description}</p>
% endif

% if len([x for x in ticket.changes if x.show_client and (x.transition or x.comments)]) > 0:
<h3>${_('Issue History')}</h3>
<ul class="list-group">
% for ch in sorted(ticket.changes, reverse=True, key=lambda x: x.timestamp):
% if ch.show_client and (ch.transition or ch.comments):
	<li class="list-group-item">
		<span class="badge">${ch.timestamp | n,date_fmt}</span>
% if ch.transition:
		<span class="badge">${str(ch.transition)}</span>
% endif
% if ch.user:
		<h4 class="list-group-item-heading">${_('Change by %s') % str(ch.user)}</h4>
% elif ch.from_client:
		<h4 class="list-group-item-heading">${_('My Comment')}</h4>
% endif
% if ch.comments:
		<p class="list-group-item-text" style="clear: right;">${ch.comments}</p>
% else:
		<p class="list-group-item-text" style="clear: right;">${_('No additional comments.')}</p>
% endif
	</li>
% endif
% endfor
</ul>

% if not ticket.archived:
<a role="button" class="btn btn-primary pull-right" href="${req.route_url('tickets.cl.issues', traverse=(ticket.id, 'append'))}" title="${_('Add your comment to issue')}">
	<span class="glyphicon glyphicon-pencil"></span>
	${_('Append Comment')}
</a>
% endif
% endif

