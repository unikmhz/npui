Ext.define('NetProfile.controller.UserSettingsForm', {
	requires: [
		'Ext.form.*',
		'NetProfile.form.field.IPv4',
		'NetProfile.form.field.IPv6',
		'NetProfile.form.field.Password',
		'Ext.panel.Panel'
	],

	btnResetText: 'Reset',
	btnResetTipTitleText: 'Reset Settings',
	btnResetTipText: 'Reset form fields to original values.',
	btnSaveText: 'Save',
	btnSaveTipTitleText: 'Save Settings',
	btnSaveTipText: 'Validate and save your settings.',

	descriptionStyle: {
		border: 0,
		padding: '7 0 10 24'
	},

	process: function(xid)
	{
		var m;

		if(!xid)
			throw 'Missing configuration section';
		m = xid.match(/^ss(\d+)$/);
		if(m === null)
			throw 'Invalid configuration section';
		xid = parseInt(m[1]);

		NetProfile.api.UserSetting.usform_get({ section: xid }, this.onFormLoad.bind(this));
	},
	onFormLoad: function(data, result)
	{
		var form, mainbar, i, fld, descr;

		if(!data || !data.fields || !data.section)
		{
			// FIXME
			return false;
		}

		mainbar = Ext.getCmp('npws_mainbar');
		fld = [];
		if(data.section.descr)
			fld.push({
				html: data.section.descr,
				border: 0,
				colspan: 2,
				padding: 16
			});
		for(i = 0; i < data.fields.length; i++)
		{
			fld.push(data.fields[i]);
			if(data.fields[i].description)
				fld.push(Ext.apply(
					{ html: Ext.String.htmlEncode(data.fields[i].description) },
					this.descriptionStyle
				));
			else
				fld.push(Ext.apply(
					{ html: Ext.String.htmlEncode(data.fields[i].title) },
					this.descriptionStyle
				));
		}
		form = Ext.create('Ext.form.Panel', {
			region: 'center',
			title: data.section.name,
			api: {
				submit: NetProfile.api.UserSetting.usform_submit
			},
			bodyPadding: 5,
			border: 0,
			layout: {
				type: 'table',
				columns: 2
			},
			fieldDefaults: {
				labelWidth: 230,
				labelAlign: 'right',
				msgTarget: 'side'
			},
			items: fld,
			buttons: [{
				text: this.btnResetText,
				iconCls: 'ico-undo',
				handler: function()
				{
					this.up('form').getForm().reset();
				},
				tooltip: { text: this.btnResetTipText, title: this.btnResetTipTitleText }
			}, {
				text: this.btnSaveText,
				iconCls: 'ico-accept',
				formBind: true,
				disabled: true,
				handler: function()
				{
					var form = this.up('form').getForm();

					if(form.isValid())
						form.submit({
							success: function(form, action)
							{
								NetProfile.api.UserSetting.client_get(function(data, result)
								{
									if(!data || !data.settings)
										return false;

									NetProfile.userSettings = data.settings;
									return true;
								});
							},
							failure: function(form, action)
							{
							},
							scope: this
						});
				},
				tooltip: { text: this.btnSaveTipText, title: this.btnSaveTipTitleText }
			}]
		});
		mainbar.replaceWith(form);
	}
});

