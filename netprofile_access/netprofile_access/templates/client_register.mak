## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_guest.mak"/>
<%block name="title">${_('Register')}</%block>

<form method="post" action="${req.route_url('access.cl.register')}">
<div class="block">
	<h1>${_('Registration Form')}</h1>
% if 'csrf' in errors:
	<p class="error">${errors['csrf']}</p>
% endif
	<p>${_('Please fill in this form so we can properly set up your account.')}</p>
% if must_verify:
	<p><strong>${_('Note:')}</strong> ${_('You will receive a confirmation e-mail with an activation link. Your account will be inactive until you click this link.')}</p>
% endif
	<h2>${_('Account Settings')}</h2>
	<p class="field">
		<label for="user">${_('User Name')}</label>
		<input class="text required" type="text" id="user" name="user" title="${_('Enter your user name here')}" value="" size="30" maxlength="254" tabindex="1" />
		<span class="req">*</span>
% if 'user' in errors:
		<span class="error">${errors['user']}</span>
% endif
	</p>
	<p class="field">
		<label for="email">${_('E-mail')}</label>
		<input class="text required" type="text" id="email" name="email" title="${_('Enter your e-mail address')}" value="" size="30" maxlength="254" tabindex="2" />
		<span class="req">*</span>
% if 'email' in errors:
		<span class="error">${errors['email']}</span>
% endif
	</p>
	<p class="field">
		<label for="pass">${_('Password')}</label>
		<input class="text required" type="password" id="pass" name="pass" title="${_('Enter your desired password')}" value="" size="30" maxlength="254" tabindex="3" />
		<span class="req">*</span>
% if 'pass' in errors:
		<span class="error">${errors['pass']}</span>
% endif
	</p>
	<p class="field">
		<label for="pass2">${_('Repeat Password')}</label>
		<input class="text required" type="password" id="pass2" name="pass2" title="${_('Repeat previously entered password')}" value="" size="30" maxlength="254" tabindex="4" />
		<span class="req">*</span>
% if 'pass2' in errors:
		<span class="error">${errors['pass2']}</span>
% endif
	</p>
	<h2>${_('Personal Information')}</h2>
	<p class="field">
		<label for="name_family">${_('Family Name')}</label>
		<input class="text required" type="text" id="name_family" name="name_family" title="${_('Enter your family name')}" value="" size="30" maxlength="254" tabindex="5" />
		<span class="req">*</span>
% if 'name_family' in errors:
		<span class="error">${errors['name_family']}</span>
% endif
	</p>
	<p class="field">
		<label for="name_given">${_('Given Name')}</label>
		<input class="text required" type="text" id="name_given" name="name_given" title="${_('Enter your given name')}" value="" size="30" maxlength="254" tabindex="6" />
		<span class="req">*</span>
% if 'name_given' in errors:
		<span class="error">${errors['name_given']}</span>
% endif
	</p>
	<p class="field">
		<label for="name_middle">${_('Middle Name')}</label>
		<input class="text required" type="text" id="name_middle" name="name_middle" title="${_('Enter your middle name')}" value="" size="30" maxlength="254" tabindex="7" />
% if 'name_middle' in errors:
		<span class="error">${errors['name_middle']}</span>
% endif
	</p>
% if must_recaptcha:
	<h2>${_('User Validation')}</h2>
% if 'recaptcha' in errors:
	<p class="error">${errors['recaptcha']}</p>
% endif
	<script type="text/javascript" src="http://www.google.com/recaptcha/api/challenge?k=${rc_public}"></script>
	<noscript>
		<p class="field">
			<iframe src="http://www.google.com/recaptcha/api/noscript?k=${rc_public}" height="300" width="500" frameborder="0"></iframe><br />
			<textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
			<input type="hidden" name="recaptcha_response_field" value="manual_challenge" />
		</p>
	</noscript>
% endif
	<p><span class="req">*</span> ${_('Fields marked with this symbol are required.')}</p>
	<p class="form_footer">
		<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
		<button type="submit" id="submit" name="submit" title="${_('Register new account')}" tabindex="10">${_('Register')}</button>
	</p>
</div>
</form>

