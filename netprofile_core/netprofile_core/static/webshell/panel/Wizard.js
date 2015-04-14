/**
 * @class NetProfile.panel.Wizard
 * @extends Ext.panel.Panel
 */
Ext.define('NetProfile.panel.Wizard', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.npwizard',
	requires: [
		'Ext.form.*',
		'NetProfile.form.field.IPv4',
		'NetProfile.form.field.IPv6',
		'NetProfile.form.field.Password',
		'NetProfile.form.WizardPane'
	],
	layout: 'card',
	border: 0,
	api: null,
	wizardName: null,
	submitApi: 'create',
	createApi: 'get_create_wizard',
	resetOnClose: false,
	extraParams: null,
	extraParamProp: null,
	extraParamRelProp: null,
	actionApi: null,
	validateApi: null,
	wizardCls: null,
	createInto: null,
//	doValidation: true, do we need this global flag???

	btnPrevText: 'Prev',
	btnNextText: 'Next',
	btnCancelText: 'Cancel',
	btnSubmitText: 'Submit',

	initComponent: function()
	{
		this.bbar = [{
			itemId: 'act_cancel',
			text: this.btnCancelText,
			iconCls: 'ico-cancel',
			handler: function(btn)
			{
				this.close();
				return true;
			},
			scope: this
		}, '->', {
			itemId: 'goto_prev',
			text: this.btnPrevText,
			iconCls: 'ico-prev',
			disabled: true,
			handler: function(btn)
			{
				return this.update('prev');
			},
			scope: this
		}, {
			itemId: 'goto_next',
			text: this.btnNextText,
			iconCls: 'ico-next',
			disabled: true,
			handler: function(btn)
			{
				return this.update('next');
			},
			scope: this
		}, {
			itemId: 'act_submit',
			text: this.btnSubmitText,
			iconCls: 'ico-accept',
			disabled: true,
			handler: function(btn)
			{
				var layout = this.getLayout(),
					curpane = layout.getActiveItem();

				if(!this.validate())
					return false;
				if(curpane.allowSubmit && this.api && this.api.action)
				{
					var args = [
						curpane.itemId,
						'submit',
						this.getValues(),
						this.actionCallback.bind(this)
					];
					if(this.wizardName)
						args.unshift(this.wizardName);
					this.api.action.apply(this.api, args);
					return true;
				}
				else if(this.createInto)
				{
					if(this.createInto.add(this.getValues()))
					{
						this.close();
						return true;
					}
				}
				else if(this.api.submit)
				{
					this.api.submit(
						this.getValues(),
						this.actionCallback.bind(this)
					);
					return true;
				}
				return false;
			},
			scope: this
		}];

		this.callParent();

		this.on('beforerender', this.loadWizard, this);
		this.on('fieldchanged', this.remoteValidate, this, { buffer: 500 });
	},
	getDirectAction: function()
	{
		var api, valid = null;
//		if(!this.wizardCls)
//		{
//			api = Ext.getCmp('npws_propbar');
//			this.wizardCls = api.getApiClass();
//		}
		api = NetProfile.api[this.wizardCls];
		if(this.validateApi)
			valid = NetProfile.api.CustomValidator.validate;
		else
			valid = api.validate_fields;
		return {
//			load      : api.read,
			submit    : api[this.submitApi],
			get_steps : api[this.createApi],
			action    : api[this.actionApi],
			validate  : valid
		};
	},
	loadWizard: function()
	{
		if(!this.api)
			this.api = this.getDirectAction();
		this.fetchExtraParams();
		var args = [this.loadCallback, this];
		if(this.extraParams)
			args.unshift(this.extraParams);
		if(this.wizardName)
			args.unshift(this.wizardName);
		this.api.get_steps.apply(this.api, args);
	},
	remoteValidate: function(fld)
	{
		if(this.api.validate)
		{
			var me = this,
				values = this.getValues(),
				cbfunc;

			cbfunc = function(data, res)
			{
				var layout = this.getLayout(),
					form = layout.getActiveItem().getForm(),
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
			};

			if(this.validateApi)
				this.api.validate(this.validateApi, values, cbfunc, this);
			else
				this.api.validate(values, cbfunc, this);
		}
		return true;
	},
	loadCallback: function(data, result)
	{
		var me = this,
			win;

		if(!data || !data.fields)
		{
			this.fireEvent('wizardloadfailed', this, data, result);
			return false;
		}
		if(data.title)
		{
			win = this.up('window');
			if(win)
				win.setTitle(data.title);
			else
				this.setTitle(data.title);
		}
		if(data.validator)
		{
			this.validateApi = data.validator;
			this.api = this.getDirectAction();
		}
		Ext.destroy(this.removeAll());
		this.fireEvent('beforeaddfields', this, data, result);
		Ext.Array.forEach(data.fields, function(step)
		{
			Ext.Array.forEach(step.items, function(fld)
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
		});
		this.add(data.fields);
		this.update('init');

		this.fireEvent('wizardloaded', this, data, result);
	},
	actionCallback: function(data, result)
	{
		var me = this,
			layout = me.getLayout(),
			pane;

		if(!data || !data.success || !data.action)
		{
			// FIXME: add visual indication
			return false;
		}
		if('disable' in data.action)
			Ext.Array.forEach(data.action.disable, function(stepid)
			{
				var step = me.getComponent(stepid);
				if(step)
				{
					step.doValidation = false;
					step.doGetValues = false;
				}
			});
		if('enable' in data.action)
			Ext.Array.forEach(data.action.enable, function(stepid)
			{
				var step = me.getComponent(stepid);
				if(step)
				{
					step.doValidation = true;
					step.doGetValues = true;
				}
			});
		if('redraw' in data.action)
			Ext.Array.forEach(data.action.redraw, function(widget)
			{
			});
		if(('reload' in data.action) && data.action.reload && this.createInto)
			this.createInto.reload();
		if('do' in data.action)
			switch(data.action['do'])
			{
				case 'prev':
				case 'next':
					layout[data.action]();
					me.update('init');
					return true;
				case 'goto':
					if(!('goto' in data.action))
						return false;
					pane = me.getComponent(data.action['goto']);
					if(pane)
						layout.setActiveItem(pane);
					me.update('init');
					return true;
				case 'close':
					return me.close();
				default:
					break;
			}
		return false;
	},
	update: function(dir)
	{
		var me = this,
			layout = me.getLayout(),
			tbar = me.down('toolbar'),
			curpane = layout.getActiveItem();

		if(dir !== 'init')
		{
			if(Ext.Array.contains(['prev', 'next'], dir))
			{
				if((dir == 'next') && curpane && curpane.doValidation && !curpane.getForm().isValid())
				{
					// FIXME: add visual indication
					return false;
				}
				var attr = false;
				switch(dir)
				{
					case 'prev':
						attr = curpane.remotePrev;
						break;
					case 'next':
						attr = curpane.remoteNext;
						break;
					default:
						break;
				}
				if(Ext.isString(attr))
				{
					layout.setActiveItem(attr);
					curpane = layout.getActiveItem();
				}
				else if(attr && this.api && this.api.action)
				{
					var args = [curpane.itemId, dir, this.getValues(), this.actionCallback.bind(this)];
					if(this.wizardName)
						args.unshift(this.wizardName);
					this.api.action.apply(this.api, args);
					return false;
				}
				else
				{
					layout[dir]();
					curpane = layout.getActiveItem();
				}
			}
		}
		tbar.getComponent('goto_prev').setDisabled(!layout.getPrev() && !curpane.remotePrev);
		tbar.getComponent('goto_next').setDisabled((!layout.getNext() && !curpane.remoteNext) || curpane.allowSubmit);
		tbar.getComponent('act_submit').setDisabled(layout.getNext() && !curpane.allowSubmit);

		return true;
	},
	validate: function()
	{
		var isvalid = true;

		this.items.each(function(i)
		{
			if(i.doValidation && !i.getForm().isValid())
				isvalid = false;
		});
		return isvalid;
	},
	nextStep: function()
	{
		return this.update('next');
	},
	prevStep: function()
	{
		return this.update('prev');
	},
	gotoStep: function(idx)
	{
	},
	getValues: function()
	{
		var res = {},
			j, iv;

		this.items.each(function(i)
		{
			if(!i.doGetValues)
				return;
			iv = i.getValues(false, false, false, true);
			for(j in iv)
				res[j] = iv[j];
		});
		return res;
	},
	fetchExtraParams: function()
	{
		var rec;

		if(!this.extraParams && this.extraParamProp)
		{
			rec = this.up('panel[cls~=record-tab]');
			if(rec)
			{
				rec = rec.record;
				this.extraParams = {};
				if(this.extraParamRelProp)
					this.extraParams[this.extraParamProp] = rec.get(this.extraParamRelProp);
				else
					this.extraParams[this.extraParamProp] = rec.get(this.extraParamProp);
			}
		}
	},
	close: function()
	{
		if(this.resetOnClose)
			this.loadWizard();
		else
			this.up('window').close();
		return true;
	},
	submit: function()
	{
	}
});

