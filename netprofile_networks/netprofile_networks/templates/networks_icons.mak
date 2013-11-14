<tpl if="enabled">
	<img class="np-inline-img" src="${req.static_url('netprofile_core:static/img/enabled.png')}" />
<tpl else>
	<img class="np-inline-img" src="${req.static_url('netprofile_core:static/img/disabled.png')}" />
</tpl>
<tpl if="public">
	<img class="np-inline-img" src="${req.static_url('netprofile_core:static/img/public.png')}" />
<tpl else>
	<img class="np-inline-img" src="${req.static_url('netprofile_core:static/img/private.png')}" />
</tpl>
