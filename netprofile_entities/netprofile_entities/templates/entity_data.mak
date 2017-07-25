## -*- coding: utf-8 -*-
##
## NetProfile: XTemplate for rendering entity data
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
<%namespace module="netprofile.common.hooks" import="gen_block" />\
<tpl if="data.addrs && data.addrs.length">
<tpl for="data.addrs">
	<div>
		<img class="np-inline-img" src="${req.static_url('netprofile_entities:static/img/house_small.png')}" alt="${_('Address', domain='netprofile_entities') | h}" />
		{.:htmlEncode}
	</div>
</tpl>
</tpl>
<tpl if="data.address">
	<div>
		<img class="np-inline-img" src="${req.static_url('netprofile_entities:static/img/house_small.png')}" alt="${_('Address', domain='netprofile_entities') | h}" />
		{data.address:htmlEncode}
	</div>
</tpl>
<tpl if="data.phones && data.phones.length">
	<div>
<tpl for="data.phones">
	<span>
		<img class="np-inline-img" src="${req.static_url('netprofile_core:static/img/phone')}/{img:encodeURI}.png" alt="${_('Phone', domain='netprofile_entities') | h}" />
		{str:htmlEncode}
	</span>
</tpl>
	</div>
</tpl>
${gen_block('entities.block.data') | n}

