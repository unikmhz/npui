## -*- coding: utf-8 -*-
##
## NetProfile: HTML template for registration notification
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
<%block name="title">${_('Registration Complete')}</%block>

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

