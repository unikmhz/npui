Ext.define('NetProfile.view.TopBar', {
	extend: 'Ext.toolbar.Toolbar',
	alias: 'widget.topbar',
	requires: [
		'NetProfile.view.Form'
	],
	id: 'npws_topbar',
	stateId: 'npws_topbar',
	stateful: true,
	collapsible: false,
//	layout: 'fit',
//	split: false,
	height: 32,
	style: {
	},
	items: ['->', {
		text: 'Log out',
		iconCls: 'ico-logout',
		tooltip: { text: 'Log out of the application and return to login screen.', title: 'Log out' },
		handler: function() {
			location.href = '/logout';
		}
	}],
	initComponent: function() {
		this.callParent(arguments);
	},
});

