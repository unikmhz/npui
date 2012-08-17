Ext.Loader.setConfig({enabled: true});

Ext.require([
	'Ext.direct.*',
	'Ext.state.*',
	'Ext.util.Cookies', 
	'Ext.Ajax'
]);

Ext.application({
	name: 'NetProfile',
	appFolder: '/static/webshell',
	autoCreateViewport: false,

	controllers: [
		'NetProfile.controller.LoginController'
	],

	launch: function() {
		Ext.QuickTips.init();
		Ext.create('NetProfile.view.LoginWindow', {}).show();
	}
});

