## -*- coding: utf-8 -*-
##
## NetProfile: XTemplate for rendering access entity data
## Copyright © 2016-2017 Alex Unigovsky
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
<tpl if="data.rate || data.nextrate">
	<div>
<tpl if="data.rate">
	<span>
		<img class="np-inline-img" src="${req.static_url('netprofile_access:static/img/rate_small.png')}" alt="${_('Rate', domain='netprofile_access') | h}" />
		{data.rate:htmlEncode}
	</span>
</tpl>
<tpl if="data.nextrate">
	<span>
		<img class="np-inline-img" src="${req.static_url('netprofile_access:static/img/nextrate_small.png')}" alt="${_('Next Rate', domain='netprofile_access') | h}" />
		{data.nextrate:htmlEncode}
	</span>
</tpl>
	</div>
<tpl if="data.accessstate || data.qpend">
	<div>
<tpl if="data.accessstate">
	<span>
		<img class="np-inline-img" src="${req.static_url('netprofile_access:static/img')}/aestate_{data.accessimg:htmlEncode}.png" alt="{data.accessstate:htmlEncode}" />
		{data.accessstate:htmlEncode}
	</span>
</tpl>
<tpl if="data.qpend">
	<span>
		<img class="np-inline-img" src="${req.static_url('netprofile_access:static/img/qpend_small.png')}" alt="${_('Ends', domain='netprofile_access') | h}" />
		{data.qpend:htmlEncode}
	</span>
</tpl>
	</div>
</tpl>
</tpl>

