Ext.define('NetProfile.view.TopBar', {
	extend: 'Ext.toolbar.Toolbar',
	alias: 'widget.topbar',
	id: 'npws_topbar',
	stateId: 'npws_topbar',
	stateful: true,
	requires: 'NetProfile.view.Form',
	collapsible: false,
//	layout: 'fit',
//	split: false,
	height: 32,
	style: {
	},
	items: [{
		text: 'Test Slider',
		handler: function() {
			var pb = Ext.getCmp('npws_propbar');
			pb.show();
		}
	}, {
		text: 'Test Form',
		handler: function() {
			var form = Ext.create('NetProfile.view.Form', {
				formCls: 'User'
			});
			var win = Ext.create('Ext.window.Window', {
				layout: 'fit',
				items: [form]
			}).show();
			//win.add(form);
			//win.show();
		}
	}, '->', {
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

