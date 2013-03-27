Ext.define('NetProfile.core.controller.RelatedWizard', {
	extend: 'Ext.util.Observable',

	caller: null,

	observeWizard: function(wizard)
	{
		this.mon(wizard, {
			beforeaddfields: this.beforeAddFields,
			scope: this
		});
	},

	beforeAddFields: function(wiz, data, res)
	{
		var rectab = this.caller.up('panel[cls~=record-tab]'),
			rec, prop, rel_prop;

		if(!rectab || !rectab.record)
			return true;
		rec = rectab.record;
		rel_prop = this.caller.extraParamRelProp;
		prop = this.caller.extraParamProp;
		if(!prop)
			return true;
		if(!rel_prop)
			rel_prop = prop;
		Ext.Array.forEach(data.fields, function(step)
		{
			Ext.Array.forEach(step.items, function(fld)
			{
				if(fld.name && (fld.name === prop))
					fld.value = rec.get(rel_prop);
				else if(fld.hiddenField && (fld.hiddenField === prop))
					Ext.apply(fld, {
						xtype: 'textfield',
						readOnly: true,
						value: rec.get('__str__')
					});
			});
		});
		return true;
	}
});

