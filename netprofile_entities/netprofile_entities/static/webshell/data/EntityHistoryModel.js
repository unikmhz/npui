/**
 * @class NetProfile.entities.data.EntityHistoryModel
 * @extends NetProfile.data.BaseModel
 */
Ext.define('NetProfile.entities.data.EntityHistoryModel', {
	extend: 'NetProfile.data.BaseModel',
	fields: [
		{ name: 'time', type: 'date', dateFormat: 'c', allowNull: false, allowBlank: false },
		{ name: 'author', type: 'string', allowNull: true, allowBlank: true },
		{ name: 'title', type: 'string', allowNull: true, allowBlank: true },
		{ name: 'parts', type: 'auto', allowNull: true, allowBlank: true }
	]
});

