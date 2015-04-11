Ext.define('NetProfile.data.PrivCapStore', {
	extend: 'Ext.data.Store',
	requires: 'NetProfile.model.PrivCap',
	model: 'NetProfile.model.PrivCap',
	pageSize: -1,
	autoLoad: true,
	autoSync: true
});

