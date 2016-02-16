/**
 * @class NetProfile.devices.data.ProbeResultsModel
 * @extends NetProfile.data.BaseModel
 */
Ext.define('NetProfile.devices.data.ProbeResultsModel', {
	extend: 'NetProfile.data.BaseModel',
	fields: [
		{ name: 'hostid', },
		{ name: 'host', type: 'string', allowNull: false, allowBlank: false },
		{ name: 'addrid', },
		{ name: 'addrtype', type: 'string', allowNull: false, allowBlank: false },
		{ name: 'addr', type: 'string', allowNull: false, allowBlank: false },
		{ name: 'sent', type: 'int', allowNull: false, allowBlank: false, defaultValue: 0 },
		{ name: 'returned', type: 'int', allowNull: false, allowBlank: false, defaultValue: 0 },
		{ name: 'min', type: 'float', allowNull: true, allowBlank: true },
		{ name: 'max', type: 'float', allowNull: true, allowBlank: true },
		{ name: 'avg', type: 'float', allowNull: true, allowBlank: true },
		{ name: 'detected', type: 'boolean', allowNull: false, allowBlank: false, defaultValue: false }
	]
});

