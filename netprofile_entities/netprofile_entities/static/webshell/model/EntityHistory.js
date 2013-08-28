/**
 * @class NetProfile.entities.model.EntityHistory
 * @extends Ext.data.Model
 */
Ext.define('NetProfile.entities.model.EntityHistory', {
	extend: 'Ext.data.Model',
	fields: [
		{ name: 'time', type: 'date', dateFormat: 'c', useNull: false, allowBlank: false },
		{ name: 'author', type: 'string', useNull: true, allowBlank: true },
		{ name: 'title', type: 'string', useNull: true, allowBlank: true },
		{ name: 'parts', type: 'auto', useNull: true, allowBlank: true }
	]
});

