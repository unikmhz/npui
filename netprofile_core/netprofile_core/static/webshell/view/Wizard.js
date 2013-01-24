/**
 * @class NetProfile.view.Wizard
 * @extends Ext.panel.Panel
 */
Ext.define('NetProfile.view.Wizard', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.npwizard',
	requires: [
		'Ext.form.*',
		'Ext.ux.form.field.IPv4',
		'Ext.ux.form.field.Password',
		'NetProfile.view.WizardPane'
	],
	layout: 'card',
	border: 0,
	api: null,
	submitApi: 'create',
	wizardCls: null,
	createInto: null,
//	doValidation: true, do we need this global flag???

	btnPrevText: 'Prev',
	btnNextText: 'Next',
	btnCancelText: 'Cancel',
	btnSubmitText: 'Submit',

	initComponent: function() {
		this.bbar = [{
			itemId: 'act_cancel',
			text: this.btnCancelText,
			iconCls: 'ico-cancel',
			handler: function(btn) {
				this.up('window').close();
				return true;
			},
			scope: this
		}, '->', {
			itemId: 'goto_prev',
			text: this.btnPrevText,
			iconCls: 'ico-prev',
			disabled: true,
			handler: function(btn) {
				return this.update('prev');
			},
			scope: this
		}, {
			itemId: 'goto_next',
			text: this.btnNextText,
			iconCls: 'ico-next',
			disabled: true,
			handler: function(btn) {
				return this.update('next');
			},
			scope: this
		}, {
			itemId: 'act_submit',
			text: this.btnSubmitText,
			iconCls: 'ico-accept',
			disabled: true,
			handler: function(btn) {
				if(!this.validate())
					return false;
				if(this.createInto)
				{
					if(this.createInto.add(this.getValues()))
					{
						this.up('window').close();
						return true;
					}
				}
				else if(this.api.submit)
				{
				}
				return false;
			},
			scope: this
		}];

		this.callParent();

		this.on('beforerender', this.loadWizard, this);

		this.addEvents(
			'wizardloaded',
			'wizardloadfailed',
			'submitsuccess',
			'submitfailure'
		);
	},
	getDirectAction: function() {
		var api;
		if(!this.wizardCls)
		{
			api = Ext.getCmp('npws_propbar');
			this.wizardCls = api.getApiClass();
		}
		api = NetProfile.api[this.wizardCls];
		return {
//			load      : api.read,
			submit    : api[this.submitApi],
			get_steps : api.get_create_wizard
		};
	},
	loadWizard: function() {
		if(!this.api)
			this.api = this.getDirectAction();
		this.api.get_steps(this.loadCallback.bind(this));
	},
	loadCallback: function(data, result) {
		if(!data || !data.fields)
		{
			this.fireEvent('wizardloadfailed', data, result);
			return false;
		}
		Ext.destroy(this.removeAll());
		this.add(data.fields);
		this.update('init');

		this.fireEvent('wizardloaded');
	},
	update: function(dir) {
		var me = this,
			layout = me.getLayout(),
			tbar = me.down('toolbar'),
			curpane;

		if(dir !== 'init')
		{
			if(Ext.Array.contains(['prev', 'next'], dir))
			{
				curpane = layout.getActiveItem();
				if(curpane && curpane.doValidation && !curpane.getForm().isValid())
				{
					// FIXME: add visual indication
					return false;
				}
				layout[dir]();
			}
		}
		tbar.getComponent('goto_prev').setDisabled(!layout.getPrev());
		tbar.getComponent('goto_next').setDisabled(!layout.getNext());
		tbar.getComponent('act_submit').setDisabled(layout.getNext());

		return true;
	},
	validate: function() {
		var isvalid = true;

		this.items.each(function(i) {
			if(i.doValidation && !i.getForm().isValid())
				isvalid = false;
		});
		return isvalid;
	},
	nextStep: function() {
	},
	prevStep: function() {
	},
	gotoStep: function(idx) {
	},
	getValues: function() {
		var res = {},
			j, iv;

		this.items.each(function(i) {
			iv = i.getValues();
			for(j in iv)
				res[j] = iv[j];
		});
		return res;
	},
	submit: function() {
	}
});

