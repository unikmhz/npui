Ext.define('NetProfile.view.MainBar', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.mainbar',
	requires: [
		'NetProfile.view.PropBar',
		'NetProfile.view.grid.core.User'
	],
	id: 'npws_mainbar',
	stateId: 'npws_mainbar',
	stateful: true,
	layout: {
		type: 'border',
		padding: 0
	},
	items: [{
		region: 'south',
		xtype: 'propbar'
	}]
});

