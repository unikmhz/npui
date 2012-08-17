Ext.define('NetProfile.store.ModelStore', {
	extend: 'Ext.data.DirectStore',
	buffered: true,
	remoteSort: true,
	autoLoad: true,
	root: 'records',
	idProperty: 'id',
	totalProperty: 'total'
});

