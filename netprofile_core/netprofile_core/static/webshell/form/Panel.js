/**
 * @class NetProfile.form.Panel
 * @extends Ext.form.Panel
 */
Ext.define('NetProfile.form.Panel', {
	extend: 'Ext.form.Panel',
	alias: 'widget.npform',
	requires: [
		'Ext.form.*',
		'NetProfile.form.field.IPv4',
		'NetProfile.form.field.IPv6',
		'NetProfile.form.field.Password'
	],
	statics: {
		formdef: {}
	},
	scrollable: 'vertical',
	remoteValidation: false,
	readOnly: false,
	bodyPadding: 5,
	layout: {
		type: 'anchor',
		reserveScrollbar: true
	},
	defaults: {
		anchor: '100%'
	},
	api: null,
	formCls: null,
	store: null,
	record: null,
	extraButtons: null,
	fieldDefaults: {
		labelWidth: 120,
		labelAlign: 'right',
		msgTarget: 'side'
	},
	trackResetOnLoad: true,

	resetText: 'Reset',
	resetTipText: 'Reset form fields to original values.',
	submitText: 'Submit',
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
			tooltip: this.resetTipText,
			tooltipType: 'title'
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
			tooltip: this.submitTipText,
			tooltipType: 'title'
		}];
		if(this.extraButtons && this.extraButtons.length)
			this.buttons = this.buttons.concat(this.extraButtons, ['->'], this.buttons);

		this.callParent();

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
			st = me.statics(),
			ro = false,
			cmp;

		if(!data || !data.fields)
		{
			me.fireEvent('formloadfailed', me, data, result);
			return false;
		}
		if(data.rvalid)
			me.remoteValidation = true;
		else
			me.remoteValidation = false;
		me.removeAll(true);
		if(typeof(data.ro) === 'boolean')
			ro = me.readOnly = !!data.ro || (me.record && !!me.record.readOnly);
		st.formdef[this.formCls] = data;
		me.suspendLayouts();
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
			if(me.readOnly)
				fld.readOnly = true;
		});
		me.add(data.fields);

		me.fireEvent('formloaded', me);

		if(me.record)
		{
			if(me.record.store)
			{
				me.mon(me.record.store, {
					load: function(store, recs, success, opts)
					{
						if(!success)
							return;

						var rectab = me.up('panel[cls~=record-tab]');

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

						var rectab = me.up('panel[cls~=record-tab]');

						if(rec.getId() === me.record.getId())
						{
							me.record = rec;
							title = rec.get('__str__');
							if(title)
								rectab.setTitle(title);
						}
					}
				});
			}
			me.suspendEvents();
			me.getForm().loadRecord(me.record);
			me.resumeEvents();
		}

		cmp = me.down('toolbar[dock=bottom]');
		if(cmp)
			cmp.setHidden(ro);
		me.resumeLayouts(true);
	}
});

