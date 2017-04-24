/**
 * @class NetProfile.controller.SettingsForm
 */
Ext.define('NetProfile.controller.SettingsForm', {
	requires: [
		'Ext.form.*',
		'NetProfile.form.field.HardwareAddress',
		'NetProfile.form.field.IPv4',
		'NetProfile.form.field.IPv6',
		'NetProfile.form.field.Money',
		'NetProfile.form.field.Password',
		'NetProfile.form.field.PropertyTree',
		'Ext.panel.Panel'
	],

	btnResetText: 'Reset',
	btnResetTipText: 'Reset form fields to original values',
	btnSaveText: 'Save',
	btnSaveTipText: 'Validate and save settings',

	descriptionStyle: {
		border: 0,
		padding: '7 0 10 24'
	},

	formFn: Ext.emptyFn,
	submitFn: Ext.emptyFn,
	onSuccessFn: Ext.emptyFn,
	onFailureFn: Ext.emptyFn,
	formItemId: 'form',
	formTarget: 'npws_mainbar',

	constructor: function(config)
	{
		var me = this;

		Ext.apply(me, config);
		me.callParent([config]);
	},
	process: function(sectionId)
	{
		var me = this;

		if(!sectionId)
			throw 'Missing configuration section';

		me.formFn({ section: sectionId }, me.onFormLoad.bind(me));
	},
	onFormLoad: function(data, result)
	{
		var me = this,
			form_target = me.formTarget,
			form, i, fld;

		if(!data || !data.fields || !data.section)
		{
			// FIXME
			return false;
		}
		if(typeof(form_target) === 'string')
			form_target = Ext.getCmp(form_target);

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
					me.descriptionStyle
				));
			else
				fld.push(Ext.apply(
					{ html: Ext.String.htmlEncode(data.fields[i].title) },
					me.descriptionStyle
				));
		}
		form = Ext.create('Ext.form.Panel', {
			region: 'center',
			itemId: me.formItemId,
			title: data.section.name,
			api: {
				submit: me.submitFn
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
				text: me.btnResetText,
				iconCls: 'ico-undo',
				handler: function()
				{
					this.up('form').getForm().reset();
				},
				tooltip: me.btnResetTipText,
				tooltipType: 'title'
			}, {
				text: me.btnSaveText,
				iconCls: 'ico-accept',
				formBind: true,
				disabled: true,
				handler: function()
				{
					var form = this.up('form').getForm();

					if(form.isValid())
						form.submit({
							success: me.onSuccessFn,
							failure: me.onFailureFn,
							scope: me
						});
				},
				tooltip: this.btnSaveTipText,
				tooltipType: 'title'
			}]
		});
		if(form_target && form_target.replaceWith)
			form_target.replaceWith(form);
	}
});

