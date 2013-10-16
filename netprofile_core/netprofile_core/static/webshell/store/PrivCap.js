Ext.define('NetProfile.store.PrivCap', {
	extend: 'Ext.data.Store',
	requires: 'NetProfile.model.PrivCap',
	model: 'NetProfile.model.PrivCap',
	pageSize: -1,
	autoLoad: true,
	autoSync: true
});

