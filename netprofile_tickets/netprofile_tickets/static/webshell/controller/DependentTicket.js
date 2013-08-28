Ext.define('NetProfile.tickets.controller.DependentTicket', {
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
			rec;

		if(!rectab || !rectab.record)
			return true;
		rec = rectab.record;
		if(!data.fields || !data.fields.length)
			return true;
		data.fields[0].items.push({
			xtype: 'hidden',
			editable: false,
			allowBlank: true,
			name: 'parentid',
			value: rec.getId()
		});
		Ext.Array.forEach(data.fields, function(step)
		{
			Ext.Array.forEach(step.items, function(fld)
			{
				if(!fld.name)
					return;
				if(fld.name === 'entityid')
					fld.value = rec.get('entityid');
				if(fld.name === 'entity')
					Ext.apply(fld, {
						xtype: 'textfield',
						readOnly: true,
						value: rec.get('entity')
					});
			});
		});
		return true;
	}
});

