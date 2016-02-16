/**
 * @class NetProfile.devices.grid.ProbeResults
 * @extends Ext.grid.Panel
 */
Ext.define('NetProfile.devices.grid.ProbeResults', {
	extend: 'Ext.grid.Panel',
	alias: 'widget.proberesults',
	requires: [
		'Ext.grid.*',
		'NetProfile.devices.data.ProbeResultsStore'
	],

	initComponent: function()
	{
		var me = this;

		me.callParent();
	}
});

