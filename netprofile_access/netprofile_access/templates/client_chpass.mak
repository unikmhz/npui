## -*- coding: utf-8 -*-
##
## NetProfile: HTML template for password change form
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
<%inherit file="netprofile_access:templates/client_layout.mak"/>
<%block name="title">${_('Change Password')}</%block>

<h1>${_('Password Change Form')}</h1>
% if 'csrf' in errors:
<div class="alert alert-warning alert-dismissable">
	<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
	${errors['csrf']}
</div>
% endif

<form method="post" novalidate="novalidate" action="${req.route_url('access.cl.chpass')}" id="chpass-form" class="form-horizontal" role="form">
<fieldset>
	<legend>${_('Account Settings')}</legend>
	<div class="row form-group${' has-warning' if 'oldpass' in errors else ''}">
		<label class="col-sm-4 control-label" for="oldpass">${_('Old Password')}</label>
		<div class="controls col-sm-8">
			<input
				type="password"
				class="form-control"
				required="required"
				id="oldpass"
				name="oldpass"
				title="${_('Enter your old password')}"
				placeholder="${_('Enter your old password')}"
				value=""
				size="30"
				maxlength="254"
				tabindex="2"
				data-validation-required-message="${_('This field is required')}"
				data-validation-maxlength-message="${_('This field is too long')}"
			/>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'oldpass' in errors:
				<li>${errors['oldpass']}</li>
% endif
			</ul></div>
		</div>
	</div>
</fieldset>
<fieldset>
	<legend>${_('New Password')}</legend>
	<div class="row form-group${' has-warning' if 'pass' in errors else ''}">
		<label class="col-sm-4 control-label" for="pass">${_('New Password')}</label>
		<div class="controls col-sm-8">
			<input
				type="password"
				class="form-control"
				required="required"
				id="pass"
				name="pass"
				title="${_('Enter your new desired password')}"
				placeholder="${_('Enter your new desired password')}"
				value=""
				size="30"
				minlength="${str(min_pwd_len)}"
				maxlength="254"
				tabindex="2"
				data-validation-required-message="${_('This field is required')}"
				data-validation-minlength-message="${_('This field is too short')}"
				data-validation-maxlength-message="${_('This field is too long')}"
			/>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'pass' in errors:
				<li>${errors['pass']}</li>
% endif
			</ul></div>
		</div>
	</div>
	<div class="row form-group${' has-warning' if 'pass2' in errors else ''}">
		<label class="col-sm-4 control-label" for="pass2">${_('Repeat Password')}</label>
		<div class="controls col-sm-8">
			<input
				type="password"
				class="form-control"
				required="required"
				id="pass2"
				name="pass2"
				title="${_('Repeat previously entered password')}"
				placeholder="${_('Repeat previously entered password')}"
				value=""
				size="30"
				minlength="${str(min_pwd_len)}"
				maxlength="254"
				tabindex="3"
				data-validation-match-match="pass"
				data-validation-required-message="${_('This field is required')}"
				data-validation-minlength-message="${_('This field is too short')}"
				data-validation-maxlength-message="${_('This field is too long')}"
				data-validation-match-message="${_('Passwords must match')}"
			/>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'pass2' in errors:
				<li>${errors['pass2']}</li>
% endif
			</ul></div>
		</div>
	</div>
</fieldset>
<div class="form-actions row">
	<p class="col-sm-4 legend"><span class="req">*</span> ${_('Fields marked with this symbol are required.')}</p>
	<div class="controls col-sm-8">
		<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
		<button type="submit" class="btn btn-primary btn-large" id="submit" name="submit" title="${_('Change your password')}" tabindex="10">${_('Change Password')}</button>
	</div>
</div>
</form>

