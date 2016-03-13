/**
 * @class NetProfile.data.PropertyTreeModel
 * @extends Ext.data.TreeModel
 */
Ext.define('NetProfile.data.PropertyTreeModel', {
	extend: 'Ext.data.TreeModel',
	fields: [{
		name: 'name',
		type: 'string',
		allowNull: false,
		allowBlank: false
	}, {
		name: 'type',
		type: 'string',
		allowNull: false,
		allowBlank: false
	}, {
		name: 'value',
		type: 'auto',
		allowNull: true,
		allowBlank: true
	}]
});

