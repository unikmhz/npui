/**
 * @class NetProfile.entities.data.EntityHistoryStore
 * @extends Ext.data.Store
 */
Ext.define('NetProfile.entities.data.EntityHistoryStore', {
	extend: 'Ext.data.Store',
	requires: 'NetProfile.entities.data.EntityHistoryModel',
	model: 'NetProfile.entities.data.EntityHistoryModel',
	sorters: [{
		direction: 'DESC',
		property: 'time'
	}],
	remoteFilter: true,
	remoteSort: true,
	storeId: 'npstore_entities_EntityHistory',
	autoLoad: false,
	autoSync: false
});

