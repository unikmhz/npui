Ext.define('Ext.ux.form.field.Password', {
	extend: 'Ext.form.field.Trigger',
	alias: 'widget.passwordfield',

	inputType: 'password',
	selectOnFocus: true,
	trigger1Cls: 'x-form-clear-trigger',

	initComponent: function()
	{
		this.clearFlag = false;
		this.callParent();
		this.on({
			change: function(fld, val)
			{
				if(val)
					this.clearFlag = false;
				else
					this.clearFlag = true;
			},
			scope: this
		});
	},
	setRawValue: function(v)
	{
		if((v === undefined) || (v === null) || (v == ''))
		{
			this.clearFlag = false;
			v = '• • •';
		}
		return this.callParent([v]);
	},
	onTrigger1Click: function(ev)
	{
		this.setRawValue(null);
		return this.isValid();
	},
	getModelData: function()
	{
		var ret, val;

		ret = {};
		val = this.getRawValue();
		if(this.clearFlag)
			ret[this.name] = null;
		else if(val != '• • •')
			ret[this.name] = val;
		ret[this.name + '_clear'] = this.clearFlag;
		return ret;
	},
	getSubmitData: function()
	{
		return this.getModelData();
	}
});

