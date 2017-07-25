## -*- coding: utf-8 -*-
##
## NetProfile: XTemplate for rendering ticket changes
## Copyright © 2017 Alex Unigovsky
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
<tpl if="data.bits && data.bits.length">
<div class="change_details">
<tpl for="data.bits">
<tpl for=".">
	<div class="change_bit">
		<div class="change_icon"><img class="np-block-img" src="{[NetProfile.staticURL]}/static/tickets/img/history/{icon:encodeURI}.png" /></div>
		<div class="change_text">{text:htmlEncode}</div>
	</div>
</tpl>
</tpl>
</div>
</tpl>

