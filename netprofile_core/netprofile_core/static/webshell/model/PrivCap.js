Ext.define('NetProfile.model.PrivCap', {
	extend: 'Ext.data.Model',
	fields: [{
		name: 'privid',
		type: 'int',
		useNull: false,
		allowBlank: false
	}, {
		name: 'owner',
		type: 'int',
		userNull: false,
		allowBlank: false
	}, {
		name: 'code',
		type: 'string',
		useNull: false,
		allowBlank: false
	}, {
		name: 'name',
		type: 'string',
		useNull: false,
		allowBlank: false,
		persist: false
	}, {
		name: 'hasacls',
		type: 'boolean',
		useNull: false,
		allowBlank: false,
		persist: false
	}, {
		name: 'value',
		type: 'boolean',
		useNull: true,
		allowBlank: true
	}],
	idProperty: 'privid'
});

