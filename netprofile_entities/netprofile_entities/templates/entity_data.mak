## -*- coding: utf-8 -*-
<%namespace module="netprofile.common.hooks" import="gen_block" />\
<tpl if="data.addrs && data.addrs.length">
<tpl for="data.addrs">
	<div>
		<img class="np-inline-img" src="${req.static_url('netprofile_entities:static/img/house_small.png')}" alt="${_('Address', domain='netprofile_entities') | h}" />
		{.}
	</div>
</tpl>
</tpl>
<tpl if="data.address">
	<div>
		<img class="np-inline-img" src="${req.static_url('netprofile_entities:static/img/house_small.png')}" alt="${_('Address', domain='netprofile_entities') | h}" />
		{data.address}
	</div>
</tpl>
<tpl if="data.phones && data.phones.length">
	<div>
<tpl for="data.phones">
	<span>
		<img class="np-inline-img" src="${req.static_url('netprofile_core:static/img/phone')}/{img}.png" alt="${_('Phone', domain='netprofile_entities') | h}" />
		{str}
	</span>
</tpl>
	</div>
</tpl>
${gen_block('entities.block.data') | n}

