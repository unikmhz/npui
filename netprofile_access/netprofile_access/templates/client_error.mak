## -*- coding: utf-8 -*-
##
## NetProfile: HTML template for error pages
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
<%inherit file="netprofile_access:templates/client_base.mak"/>

	<div class="jumbotron"><div class="container">
		<h1>${error} <small>${_('Error %d', domain='netprofile_access') % req.response.status_code}</small></h1>
% if req.response.status_code == 404:
		<p>
			${_('There is no page with the address you provided.', domain='netprofile_access')}
			${_('We\'re really sorry about that.', domain='netprofile_access')}
		</p>
% elif req.response.status_code == 403:
		<p>
			${_('You don\'t have the credentials that are required to access this page.', domain='netprofile_access')}
% if not req.user:
			${_('Maybe you forgot to log in?', domain='netprofile_access')}
% else:
			${_('We\'re really sorry about that.', domain='netprofile_access')}
% endif
		</p>
% endif
		<p>${_('You can contact support or try again.', domain='netprofile_access')}</p>
		<p class="pull-right">
% if req.referer:
			<a class="btn btn-info btn-lg" role="button" href="${req.referer}" title="${_('Go back from where you came', domain='netprofile_access')}">
				<span class="glyphicon glyphicon-backward"></span>
				${_('Go Back', domain='netprofile_access')}
			</a>
% endif
% if req.user:
			<a class="btn btn-primary btn-lg" role="button" href="${req.route_url('access.cl.home')}" title="${_('Return to home page', domain='netprofile_access')}">
				<span class="glyphicon glyphicon-home"></span>
				${_('Go Home', domain='netprofile_access')}
			</a>
% else:
			<a class="btn btn-primary btn-lg" role="button" href="${req.route_url('access.cl.login')}" title="${_('Return to sign in page', domain='netprofile_access')}">
				<span class="glyphicon glyphicon-log-in"></span>
				${_('Log In', domain='netprofile_access')}
			</a>
% endif
		</p>
	</div></div>

