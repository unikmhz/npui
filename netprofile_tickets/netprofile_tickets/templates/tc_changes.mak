## -*- coding: utf-8 -*-
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

