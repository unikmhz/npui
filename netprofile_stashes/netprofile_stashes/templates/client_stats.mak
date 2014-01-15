## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_layout.mak"/>
% for stash in req.user.parent.stashes:
% if int(stash_id) == 0 or stash.id == int(stash_id):
<div class="panel panel-default">
 	<div class="panel-heading">${stash.name}<a href="#" class="btn btn-default pull-right btn-xs">${_('Apply Filter')}</a></div>
	<table class="table">
		<tr>
			<th style="width: 30%">${_('Date')}</th>
		    <th style="width: 10%;">${_('Direction')}</th>
		    <th style="width: 20%">${_('Amount')}</th>
		    <th style="width: 40%">${_('Type')}</th>
		</tr>
		<tbody>
		% for io in stash.ios:
			<tr 
				% if io.type.type == '\'in\'':
					style="danger"
				% elif io.type.type == '\'out\'':
					style="success"
				% endif
			>
				<td>${io.timestamp}</td>
				<td>${io.type.type}</td>
				<td>${round(io.difference, 2)}</td>
				<td>${io.type}</td>
			</tr>
		% endfor
		</tbody>
	</table>
</div>
% endif
% endfor

