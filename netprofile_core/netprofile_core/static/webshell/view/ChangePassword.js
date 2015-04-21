Ext.define('NetProfile.view.ChangePassword', {
	extend: 'Ext.container.Viewport',
	requires: [
		'NetProfile.toolbar.MainToolbar',
		'NetProfile.panel.Wizard'
	],
	id: 'npws_chpass',
	layout: 'center',

	initComponent: function()
	{
		var me = this;

		me.items = [{
			xtype: 'npwizard',
			iconCls: 'ico-lock',
			shrinkWrap: true,
			border: true,
			showNavigation: false,
			wizardCls: 'User',
			createApi: 'get_chpass_wizard',
			submitApi: 'change_password',
			validateApi: 'ChangePassword',
			cancelBtnCfg: {
				iconCls: 'ico-logout',
				text: NetProfile.toolbar.MainToolbar.prototype.logoutText,
				tooltip: {
					text: NetProfile.toolbar.MainToolbar.prototype.logoutTipText,
					title: NetProfile.toolbar.MainToolbar.prototype.logoutText
				}
			},
			afterSubmit: function(data)
			{
				NetProfile.logOut(false);
			},
			onCancel: function(btn)
			{
				NetProfile.logOut(false);
			}
		}];

		me.callParent(arguments);
	}
});

