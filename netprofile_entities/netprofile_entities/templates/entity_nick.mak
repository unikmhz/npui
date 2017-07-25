## -*- coding: utf-8 -*-
##
## NetProfile: XTemplate for rendering entity identifiers
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
{__str__:htmlEncode}
<tpl if="data.flags && data.flags.length">
	<br />
	<tpl for="data.flags">
		<img class="np-inline-img" src="${req.static_url('netprofile_entities:static/img/flags/')}{0:encodeURI}.png" alt="{1:htmlEncode}" title="{1:htmlEncode}" />
	</tpl>
</tpl>

