Ext.define('NetProfile.toolbar.MainToolbar', {
	extend: 'Ext.toolbar.Toolbar',
	alias: 'widget.maintoolbar',
	requires: [
		'Ext.menu.Menu',
		'Ext.menu.CheckItem',
		'Ext.tab.Panel',
		'Ext.JSON',
		'Ext.XTemplate',
		'NetProfile.store.Language',
		'NetProfile.window.CenterWindow'
	],
	config: {
		id: 'npws_maintoolbar',
		stateId: 'npws_maintoolbar',
		stateful: true,
		collapsible: false,
		height: 32,
		langMenuConfig: {
			xtype: 'menucheckitem',
			group: 'lang',
			checkHandler: 'doChangeLocale'
		}
	},

	toolsText: 'Tools',
	toolsTipText: 'Various tools and windows',
	logoutText: 'Log out',
	logoutTipText: 'Log out of the application and return to login screen.',
	chPassText: 'Change password',
	chLangText: 'Change language',
	showConsoleText: 'Show console',
	aboutText: 'About…',
	aboutNetProfileText: 'About NetProfile',
	infoText: 'Information',
	contributorsText: 'NetProfile project contributors',
	gplPart1Text: 'NetProfile is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.',
	gplPart2Text: 'NetProfile is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.',
	licenseText: 'License',
	modulesText: 'Modules',
	currentModulesText: 'Currently loaded modules:',
	modLineTpl: '<li><strong>{0}</strong>, version {1}</li>',
	downloadTpl: 'NetProfile source code can be <a href="{0}">downloaded here</a>.',

	initComponent: function()
	{
		var me = this,
			lang_store = Ext.create('NetProfile.store.Language'),
			lang_menu = [];

		lang_store.each(function(rec, idx, len)
		{
			var lang_code = rec.get('code'),
				item;

			item = Ext.apply({
				itemId: lang_code,
				iconCls: 'ico-lang-' + lang_code,
				text: rec.get('name'),
				scope: me,
				checked: lang_code === NetProfile.currentLocale
			}, me.getLangMenuConfig() || {});
			lang_menu.push(item);
		});

		me.items = [{
			text: me.toolsText,
			iconCls: 'ico-tool',
			itemId: 'sub_tools',
			tooltip: { text: me.toolsTipText, title: me.toolsText },
			menu: {
				xtype: 'menu',
				items: [{
					xtype: 'menuitem',
					iconCls: 'ico-lock',
					text: me.chPassText,
					handler: NetProfile.changePassword
				}, {
					xtype: 'menuitem',
					showSeparator: false,
					iconCls: 'ico-locale',
					text: me.chLangText,
					menu: {
						xtype: 'menu',
						items: lang_menu
					}
				}, {
					xtype: 'menuitem',
					iconCls: 'ico-console',
					text: me.showConsoleText,
					handler: function(el, ev)
					{
						NetProfile.showConsole();
					}
				}, '-', {
					text: me.aboutText,
					iconCls: 'ico-info',
					handler: 'showAboutWindow',
					scope: me
				}]
			}
		}, '->', {
			text: me.logoutText,
			iconCls: 'ico-logout',
			tooltip: { text: me.logoutTipText, title: me.logoutText },
			handler: 'doLogout',
			scope: me
		}];
		me.callParent(arguments);
	},
	doLogout: function()
	{
		NetProfile.logOut(true);
	},
	doChangeLocale: function(menuitem, checked)
	{
		if(checked)
			window.location = '/core/noop?__locale=' + menuitem.getItemId();
	},
	showAboutWindow: function()
	{
		var me = this;

		Ext.Ajax.request({
			url: NetProfile.baseURL + '/core/about',
			method: 'POST',
			success: function(response, opt)
			{
				var data = Ext.JSON.decode(response.responseText),
					tabs = [],
					modhtml = [],
					win, infohtml;

				if(!data)
					return false;
				infohtml = '<div><strong>NetProfile CRM/NMS</strong><br />Copyright © 2010-2016 Alex Unigovsky<br />Copyright © 2010-2016 NetProfile project contributors</div><div>ASD</div>';
				infohtml = new Ext.XTemplate(
					'<div>',
						'<strong>NetProfile CRM/NMS</strong>',
						'<br />Copyright © 2010-2016 Alex Unigovsky',
						'<br />Copyright © 2010-2016 {contrib}',
					'</div>',
					'<div style="padding-top: 1em;">{gpl1}</div>',
					'<div style="padding-top: 1em;">{gpl2}</div>',
					'<div style="padding-top: 1em;">{dl}</div>'
				);
				tabs.push({
					iconCls: 'ico-info',
					title: me.infoText,
					border: 0,
					bodyPadding: 8,
					html: infohtml.apply({
						contrib: me.contributorsText,
						gpl1: Ext.String.htmlEncode(me.gplPart1Text),
						gpl2: Ext.String.htmlEncode(me.gplPart2Text),
						dl: Ext.String.format(me.downloadTpl, 'https://github.com/unikmhz/npui')
					}),
					scrollable: 'vertical'
				});
				if(data.modules && data.modules.length)
				{
					Ext.Array.forEach(data.modules, function(modinfo)
					{
						modhtml.push(Ext.String.format(
							me.modLineTpl,
							Ext.String.htmlEncode(modinfo[0]),
							Ext.String.htmlEncode(modinfo[1])
						));
					});

					if(modhtml.length)
					{
						modhtml = me.currentModulesText
							+ '<ul>'
							+ modhtml.join('')
							+ '</ul>';
						tabs.push({
							iconCls: 'ico-module',
							title: me.modulesText,
							border: 0,
							bodyPadding: 8,
							html: modhtml,
							scrollable: 'vertical'
						});
					}
				}
				if(data.license)
					tabs.push({
						iconCls: 'ico-license',
						title: me.licenseText,
						border: 0,
						bodyPadding: 8,
						html: '<pre>' + Ext.String.htmlEncode(data.license) + '</pre>',
						scrollable: 'vertical'
					});

				win = Ext.create('NetProfile.window.CenterWindow', {
					minWidth: 600,
					width: 600,
					maxHeight: 550,
					iconCls: 'ico-info',
					title: me.aboutNetProfileText,
					items: [{
						xtype: 'tabpanel',
						layout: 'fit',
						border: 0,
						items: tabs
					}]
				});

				win.show();
			}
		});
	}
});

