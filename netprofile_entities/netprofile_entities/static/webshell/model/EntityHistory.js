/**
 * @class NetProfile.entities.model.EntityHistory
 * @extends Ext.data.Model
 */
Ext.define('NetProfile.entities.model.EntityHistory', {
	extend: 'Ext.data.Model',
	fields: [
		{ name: 'time', type: 'date', dateFormat: 'c', allowNull: false, allowBlank: false },
		{ name: 'author', type: 'string', allowNull: true, allowBlank: true },
		{ name: 'title', type: 'string', allowNull: true, allowBlank: true },
		{ name: 'parts', type: 'auto', allowNull: true, allowBlank: true }
	]
});

