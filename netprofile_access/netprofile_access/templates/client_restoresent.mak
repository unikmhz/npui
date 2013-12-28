## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_guest.mak"/>
<%block name="title">${_('Password Recovery Complete')}</%block>

<div class="block">
	<h1>${_('Password Recovery Complete')}</h1>
	<p>
% if change_pass:
		${_('New automatically generated password was sent to your e-mail.')}
% else:
		${_('Your current password was sent to your e-mail.')}
% endif
	</p>
	<p><a href="${req.route_url('access.cl.login')}">${_('Return to log in page')}</a>.</p>
</div>

