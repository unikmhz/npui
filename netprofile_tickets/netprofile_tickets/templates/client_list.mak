## -*- coding: utf-8 -*-
##
## NetProfile: HTML template for issues list
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
<%block name="title">${_('My Issues')}</%block>

<a role="button" class="btn btn-primary pull-right" href="${req.route_url('tickets.cl.issues', traverse='new')}">
	<span class="glyphicon glyphicon-plus"></span>
	${_('New Issue')}
</a>

<h1>${_('My Issues')}</h1>

% if len(tickets) > 0:
<div class="list-group" role="list">
% for tkt in tickets:
	<a href="${req.route_url('tickets.cl.issues', traverse=(tkt.id, 'view'))}" class="list-group-item" role="listitem" aria-labelledby="${'tkt-%d' % tkt.id}">
		<span class="badge">${tkt.creation_time | n,date_fmt}</span>
		<h4 class="list-group-item-heading" id="${'tkt-%d' % tkt.id}">${tkt.name}</h4>
% if tkt.description:
		<p class="list-group-item-text">${tkt.description}</p>
% endif
	</a>
% endfor
</div>

<a role="button" class="btn btn-primary pull-right" href="${req.route_url('tickets.cl.issues', traverse='new')}">
	<span class="glyphicon glyphicon-plus"></span>
	${_('New Issue')}
</a>
% endif

