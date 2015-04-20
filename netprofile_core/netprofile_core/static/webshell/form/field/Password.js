Ext.define('NetProfile.form.field.Password', {
	extend: 'Ext.form.field.Text',
	alias: 'widget.passwordfield',

	config: {
		inputType: 'password',
		emptyValue: '• • •',
		selectOnFocus: true,
		triggers: {
			clear: {
				cls: 'x-form-clear-trigger',
				weight: 1,
				handler: function()
				{
					this.setRawValue(null);
					return this.isValid();
				}
			}
		}
	},

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
			this.clearFlag = true;
			v = this.emptyValue;
		}
		return this.callParent([v]);
	},
	resetOriginalValue: function()
	{
		this.setRawValue(null);
		this.callParent(arguments);
	},
	getModelData: function()
	{
		var ret, val;

		ret = {};
		val = this.getRawValue();
		if(this.clearFlag)
			ret[this.name] = null;
		else if(val != this.emptyValue)
			ret[this.name] = val;
		ret[this.name + '_clear'] = this.clearFlag;
		return ret;
	},
	getSubmitData: function()
	{
		return this.getModelData();
	}
});

