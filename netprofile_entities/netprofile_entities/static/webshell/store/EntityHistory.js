/**
 * @class NetProfile.entities.store.EntityHistory
 * @extends Ext.data.Store
 */
Ext.define('NetProfile.entities.store.EntityHistory', {
	extend: 'Ext.data.Store',
	requires: 'NetProfile.entities.model.EntityHistory',
	model: 'NetProfile.entities.model.EntityHistory',
	sorters: [{
		direction: 'DESC',
		property: 'time'
	}],
	remoteFilter: true,
	remoteGroup: true,
	remoteSort: true,
	storeId: 'npstore_entities_EntityHistory',
	autoLoad: false,
	autoSync: false
});

