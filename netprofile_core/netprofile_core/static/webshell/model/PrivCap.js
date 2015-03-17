Ext.define('NetProfile.model.PrivCap', {
	extend: 'Ext.data.Model',
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

