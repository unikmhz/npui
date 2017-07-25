## -*- coding: utf-8 -*-
##
## NetProfile: Template for HTTP error 403
## Copyright © 2015-2017 Alex Unigovsky
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
<%inherit file="netprofile_core:templates/base.mak"/>
<%block name="title">${_('Access Denied', domain='netprofile_core') | h}</%block>\
<%block name="head_css">\
	<link rel="stylesheet" href="${req.static_url('netprofile_core:static/css/login.css')}" type="text/css" media="screen, projection" />\
</%block>\
<div id="login_outer" role="presentation">
	<img alt="NetProfile" src="${req.static_url('netprofile_core:static/img/nplogo.png')}" draggable="false" role="banner" />
	<div class="elem errheader">
		${_('Error %d', domain='netprofile_core') % (403,) | h}
	</div>
	<div class="elem errbody">${_('Resource access was forbidden.', domain='netprofile_core') | h}</div>
</div>

