## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>\
<%namespace module="netprofile.tpl.filters" import="date_fmt, date_fmt_short, bytes_fmt" />\
<%block name="title">
% if active:
	${_('Active Sessions', domain='netprofile_sessions')}
% else:
	${_('Past Sessions', domain='netprofile_sessions')}
% endif
</%block>

<h1>
% if active:
	${_('Active Sessions', domain='netprofile_sessions')}
% else:
	${_('Past Sessions', domain='netprofile_sessions')}
% endif
% if ename:
	<small class="single-line" title="${_('User Name', domain='netprofile_sessions')}">${ename}</small>
% endif
</h1>

<div class="panel panel-default">
	<div class="panel-heading clearfix">
	<form method="post" novalidate="novalidate" action="" id="sessions-form" class="form-inline" role="form">
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

% if len(sessions) > 0:
	<div class="table-responsive">
	<table class="table table-striped">
	<thead>
		<tr>
			<th>${_('From')}</th>
			<th>${_('Till')}</th>
			<th>${_('Client', domain='netprofile_sessions')}</th>
			<th>${_('Address', domain='netprofile_sessions')}</th>
			<th>${_('In', domain='netprofile_sessions')}</th>
			<th>${_('Out', domain='netprofile_sessions')}</th>
		</tr>
	</thead>
	<tbody>
% for s in sessions:
		<tr>
			<td>${s.start_timestamp | n,date_fmt_short}</td>
% if active:
			<td>${s.update_timestamp | n,date_fmt_short}</td>
% else:
			<td>${s.end_timestamp | n,date_fmt_short}</td>
% endif
			<td>${s.calling_station_id}</td>
			<td>
% if s.ipv4_address:
				${s.ipv4_address}
% endif
% if s.ipv6_address:
				${s.ipv6_address}
% endif
			</td>
			<td><span title="${s.used_ingress_traffic}">${s.used_ingress_traffic | n,bytes_fmt}</span></td>
			<td><span title="${s.used_egress_traffic}">${s.used_egress_traffic | n,bytes_fmt}</span></td>
		</tr>
		% endfor
	</tbody>
	</table>
	</div>
% else:
	<div class="panel-body text-center">${_('No sessions were found.', domain='netprofile_sessions')}</div>
% endif
% if maxpage > 1:
	<div class="panel-footer">
		<ul class="pagination pagination-sm" style="margin-top: 0.1em; margin-bottom: 0.1em;">
% if page == 1:
			<li class="disabled"><span>&laquo;</span></li>
% else:
			<li><a href="${req.current_route_url(_query={'page' : (page - 1)})}">&laquo;</a></li>
% endif
% for pg in range(min(max(page - 2, 1), 1 if maxpage < 5 else maxpage - 4), max(min(page + 2, maxpage), 5 if maxpage > 5 else maxpage) + 1):
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

