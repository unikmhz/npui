## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_guest.mak"/>
<%block name="title">${_('Account Activation')}</%block>

% if failed:
<h1>${_('Account Activation Failed')}</h1>
<p>${_('Either your activation link was incomplete or it has timed out.')}</p>
% else:
<h1>${_('Account Activation Successful')}</h1>
<p>${_('You can now log in to your newly created account.')}</p>
% endif
<p><a href="${req.route_url('access.cl.login')}">${_('Return to log in page')}</a>.</p>

