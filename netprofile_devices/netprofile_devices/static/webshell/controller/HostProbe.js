/**
 * @class NetProfile.devices.controller.HostProbe
 * @extends Ext.app.Controller
 */
Ext.define('NetProfile.devices.controller.HostProbe', {
	extend: 'Ext.app.Controller',
	requires: [
		'Ext.mixin.Observable',
		'NetProfile.data.SockJS',
		'NetProfile.window.CenterWindow',
		'NetProfile.devices.grid.ProbeResults',
		'NetProfile.devices.data.ProbeResultsModel',
		'NetProfile.devices.data.ProbeResultsStore'
	],

	probeResultsText: 'Probe Results',

	init: function()
	{
		var me = this;

		if(NetProfile.cap('HOSTS_PROBE'))
		{
			Ext.mixin.Observable.observe(NetProfile.data.SockJS, {
				taskresult: 'onTaskResult',
				scope: me
			});
		}
	},
	onTaskResult: function(me, sock, ev)
	{
		var me = this,
			data = ev.data,
			results, store, grid, win;

		if(data.tname !== 'netprofile_devices.tasks.task_probe_hosts')
			return false;
		results = data.value;

		if(!results || !results.length)
		{
			// FIXME: display error
			return false;
		}

		store = Ext.create('NetProfile.devices.data.ProbeResultsStore', {
		});

		Ext.Array.forEach(results, function(res)
		{
			store.add(Ext.create('NetProfile.devices.data.ProbeResultsModel', res));
		});

		grid = Ext.create('NetProfile.devices.grid.ProbeResults', {
			store: store
		});
		win = Ext.create('NetProfile.window.CenterWindow', {
			title: me.probeResultsText,
			iconCls: 'ico-netmon',
			minWidth: 650,
			width: 650,
			items: [ grid ]
		});
		win.show();
		return true;
	}
});

