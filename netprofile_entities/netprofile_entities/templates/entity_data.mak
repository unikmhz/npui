<tpl if="data.addrs && data.addrs.length">
<tpl for="data.addrs">
	<div>
		<img class="np-inline-img" src="${req.static_url('netprofile_entities:static/img/house_small.png')}" />
		{.}
	</div>
</tpl>
</tpl>
<tpl if="data.address">
	<div>
		<img class="np-inline-img" src="${req.static_url('netprofile_entities:static/img/house_small.png')}" />
		{data.address}
	</div>
</tpl>
<tpl if="data.phones && data.phones.length">
	<div>
<tpl for="data.phones">
	<span>
		<img class="np-inline-img" src="${req.static_url('netprofile_core:static/img/phone')}/{img}.png" />
		{str}
	</span>
</tpl>
	</div>
</tpl>

