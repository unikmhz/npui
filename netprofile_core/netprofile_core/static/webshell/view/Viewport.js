Ext.define('NetProfile.view.Viewport', {
	extend: 'Ext.container.Viewport',
	requires: [
		'NetProfile.view.TopBar',
		'NetProfile.view.MainBar',
		'NetProfile.view.SideBar',
		'NetProfile.view.FileDownload'
	],
	id: 'npws_viewport',
	stateId: 'npws_viewport',
	stateful: true,
	layout: {
		type: 'border',
		padding: 4
	},
	border: 0,
	defaults: {
		split: true
	},
	items: [{
		region: 'west',
		xtype: 'sidebar'
	}, {
		region: 'center',
		split: false,
		xtype: 'mainbar'
	}, {
		region: 'south',
		split: false,
		xtype: 'filedownload'
	}],

	initComponent: function()
	{
		this.callParent(arguments);
	}
});

