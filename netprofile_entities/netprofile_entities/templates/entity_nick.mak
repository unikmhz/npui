## -*- coding: utf-8 -*-
{__str__:htmlEncode}
<tpl if="data.flags && data.flags.length">
	<br />
	<tpl for="data.flags">
		<img class="np-inline-img" src="${req.static_url('netprofile_entities:static/img/flags/')}{0:encodeURI}.png" alt="{1:htmlEncode}" title="{1:htmlEncode}" />
	</tpl>
</tpl>

