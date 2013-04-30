Ext.define('NetProfile.model.Basic', {
	extend: 'Ext.data.Model',
	requires: [
		'Ext.data.reader.Json'
	],
	getData: function(includeAssociated)
	{
		var me = this,
			fields = me.fields.items,
			fLen = fields.length,
			data = {},
			name, f;

		for(f = 0; f < fLen; f++)
		{
			name = fields[f].name;
			if(fields[f].serialize)
				data[name] = fields[f].serialize(me.get(name), me);
			else
				data[name] = me.get(name);
		}

		if(includeAssociated === true)
			Ext.apply(data, me.getAssociatedData());
		return data;
	}
});

