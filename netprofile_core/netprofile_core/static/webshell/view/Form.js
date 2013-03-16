/**
 * @class NetProfile.view.Form
 * @extends Ext.form.Panel
 */
Ext.define('NetProfile.view.Form', {
	extend: 'Ext.form.Panel',
	alias: 'widget.npform',
	requires: [
		'Ext.form.*',
		'Ext.ux.form.field.IPv4',
		'Ext.ux.form.field.Password'
	],
	statics: {
		formdef: {}
	},
//	border: 0,
	autoScroll: true,
	bodyPadding: 5,
	layout: 'anchor',
	defaults: {
		anchor: '100%'
	},
	api: null,
	formCls: null,
	store: null,
	record: null,
	fieldDefaults: {
		labelWidth: 120,
		labelAlign: 'right',
		msgTarget: 'side'
	},
	trackResetOnLoad: true,

	resetText: 'Reset',
	resetTipTitleText: 'Reset Form',
	resetTipText: 'Reset form fields to original values.',
	submitText: 'Submit',
	submitTipTitleText: 'Submit Form',
	submitTipText: 'Validate and submit this form.',

	initComponent: function()
	{
		this.buttons = [{
			text: this.resetText,
			iconCls: 'ico-undo',
			handler: function()
			{
				this.up('form').getForm().reset();
			},
			tooltip: { text: this.resetTipText, title: this.resetTipTitleText }
		}, {
			text: this.submitText,
			iconCls: 'ico-accept',
			formBind: true,
			disabled: true,
			handler: function()
			{
				var fp = this.up('form'),
					form = fp.getForm();

				if(form.isValid())
				{
					if(fp.record)
					{
						if(fp.record.store)
							form.updateRecord(fp.record);
						else
						{
							form.updateRecord(fp.record);
							fp.record.save();
						}
						form.loadRecord(fp.record);
					}
				}
//					form.submit({
//						success: function(form, action) {
//							Ext.Msg.alert('Success', action.result.msg);
//							this.fireEvent('submitsuccess', form, action);
//						},
//						failure: function(form, action) {
//							Ext.Msg.alert('Failed', action.result.msg);
//							this.fireEvent('submitfailure', form, action);
//						},
//						scope: this
//					});
			},
			tooltip: { text: this.submitTipText, title: this.submitTipTitleText }
		}];

		this.callParent();

		this.on('beforerender', this.loadForm, this);

		this.addEvents(
			'formloaded',
			'formloadfailed',
			'submitsuccess',
			'submitfailure'
		);
	},
	getDirectAction: function()
	{
		var api;
		if(!this.formCls)
		{
			var p = this.up('panel');

			this.formCls = p.apiClass;
			this.record = p.record;
		}
		api = NetProfile.api[this.formCls];
		return {
			load:       api.read,
			submit:     api.update,
			get_fields: api.get_fields
		};
	},
	loadForm: function()
	{
		var st = this.statics();

		this.api = this.getDirectAction();
		if(st.formdef.hasOwnProperty(this.formCls))
			this.loadCallback(st.formdef[this.formCls], null);
		else
			this.api.get_fields(this.loadCallback.bind(this));
	},
	loadCallback: function(data, result)
	{
		var st = this.statics();

		if(!data || !data.fields)
		{
			this.fireEvent('formloadfailed', data, result);
			return false;
		}
		Ext.destroy(this.removeAll());
		st.formdef[this.formCls] = data;
		this.suspendLayouts();
		this.add(data.fields);
		this.resumeLayouts(true);

		this.fireEvent('formloaded');

		if(this.record)
		{
			if(this.record.store)
			{
				this.mon(this.record.store, {
					load: function(store, recs, success, opts)
					{
						if(!success)
							return;

						var me = this,
							rectab = this.up('panel[cls~=record-tab]');

						Ext.Array.forEach(recs, function(rec)
						{
							var title;

							if(rec.getId() === me.record.getId())
							{
								me.record = rec;
								title = rec.get('__str__');
								if(title)
									rectab.setTitle(title);
							}
						});
					},
					update: function(store, rec, op, opts)
					{
						if(op !== Ext.data.Model.COMMIT)
							return;

						var rectab = this.up('panel[cls~=record-tab]');

						if(rec.getId() === this.record.getId())
						{
							this.record = rec;
							title = rec.get('__str__');
							if(title)
								rectab.setTitle(title);
						}
					},
					scope: this
				});
			}
			this.getForm().loadRecord(this.record);
		}
	}
});

