/**
 * @class NetProfile.devices.controller.HostProbe
 * @extends Ext.app.Controller
 */
Ext.define('NetProfile.devices.controller.HostProbe', {
	extend: 'Ext.app.Controller',
	requires: [
		'Ext.JSON',
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

			me.control({
				'grid_hosts_Host' : {
					action_probe: function(grid, item, ev, record)
					{
						me.onProbe('hosts', [record.getId()]);
					}
				},
				'grid_entities_Entity' : {
					action_probe: function(grid, item, ev, record)
					{
						me.onProbe('entities', [record.getId()]);
					}
				},
				'grid_entities_PhysicalEntity' : {
					action_probe: function(grid, item, ev, record)
					{
						me.onProbe('entities', [record.getId()]);
					}
				},
				'grid_entities_LegalEntity' : {
					action_probe: function(grid, item, ev, record)
					{
						me.onProbe('entities', [record.getId()]);
					}
				},
				'grid_entities_StructuralEntity' : {
					action_probe: function(grid, item, ev, record)
					{
						me.onProbe('entities', [record.getId()]);
					}
				},
				'grid_domains_Domain' : {
					action_probe: function(grid, item, ev, record)
					{
						me.onProbe('domains', [record.getId()]);
					}
				},
				'grid_geo_House' : {
					action_probe: function(grid, item, ev, record)
					{
						me.onProbe('houses', [record.getId()]);
					}
				},
				'grid_geo_Street' : {
					action_probe: function(grid, item, ev, record)
					{
						me.onProbe('streets', [record.getId()]);
					}
				},
				'grid_geo_District' : {
					action_probe: function(grid, item, ev, record)
					{
						me.onProbe('districts', [record.getId()]);
					}
				},
				'grid_geo_City' : {
					action_probe: function(grid, item, ev, record)
					{
						me.onProbe('cities', [record.getId()]);
					}
				},
				'grid_geo_HouseGroup' : {
					action_probe: function(grid, item, ev, record)
					{
						me.onProbe('housegroups', [record.getId()]);
					}
				}
			});
		}
	},
	onProbe: function(type, ids)
	{
		if(!NetProfile.rtSocket)
			return false; // FIXME: Print some error to console?

		NetProfile.rtSocket.send(Ext.JSON.encode({
			'type'  : 'task',
			'tname' : 'netprofile_devices.tasks.task_probe_hosts',
			'args'  : [type, ids]
		}));
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
			return true;
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

