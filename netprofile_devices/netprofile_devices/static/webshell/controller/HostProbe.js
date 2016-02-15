/**
 * @class NetProfile.devices.controller.HostProbe
 * @extends Ext.app.Controller
 */
Ext.define('NetProfile.devices.controller.HostProbe', {
	extend: 'Ext.app.Controller',
	requires: [
		'Ext.mixin.Observable',
		'NetProfile.data.SockJS'
	],

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
		return true;
	}
});

