Ext.define('NetProfile.form.DynamicCheckboxGroup', {
	extend: 'Ext.form.CheckboxGroup',
	alias: 'widget.dyncheckboxgroup',
	requires: [
	],
	store: null,
	valueField: null,
	displayField: null,
	formCheckboxes: true,
	readOnly: false,

	initComponent: function()
	{
		this.storedValues = null;
		this.callParent();
	},
	onRender: function(p, idx)
	{
		this.callParent();
		if(this.store && this.valueField)
		{
			if(!this.displayField)
				this.displayField = '__str__';
			if(Ext.isString(this.store))
			{
				this.store = Ext.create(this.store, {
					buffered: false,
					autoLoad: true,
					pageSize: -1,
					listeners: {
						load: this.onLoad,
						prefetch: this.onLoad,
						scope: this
					}
				});
			}
			else if(!this.store.isLoading())
			{
				this.suspendLayouts();
				if(this.store.getCount() > 0)
				{
					this.store.each(function(rec)
					{
						this.addCheckbox(
							rec.get(this.valueField),
							rec.get(this.displayField)
						);
					}, this);
					if(this.storedValues)
					{
						this.suspendEvents(false);
						this.setValue(this.storedValues);
						this.storedValues = null;
						this.resumeEvents();
					}
				}
				else
					this.store.reload();
				this.resumeLayouts(true);
			}
		}
	},
	addCheckbox: function(k, v)
	{
		this.add({
			name: this.name,
			boxLabel: v,
			inputValue: k,
			submitValue: this.formCheckboxes,
			isFormField: this.formCheckboxes,
			readOnly: this.readOnly
		});
	},
	onLoad: function(store, recs, ok)
	{
		var len, i;

		this.suspendLayouts();
		this.storedValues = this.getValue();
		this.removeAll(true);
		for(i = 0, len = recs.length; i < len; i++)
		{
			this.addCheckbox(
				recs[i].get(this.valueField),
				recs[i].get(this.displayField)
			);
		}
		if(this.storedValues)
		{
			this.setValue(this.storedValues);
			this.storedValues = null;
		}
		this.resetOriginalValue();
		this.resumeLayouts(true);
	},
	getValue: function()
	{
		var val = {}, ck = [];

		if(this.storedValues)
			return this.storedValues;
		Ext.Array.forEach(this.getChecked(), function(box)
		{
			var val = box.getSubmitValue();
			if(val !== null)
				ck.push(val);
		});
		if(ck.length > 0)
			val[this.name] = ck;
		return val;
	},
	setValue: function(value)
	{
		if(Ext.isArray(value))
		{
			xvalue = {};
			xvalue[this.name] = value;
			value = xvalue;
		};
		if(!Ext.isObject(value))
		{
			xvalue = {};
			xvalue[this.name] = [value];
			value = xvalue;
		}
		if(this.getBoxes().length)
			return this.callParent([value]);
		if((this.name in value) && (value[this.name].length))
			this.storedValues = value;
		else
			this.storedValues = null;
	},
	getModelData: function()
	{
		var ret = [],
			xret = {};

		if(this.storedValues)
			return this.storedValues;
		Ext.Array.forEach(this.getChecked(), function(box)
		{
			var val = box.getSubmitValue();
			if(val !== null)
				ret.push(val);
		});
		xret[this.name] = ret;
		return xret;
	},
	getSubmitData: function()
	{
		return this.getModelData();
	}
});

