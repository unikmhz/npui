## -*- coding: utf-8 -*-
<%!

from netprofile_stashes.models import IOOperationType

%>\
<%inherit file="netprofile_access:templates/client_layout.mak"/>\
<%namespace module="netprofile.tpl.filters" import="date_fmt, date_fmt_short, curr_fmt" />\
<%block name="title">${_('Account Operations')}</%block>

<h1>
	${_('Account Operations')}
% if sname:
	<small class="single-line" title="${_('Account Name')}">${sname}</small>
% endif
</h1>

<div class="panel panel-default">
	<div class="panel-heading clearfix">
	<form method="post" novalidate="novalidate" action="" id="ops-form" class="form-inline" role="form">
		<div class="form-group" style="max-width: 20em;">
			<label class="sr-only" for="from">${_('From')}</label>
			<div class="input-group date dt-picker" id="dp-from" data-dp-hidden="from-val" data-dp-start="dp-to">
				<input
					type="text"
					class="form-control"
					id="from"
					title="${_('Enter starting date of the range')}"
					placeholder="${_('From')}"
					value="${ts_from | n,date_fmt_short}"
					size="26"
					tabindex="1"
				/>
				<input type="hidden" id="from-val" name="from" value="${ts_from.isoformat()}" />
				<span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span></span>
			</div>
		</div>
		<div class="form-group" style="max-width: 20em;">
			<label class="sr-only" for="to">${_('Till')}</label>
			<div class="input-group date dt-picker" id="dp-to" data-dp-hidden="to-val" data-dp-end="dp-from">
				<input
					type="text"
					class="form-control"
					id="to"
					title="${_('Enter ending date of the range')}"
					placeholder="${_('Till')}"
					value="${ts_to | n,date_fmt_short}"
					size="26"
					tabindex="2"
				/>
				<input type="hidden" id="to-val" name="to" value="${ts_to.isoformat()}" />
				<span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span></span>
			</div>
		</div>
		<div class="form-group pull-right">
			<button type="submit" class="btn btn-default" id="submit" name="submit" title="${_('Change filter')}" tabindex="10">
				<span class="glyphicon glyphicon-filter"></span>
				${_('Filter')}
			</button>
		</div>
	</form>
	</div>

% if len(ios) > 0:
	<div class="table-responsive">
	<table class="table table-striped">
	<thead>
		<tr>
			<th style>${_('Date')}</th>
			<th style>${_('Sum')}</th>
			<th style>${_('Type')}</th>
		</tr>
	</thead>
	<tbody>
% for io in ios:
		<tr\
% if io.type.type == IOOperationType.incoming:
 class="success"\
% elif io.type.type == IOOperationType.outgoing:
 class="warning"\
% endif
>
			<td>${io.timestamp | n,date_fmt_short}</td>
			<td>${io.difference | n,curr_fmt}</td>
			<td>${io.type}</td>
		</tr>
		% endfor
	</tbody>
	</table>
	</div>
% else:
	<div class="panel-body text-center">${_('No operations were found.')}</div>
% endif
% if maxpage > 1:
	<div class="panel-footer">
		<ul class="pagination pagination-sm" style="margin-top: 0.1em; margin-bottom: 0.1em;">
% if page == 1:
			<li class="disabled"><span>&laquo;</span></li>
% else:
			<li><a href="${req.current_route_url(_query={'page' : (page - 1)})}">&laquo;</a></li>
% endif
% for pg in range(min(max(page - 2, 1), maxpage - 4), max(min(page + 2, maxpage), 5) + 1):
% if pg == page:
			<li class="active"><span>${pg}<span class="sr-only"> ${_('(current)')}</span></span></li>
% else:
			<li><a href="${req.current_route_url(_query={'page' : pg})}">${pg}</a></li>
% endif
% endfor
% if page == maxpage:
			<li class="disabled"><span>&raquo;</span></li>
% else:
			<li><a href="${req.current_route_url(_query={'page' : (page + 1)})}">&raquo;</a></li>
% endif
		</ul>
	</div>
% endif
</div>

