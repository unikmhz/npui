Ext.define('NetProfile.view.Form', {
	extend: 'Ext.Panel',
	alias: 'widget.npform',
	requires: [
	],
	border: false,
	formCls: '',
	formConfig: {
		fields: []
	},
	initComponent: function() {
		var config = {};
		Ext.apply(this, Ext.apply(this.initialConfig, config));
		NetProfile.view.Form.superclass.initComponent.apply(this, arguments);

		//this.callParent();

		this.on('render', function() {
			this.loadForm();
		}, this);

		this.addEvents['formLoaded'];

	},
	getDirectAction: function() {
		return NetProfile.api[this.formCls];
	},
	loadCallback: function(data, result) {
		//console.log('loadCallback', this, arguments);
		//console.log(this);
		this.removeAll();

		Ext.each(this.formConfig.fields, function(item) {
			Ext.each(data.fields, function(item2) {
				if(item.name == item2.name) {
					Ext.apply(item2, item);
					return false;
				}
			}, this);
			// if in data.fields, override config.items
		}, this);

		var conf = {
			xtype: 'form',
			api: this.getDirectAction(),
			border: false,
			labelWidth: 200,
			items: data.fields,
			buttons: [{
				text: 'Submit',
				scope: this,
				handler: function() {
					//console.log('submit form', this, arguments);
					this.get(0).getForm().submit({
						params: {},
						failure: function(form, action) {
							if(action.failureType == Ext.form.Action.SERVER_INVALID)
								alert('form submit failure' + action.result.errors);
							this.fireEvent('submitFailure', form, action);
						},
						success: function(form, action) {
							this.fireEvent('submitSuccess', form, action);
						},
						scope:this
					});
				}
			}]
		}
		Ext.apply(conf, this.formConfig);

		// custom layout
		//Ext.Object.merge(this,conf);
		this.add(conf);
		this.doLayout();
		console.log(this);
		console.log(conf);
		this.fireEvent('formLoaded');
	},
	loadForm: function() {
		this.getDirectAction().get_fields(this.loadCallback.bind(this));
	}

});

