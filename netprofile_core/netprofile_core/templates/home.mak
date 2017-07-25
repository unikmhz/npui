## -*- coding: utf-8 -*-
##
## NetProfile: HTML template for administrative UI
## Copyright © 2012-2017 Alex Unigovsky
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
<%block name="head">
	<script type="text/javascript" src="${req.route_url('extapi')}" charset="UTF-8"></script>
	<script type="text/javascript" src="${req.route_url('core.js.webshell')}" charset="UTF-8"></script>
</%block>

	<!-- Fields required for b/c history management -->
	<form id="history-form" class="x-hidden-display">
		<input type="hidden" id="x-history-field" />
		<iframe id="x-history-frame"></iframe>
	</form>

	<div id="splash"><div class="splashcont">
		<img src="${req.static_url('netprofile_core:static/img/loading-bars.svg')}" alt="${_('Please wait while the application is loading…') | h}" />
		<h1>${_('Loading…') | h}</h1>
	</div></div>

