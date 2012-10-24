Ext.define('NetProfile.view.TopBar', {
	extend: 'Ext.toolbar.Toolbar',
	alias: 'widget.topbar',
	requires: [
		'NetProfile.view.Form',
		'NetProfile.view.Wizard'
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

	logoutText: 'Log out',
	logoutTipText: 'Log out of the application and return to login screen.',

	initComponent: function() {
		this.items = ['->', {
			text: this.logoutText,
			iconCls: 'ico-logout',
			tooltip: { text: this.logoutTipText, title: this.logoutText },
			handler: function() {
				location.href = '/logout';
			}
		}];
		this.callParent(arguments);
	},
});

