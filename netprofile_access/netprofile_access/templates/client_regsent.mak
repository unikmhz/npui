## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_guest.mak"/>
<%block name="title">${_('Registration Complete')}</%block>

<div class="block">
	<h1>${_('Registration Complete')}</h1>
	<p>
		${_('Thank you for registering an account in our system.')}
% if must_verify:
		${_('A message containing an activation link was sent to the e-mail address you provided. You won\'t be able to log in until you follow this link.')}
% else:
		${_('You can now log in with the user name and password that you provided during registration.')}
		<a href="${req.route_url('access.cl.login')}">${_('Return to log in page')}</a>.
% endif
	</p>
</div>

