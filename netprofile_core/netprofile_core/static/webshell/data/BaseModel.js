Ext.define('NetProfile.data.schema.Namer', {
	extend: 'Ext.data.schema.Namer',
	alias: 'namer.np',

	undotted: function(name)
	{
		if(name.indexOf('.') < 0)
			return name;

		var parts = name.split('.'),
			index = parts.length;

		if((index > 1) && (parts[0] == 'NetProfile'))
		{
			index -= 1;
			parts.shift();
		}
		if((index > 2) && (parts[0] == 'model'))
		{
			index -= 2;
			parts.splice(0, 2);
		}
		while(index-- > 1)
		{
			parts[index] = this.apply('capitalize', parts[index]);
		}

		return parts.join('');
	}
});

Ext.define('NetProfile.data.BaseModel', {
	extend: 'Ext.data.Model',
	requires: [ 'NetProfile.data.schema.Namer' ],
	schema: {
		namespace: 'NetProfile',
		namer:     'np'
	}
});

