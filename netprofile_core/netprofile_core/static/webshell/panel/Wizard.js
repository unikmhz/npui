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

	config: {
		layout: 'card',
		border: 0,
		api: null,
		createInto: null,
		resetOnClose: false,

		wizardName: null,
		wizardCls: null,
		submitApi: 'create',
		createApi: 'get_create_wizard',
		actionApi: null,
		validateApi: null,

		extraParams: null,
		extraParamProp: null,
		extraParamRelProp: null,

		showSubmit: true,
		showCancel: true,
		showNavigation: true,

		cancelBtnCfg: {
			text: 'Cancel',
			iconCls: 'ico-cancel'
		},
		prevBtnCfg: {
			text: 'Prev',
			iconCls: 'ico-prev',
			disabled: true
		},
		nextBtnCfg: {
			text: 'Next',
			iconCls: 'ico-next',
			disabled: true
		},
		submitBtnCfg: {
			text: 'Submit',
			iconCls: 'ico-accept',
			disabled: true
		}
	},

	initComponent: function()
	{
		var me = this;

		me.bbar = [];
		if(me.showCancel)
			me.bbar.push(Ext.apply({
				itemId: 'act_cancel',
				handler: 'onCancel',
				scope: me
			}, me.cancelBtnCfg));
		if(me.showNavigation || me.showSubmit)
			me.bbar.push('->');
		if(me.showNavigation)
			me.bbar.push(Ext.apply({
				itemId: 'goto_prev',
				handler: 'onPrevious',
				scope: me
			}, me.prevBtnCfg), Ext.apply({
				itemId: 'goto_next',
				handler: 'onNext',
				scope: me
			}, me.nextBtnCfg));
		if(me.showSubmit)
			me.bbar.push(Ext.apply({
				itemId: 'act_submit',
				handler: 'onSubmit',
				scope: me
			}, me.submitBtnCfg));

		me.callParent();

		me.on('beforerender', me.loadWizard, me);
		me.on('fieldchanged', me.remoteValidate, me, { buffer: 500 });
	},
	onCancel: function(btn)
	{
		this.close();
		return true;
	},
	onPrevious: function(btn)
	{
		return this.update('prev');
	},
	onNext: function(btn)
	{
		return this.update('next');
	},
	onSubmit: function(btn)
	{
		var me = this,
			layout = me.getLayout(),
			curpane = layout.getActiveItem(),
			args;

		if(!me.validate())
			return false;
		if(curpane.allowSubmit && me.api && me.api.action)
		{
			args = [
				curpane.itemId,
				'submit',
				me.getValues(),
				me.actionCallback.bind(me)
			];
			if(me.wizardName)
				args.unshift(me.wizardName);
			me.api.action.apply(me.api, args);
			return true;
		}
		else if(me.createInto)
		{
			if(me.createInto.add(me.getValues()))
			{
				me.close();
				return true;
			}
		}
		else if(me.api.submit)
		{
			me.api.submit(
				me.getValues(),
				me.actionCallback.bind(me)
			);
			return true;
		}
		return false;
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
			pane, method;

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
		if('exec' in data.action)
		{
			method = data.action['exec'];
			if(method in me)
				me[method](data);
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
		if(me.showNavigation)
		{
			tbar.getComponent('goto_prev').setDisabled(!layout.getPrev() && !curpane.remotePrev);
			tbar.getComponent('goto_next').setDisabled((!layout.getNext() && !curpane.remoteNext) || curpane.allowSubmit);
		}
		if(me.showSubmit)
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
		var me = this,
			win;

		if(me.resetOnClose)
			me.loadWizard();
		else
		{
			win = me.up('window');
			if(win)
				win.close();
		}
		return true;
	},
	submit: function()
	{
	}
});

