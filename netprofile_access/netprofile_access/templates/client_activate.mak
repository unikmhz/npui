## -*- coding: utf-8 -*-
##
## NetProfile: HTML template for account activation
## Copyright © 2013-2017 Alex Unigovsky
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

