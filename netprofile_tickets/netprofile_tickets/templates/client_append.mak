## -*- coding: utf-8 -*-
##
## NetProfile: HTML template for issue comment form
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
<%block name="title">${_('Append Comment to Issue #%d') % ticket.id}</%block>

<h1>${_('Add Comment to Issue')} <small class="single-line">${_('ID: %d') % ticket.id}</small></h1>

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
	<p class="col-sm-9">${str(ticket.state)}</p>
</div>

% if ticket.description:
<p>${ticket.description}</p>
% endif

% if 'csrf' in errors:
<div class="alert alert-warning alert-dismissable">
	<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
	${errors['csrf']}
</div>
% endif

<form method="post" novalidate="novalidate" action="${req.route_url('tickets.cl.issues', traverse=(ticket.id, 'append'))}" id="tktappend-form" class="form-horizontal" role="form">
<fieldset>
	<legend>${_('New Comment')}</legend>
	<div class="row form-group${' has-warning' if 'comments' in errors else ''}">
		<label class="col-sm-4 control-label" for="comments">${_('Text')}</label>
		<div class="controls col-sm-8">
			<textarea
				class="form-control"
				required="required"
				id="comments"
				name="comments"
				title="${_('Enter your additional comment text')}"
				placeholder="${_('Enter your additional comment text')}"
				tabindex="1"
				data-validation-required-message="${_('This field is required', domain='netprofile_access')}"
			/></textarea>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'comments' in errors:
				<li>${errors['comments']}</li>
% endif
			</ul></div>
		</div>
	</div>
</fieldset>
<div class="form-actions row">
	<p class="col-sm-4 legend"><span class="req">*</span> ${_('Fields marked with this symbol are required.', domain='netprofile_access')}</p>
	<div class="controls col-sm-8">
		<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
		<button type="submit" class="btn btn-primary btn-large" id="submit" name="submit" title="${_('Add your comment to issue')}" tabindex="10">
			<span class="glyphicon glyphicon-pencil"></span>
			${_('Append Comment')}
		</button>
	</div>
</div>
</form>

