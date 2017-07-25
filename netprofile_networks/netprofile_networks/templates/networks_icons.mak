## -*- coding: utf-8 -*-
##
## NetProfile: XTemplate for rendering network icons
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
<tpl if="enabled">
	<img class="np-inline-img" src="${req.static_url('netprofile_core:static/img/enabled.png')}" />
<tpl else>
	<img class="np-inline-img" src="${req.static_url('netprofile_core:static/img/disabled.png')}" />
</tpl>
<tpl if="public">
	<img class="np-inline-img" src="${req.static_url('netprofile_core:static/img/public.png')}" />
<tpl else>
	<img class="np-inline-img" src="${req.static_url('netprofile_core:static/img/private.png')}" />
</tpl>
