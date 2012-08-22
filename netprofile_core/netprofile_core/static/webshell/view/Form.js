Ext.define('NetProfile.view.Form', {
	extend: 'Ext.form.Panel',
	alias: 'widget.npform',
	requires: [
		'Ext.form.*'
	],
	border: 0,
	autoScroll: true,
	bodyPadding: 5,
	layout: 'anchor',
	defaults: {
		anchor: '100%'
	},
	api: null,
	formCls: null,
	record: null,
	fieldDefaults: {
		labelWidth: 120,
		labelAlign: 'right',
		msgTarget: 'side'
	},
	buttons: [{
		text: 'Reset',
		handler: function() {
			this.up('form').getForm().reset();
		},
		tooltip: { text: 'Reset form fields to original values.', title: 'Reset Form' }
	}, {
		text: 'Submit',
		formBind: true,
		disabled: true,
		handler: function() {
			var form = this.up('form').getForm();

			if(form.isValid())
				form.updateRecord();
//				form.submit({
//					success: function(form, action) {
//						Ext.Msg.alert('Success', action.result.msg);
//						this.fireEvent('submitsuccess', form, action);
//					},
//					failure: function(form, action) {
//						Ext.Msg.alert('Failed', action.result.msg);
//						this.fireEvent('submitfailure', form, action);
//					},
//					scope: this
//				});
		},
		tooltip: { text: 'Validate and submit this form.', title: 'Submit Form' }
	}],
	initComponent: function() {
		this.api = this.getDirectAction();

		this.callParent();

		this.on('beforerender', this.loadForm, this);

		this.addEvents(
			'formloaded',
			'formloadfailed',
			'submitsuccess',
			'submitfailure'
		);

	},
	getDirectAction: function() {
		var api;
		if(!this.formCls)
		{
			api = Ext.getCmp('npws_propbar');
			this.formCls = api.getApiClass();
			this.record = api.getRecord();
		}
		api = NetProfile.api[this.formCls];
		return {
			load:       api.read,
			submit:     api.update,
			get_fields: api.get_fields
		};
	},
	loadForm: function() {
		this.api.get_fields(this.loadCallback.bind(this));
	},
	loadCallback: function(data, result) {
		Ext.destroy(this.removeAll());
		if(!data || !data.fields)
		{
			this.fireEvent('formloadfailed', data, result);
			return false;
		}
//		data.fields.forEach(function(item)
//		{
//			this.add(item);
//		}, this);
//		this.checkChange();
		this.add(data.fields);

		this.fireEvent('formloaded');

		if(this.record)
			this.getForm().loadRecord(this.record);
	}

});

