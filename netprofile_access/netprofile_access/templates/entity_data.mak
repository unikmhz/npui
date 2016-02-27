## -*- coding: utf-8 -*-
<tpl if="data.rate || data.nextrate">
	<div>
<tpl if="data.rate">
	<span>
		<img class="np-inline-img" src="${req.static_url('netprofile_access:static/img/rate_small.png')}" alt="${_('Rate', domain='netprofile_access') | h}" />
		{data.rate}
	</span>
</tpl>
<tpl if="data.nextrate">
	<span>
		<img class="np-inline-img" src="${req.static_url('netprofile_access:static/img/nextrate_small.png')}" alt="${_('Next Rate', domain='netprofile_access') | h}" />
		{data.nextrate}
	</span>
</tpl>
	</div>
<tpl if="data.accessstate || data.qpend">
	<div>
<tpl if="data.accessstate">
	<span>
		<img class="np-inline-img" src="${req.static_url('netprofile_access:static/img')}/aestate_{data.accessimg}.png" alt="{data.accessstate}" />
		{data.accessstate}
	</span>
</tpl>
<tpl if="data.qpend">
	<span>
		<img class="np-inline-img" src="${req.static_url('netprofile_access:static/img/qpend_small.png')}" alt="${_('Ends', domain='netprofile_access') | h}" />
		{data.qpend}
	</span>
</tpl>
	</div>
</tpl>
</tpl>

