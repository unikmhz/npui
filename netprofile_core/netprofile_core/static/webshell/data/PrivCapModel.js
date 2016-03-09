Ext.define('NetProfile.data.PrivCapModel', {
	extend: 'NetProfile.data.BaseModel',
	fields: [{
		name: 'privid',
		type: 'int',
		allowNull: false,
		allowBlank: false
	}, {
		name: 'owner',
		type: 'int',
		userNull: false,
		allowBlank: false
	}, {
		name: 'code',
		type: 'string',
		allowNull: false,
		allowBlank: false
	}, {
		name: 'name',
		type: 'string',
		allowNull: false,
		allowBlank: false,
		persist: false
	}, {
		name: 'prefix',
		type: 'string',
		allowNull: false,
		allowBlank: false,
		persist: false,
		calculate: function(data)
		{
			return data.name.split(':')[0];
		}
	}, {
		name: 'suffix',
		type: 'string',
		allowNull: false,
		allowBlank: false,
		persist: false,
		calculate: function(data)
		{
			var nparts = data.name.split(':', 2);
			if(nparts && (nparts.length === 2))
				return Ext.String.trim(nparts[1]);
			return data.name;
		}
	}, {
		name: 'hasacls',
		type: 'boolean',
		allowNull: false,
		allowBlank: false,
		persist: false
	}, {
		name: 'value',
		type: 'boolean',
		allowNull: true,
		allowBlank: true
	}],
	idProperty: 'privid'
});

