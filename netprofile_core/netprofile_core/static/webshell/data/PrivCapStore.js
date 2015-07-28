Ext.define('NetProfile.data.PrivCapStore', {
	extend: 'Ext.data.Store',
	requires: 'NetProfile.data.PrivCapModel',
	model: 'NetProfile.data.PrivCapModel',
	pageSize: -1,
	autoLoad: true,
	autoSync: true
});

