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
	autoScroll: true,
	remoteValidation: false,
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
			itemId: 'btn_reset',
			handler: function()
			{
				this.up('form').getForm().reset();
			},
			tooltip: { text: this.resetTipText, title: this.resetTipTitleText }
		}, {
			text: this.submitText,
			iconCls: 'ico-accept',
			itemId: 'btn_submit',
			formBind: true,
			disabled: true,
			handler: function()
			{
				var fp = this.up('form'),
					form = fp.getForm();

				if(form.isValid())
				{
					if(!fp.record)
						return;
					if(fp.record.store)
					{
						form.updateRecord(fp.record);
						if(!fp.record.store.autoSync)
							fp.record.store.sync();
					}
					else
					{
						form.updateRecord(fp.record);
						fp.record.save();
					}
					form.loadRecord(fp.record);
				}
			},
			tooltip: { text: this.submitTipText, title: this.submitTipTitleText }
		}];

		this.callParent();

		this.addEvents(
			'fieldchanged',
			'formloaded',
			'formloadfailed',
			'submitsuccess',
			'submitfailure'
		);
		this.on('beforerender', this.loadForm, this);
		this.on('fieldchanged', this.remoteValidate, this, { buffer: 500 });
	},
	getDirectAction: function()
	{
		var api;
		if(!this.formCls)
		{
			var p = this.up('panel[cls~=record-tab]');

			this.formCls = p.apiClass;
			this.record = p.record;
		}
		api = NetProfile.api[this.formCls];
		return {
			load:       api.read,
			submit:     api.update,
			get_fields: api.get_fields,
			validate:   api.validate_fields
		};
	},
	loadForm: function()
	{
		var st = this.statics();

		this.api = this.getDirectAction();
		if(st.formdef.hasOwnProperty(this.formCls))
			this.loadCallback(st.formdef[this.formCls], null);
		else
			this.api.get_fields(this.loadCallback, this);
	},
	remoteValidate: function(fld)
	{
		if(this.api.validate && this.remoteValidation)
		{
			var me = this,
				values = this.getValues(false, false, false, true);

			this.api.validate(values, function(data, res)
			{
				var form = this.getForm(),
					xfld;

				if(!data || !data.success)
					return false;
				if(!data.errors)
					return true;
				form.getFields().each(function(xfld)
				{
					if(!xfld.name)
						return true;
					if(xfld.name in data.errors)
						xfld.asyncErrors = data.errors[xfld.name];
					else
						xfld.asyncErrors = [];
				});
				form.isValid();
				return true;
			}, this);
		}
		return true;
	},
	loadCallback: function(data, result)
	{
		var me = this,
			st = this.statics();

		if(!data || !data.fields)
		{
			this.fireEvent('formloadfailed', this, data, result);
			return false;
		}
		if(data.rvalid)
			this.remoteValidation = true;
		else
			this.remoteValidation = false;
		this.removeAll(true);
		st.formdef[this.formCls] = data;
		this.suspendLayouts();
		Ext.Array.forEach(data.fields, function(fld)
		{
			Ext.apply(fld, {
				listeners: {
					change: function(fld, newval)
					{
						this.fireEvent('fieldchanged', fld);
					},
					scope: me
				}
			});
		});
		this.add(data.fields);
		this.resumeLayouts(true);

		this.fireEvent('formloaded', this);

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
			var tb = this.down('toolbar[dock=bottom]'),
				ro = !!this.record.readOnly;
			if(ro)
				tb.hide();
			else
				tb.show();
			this.suspendEvents();
			this.getForm().loadRecord(this.record);
			this.resumeEvents();
		}
	}
});

