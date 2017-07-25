## -*- coding: utf-8 -*-
##
## NetProfile: HTML template for issue information
## Copyright © 2014-2017 Alex Unigovsky
##
## This file is part of NetProfile.
## NetProfile is free software: you can redistribute it and/or
## modify it under the terms of the GNU Affero General Public
## License as published by the Free Software Foundation, either
## version 3 of the License, or (at your option) any later
## version.
##
## NetProfile is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General
## Public License along with NetProfile. If not, see
## <http://www.gnu.org/licenses/>.
##
<%inherit file="netprofile_access:templates/client_layout.mak"/>\
<%namespace module="netprofile.tpl.filters" import="date_fmt" />\
<%block name="title">${_('View Issue #%d') % ticket.id}</%block>

% if not ticket.archived:
<div class="btn-group pull-right">
<a role="button" class="btn btn-primary" href="${req.route_url('tickets.cl.issues', traverse=(ticket.id, 'append'))}" title="${_('Add your comment to issue')}">
	<span class="glyphicon glyphicon-pencil"></span>
	${_('Append Comment')}
</a>
</div>
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

<ul class="nav nav-tabs">
	<li class="active"><a href="#tab-changes" data-toggle="tab">${_('History')}</a></li>
	<li><a href="#tab-files" data-toggle="tab">${_('Files')}</a></li>
</ul>
<div class="tab-content">
<div class="tab-pane fade in active" id="tab-changes">
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
% endif
% if not ticket.archived:
	<div class="btn-group pull-right">
	<a role="button" class="btn btn-primary" href="${req.route_url('tickets.cl.issues', traverse=(ticket.id, 'append'))}" title="${_('Add your comment to issue')}">
		<span class="glyphicon glyphicon-pencil"></span>
		${_('Append Comment')}
	</a>
</div>
% endif
</div>
<div class="tab-pane fade" id="tab-files">
	<h3>${_('Attached Files')}</h3>
	<form id="fileupload" class="file-upload" action="${req.route_url('access.cl.upload')}" method="post" enctype="multipart/form-data">
	<div class="row fileupload-buttonbar">
		<div class="col-lg-7">
			<input type="hidden" id="mode" name="mode" value="ticket" />
			<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
			<input type="hidden" id="ticketid" name="ticketid" value="${ticket.id}" />
			<span class="btn btn-success fileinput-button" title="${_('Attach a file to issue')}">
				<span class="glyphicon glyphicon-plus"></span>
				${_('Attach File')}
				<input type="file" name="files" multiple="multiple" capture="capture" />
			</span>
			<button type="submit" class="btn btn-primary start" title="${_('Start file upload')}">
				<span class="glyphicon glyphicon-upload"></span>
				${_('Start Upload')}
			</button>
			<button type="reset" class="btn btn-warning cancel" title="${_('Cancel upload in progress')}">
				<span class="glyphicon glyphicon-ban-circle"></span>
				${_('Cancel Upload')}
			</button>
			<button type="button" class="btn btn-danger delete" title="${_('Remove already added files')}">
				<span class="glyphicon glyphicon-trash"></span>
				${_('Delete')}
			</button>
			<input type="checkbox" class="toggle" />
			<span class="fileupload-process"></span>
		</div>
		<div class="col-lg-5 fileupload-progress fade">
			<div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100">
				<div class="progress-bar progress-bar-success" style="width:0%;"></div>
			</div>
			<div class="progress-extended">&nbsp;</div>
		</div>
	</div>
	<table role="presentation" class="table table-striped"><tbody class="files"></tbody></table>
	</form>
</div>
</div>

