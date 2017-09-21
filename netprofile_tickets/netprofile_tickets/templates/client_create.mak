## -*- coding: utf-8 -*-
##
## NetProfile: HTML template for issue creation form
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
<%block name="title">${_('New Issue')}</%block>

<h1>${_('New Issue')}</h1>
<p>${_('Please describe your issue in the form below.')}</p>
% if 'csrf' in errors:
<div class="alert alert-warning alert-dismissable">
	<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
	${errors['csrf']}
</div>
% endif

<form method="post" novalidate="novalidate" action="${req.route_url('tickets.cl.issues', traverse='/new')}" id="newtkt-form" class="form-horizontal" role="form">
<fieldset>
	<legend>${_('Issue Details')}</legend>
	<div class="row form-group${' has-warning' if 'name' in errors else ''}">
		<label class="col-sm-4 control-label" for="name">${_('Title')}</label>
		<div class="controls col-sm-8">
			<input
				type="text"
				class="form-control"
				required="required"
				id="name"
				name="name"
				title="${_('Enter a short issue description')}"
				placeholder="${_('Enter a short issue description')}"
				value=""
				size="30"
				maxlength="254"
				tabindex="1"
				data-validation-required-message="${_('This field is required', domain='netprofile_access')}"
				data-validation-maxlength-message="${_('This field is too long', domain='netprofile_access')}"
			/>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'name' in errors:
				<li>${errors['name']}</li>
% endif
			</ul></div>
		</div>
	</div>
	<div class="row form-group${' has-warning' if 'state' in errors else ''}">
		<label class="col-sm-4 control-label">${_('Type')}</label>
		<div class="controls col-sm-8">
<% num_st = 0 %>\
% for state in states:
<% num_st += 1 %>\
			<label title="${state.title}" class="radio inline" for="state-${state.id}"><input
				type="radio"
				required="required"
				id="state-${state.id}"
				name="state"
				title="${_('Choose your issue type')}"
				value="${state.id}"
				tabindex="${str(loop.index + 2)}"
			/> ${state.title}</label>
% endfor
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'state' in errors:
				<li>${errors['state']}</li>
% endif
			</ul></div>
		</div>
	</div>
	<div class="row form-group${' has-warning' if 'descr' in errors else ''}">
		<label class="col-sm-4 control-label" for="descr">${_('Description')}</label>
		<div class="controls col-sm-8">
			<textarea
				class="form-control"
				id="descr"
				name="descr"
				title="${_('Enter an optional longer issue description')}"
				placeholder="${_('Enter an optional longer issue description')}"
				tabindex="${str(num_st + 2)}"
			/></textarea>
			<div class="help-block"><ul role="alert">
% if 'descr' in errors:
				<li>${errors['descr']}</li>
% endif
			</ul></div>
		</div>
	</div>
	<div class="row form-group">
		<label class="col-sm-4 control-label" for="subscribe">${_('Send me updates')}</label>
		<div class="controls col-sm-8">
			<div class="checkbox">
				<input
					type="checkbox"
					id="subscribe"
					name="subscribe"
					title="${_('Notify me when this issue has updates')}"
					value="true"
					checked="checked"
					tabindex="${str(num_st + 3)}"
				/></div>
		</div>
	</div>
</fieldset>
<div class="form-actions row">
	<p class="col-sm-4 legend"><span class="req">*</span> ${_('Fields marked with this symbol are required.', domain='netprofile_access')}</p>
	<div class="controls col-sm-8">
		<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
		<button type="submit" class="btn btn-primary btn-large" id="submit" name="submit" title="${_('Add New Issue')}" tabindex="${str(num_st + 4)}">
			<span class="glyphicon glyphicon-plus"></span>
			${_('Add New Issue')}
		</button>
	</div>
</div>
</form>

