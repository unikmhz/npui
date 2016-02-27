## -*- coding: utf-8 -*-
{__str__}
<tpl if="data.flags && data.flags.length">
	<br />
	<tpl for="data.flags">
		<img class="np-inline-img" src="${req.static_url('netprofile_entities:static/img/flags/')}{0}.png" alt="{1}" />
	</tpl>
</tpl>

