## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_guest.mak"/>
<%block name="title">${_('Register')}</%block>

<h1>${_('Registration Form')}</h1>
<p>${_('Please fill in this form so we can properly set up your account.')}</p>
% if must_verify:
<p><strong>${_('Note:')}</strong> ${_('You will receive a confirmation e-mail with an activation link. Your account will be inactive until you click this link.')}</p>
% endif
% if 'csrf' in errors:
<div class="alert alert-warning alert-dismissable">
	<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
	${errors['csrf']}
</div>
% endif

<form method="post" novalidate="novalidate" action="${req.route_url('access.cl.register')}" id="register-form" class="form-horizontal" role="form">
<fieldset>
	<legend>${_('Account Settings')}</legend>
% if not  maillogin:
	<div class="row form-group${' has-warning' if 'user' in errors else ''}">
		<label class="col-sm-4 control-label" for="user">${_('User Name')}</label>
		<div class="controls col-sm-8">
			<input
				type="text"
				class="form-control"
				required="required"
				id="user"
				name="user"
				title="${_('Enter your user name here')}"
				placeholder="${_('Enter your user name here')}"
				value=""
				size="30"
				maxlength="254"
				pattern="[\w\d._-]+"
				tabindex="1"
				data-validation-ajax-ajax="${req.route_url('access.cl.check.nick')}"
				data-validation-required-message="${_('This field is required')}"
				data-validation-maxlength-message="${_('This field is too long')}"
				data-validation-pattern-message="${_('Invalid character was used')}"
				data-validation-ajax-message="${_('This username is already taken')}"
			/>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'user' in errors:
				<li>${errors['user']}</li>
% endif
			</ul></div>
		</div>
	</div>
% endif
	<div class="row form-group${' has-warning' if 'email' in errors else ''}">
		<label class="col-sm-4 control-label" for="email">${_('E-mail')}</label>
		<div class="controls col-sm-8">
			<input
				type="email"
				class="form-control"
				required="required"
				id="email"
				name="email"
				title="${_('Enter your e-mail address')}"
				placeholder="${_('Enter your e-mail address')}"
				value=""
				size="30"
				maxlength="254"
				tabindex="2"
				data-validation-required-message="${_('This field is required')}"
				data-validation-maxlength-message="${_('This field is too long')}"
				data-validation-email-message="${_('Invalid e-mail format')}"
			/>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'email' in errors:
				<li>${errors['email']}</li>
% endif
			</ul></div>
		</div>
	</div>
	<div class="row form-group${' has-warning' if 'pass' in errors else ''}">
		<label class="col-sm-4 control-label" for="pass">${_('Password')}</label>
		<div class="controls col-sm-8">
			<input
				type="password"
				class="form-control"
				required="required"
				id="pass"
				name="pass"
				title="${_('Enter your desired password')}"
				placeholder="${_('Enter your desired password')}"
				value=""
				size="30"
				minlength="${str(min_pwd_len)}"
				maxlength="254"
				tabindex="3"
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
				tabindex="4"
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
<fieldset>
	<legend>${_('Personal Information')}</legend>
	<div class="row form-group${' has-warning' if 'name_family' in errors else ''}">
		<label class="col-sm-4 control-label" for="name_family">${_('Family Name')}</label>
		<div class="controls col-sm-8">
			<input
				type="text"
				class="form-control"
				required="required"
				id="name_family"
				name="name_family"
				title="${_('Enter your family name')}"
				placeholder="${_('Enter your family name')}"
				value=""
				size="30"
				maxlength="254"
				tabindex="5"
				data-validation-required-message="${_('This field is required')}"
				data-validation-maxlength-message="${_('This field is too long')}"
			/>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'name_family' in errors:
				<li>${errors['name_family']}</li>
% endif
			</ul></div>
		</div>
	</div>
	<div class="row form-group${' has-warning' if 'name_given' in errors else ''}">
		<label class="col-sm-4 control-label" for="name_given">${_('Given Name')}</label>
		<div class="controls col-sm-8">
			<input
				type="text"
				class="form-control"
				required="required"
				id="name_given"
				name="name_given"
				title="${_('Enter your given name')}"
				placeholder="${_('Enter your given name')}"
				value=""
				size="30"
				maxlength="254"
				tabindex="6"
				data-validation-required-message="${_('This field is required')}"
				data-validation-maxlength-message="${_('This field is too long')}"
			/>
			<span class="req">*</span>
			<div class="help-block"><ul role="alert">
% if 'name_given' in errors:
				<li>${errors['name_given']}</li>
% endif
			</ul></div>
		</div>
	</div>
	<div class="row form-group${' has-warning' if 'name_middle' in errors else ''}">
		<label class="col-sm-4 control-label" for="name_middle">${_('Middle Name')}</label>
		<div class="controls col-sm-8">
			<input
				type="text"
				class="form-control"
				id="name_middle"
				name="name_middle"
				title="${_('Enter your middle name')}"
				placeholder="${_('Enter your middle name')}"
				value=""
				size="30"
				maxlength="254"
				tabindex="7"
				data-validation-maxlength-message="${_('This field is too long')}"
			/>
			<div class="help-block"><ul role="alert">
% if 'name_middle' in errors:
				<li>${errors['name_middle']}</li>
% endif
			</ul></div>
		</div>
	</div>
</fieldset>
% if must_recaptcha:
<fieldset>
	<legend>${_('User Validation')}</legend>
	<div class="row recaptcha-row form-group"><div class="col-sm-offset-4 col-sm-8">
% if 'recaptcha' in errors:
		<div class="alert alert-warning alert-dismissable">
			<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>
			${errors['recaptcha']}
		</div>
% endif
		<script type="text/javascript" src="http://www.google.com/recaptcha/api/challenge?k=${rc_public}"></script>
		<noscript>
			<iframe src="http://www.google.com/recaptcha/api/noscript?k=${rc_public}" height="300" width="500" frameborder="0"></iframe><br />
			<textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
			<input type="hidden" name="recaptcha_response_field" value="manual_challenge" />
		</noscript>
	</div></div>
</fieldset>
% endif
<div class="form-actions row">
	<p class="col-sm-4 legend"><span class="req">*</span> ${_('Fields marked with this symbol are required.')}</p>
	<div class="controls col-sm-8">
		<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
		<button type="submit" class="btn btn-primary btn-large" id="submit" name="submit" title="${_('Register new account')}" tabindex="10">${_('Register')}</button>
	</div>
</div>
</form>

