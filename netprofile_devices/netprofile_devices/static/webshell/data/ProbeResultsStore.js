/**
 * @class NetProfile.devices.data.ProbeResultsStore
 * @extends Ext.data.Store
 */
Ext.define('NetProfile.devices.data.ProbeResultsStore', {
	extend: 'Ext.data.Store',
	requires: 'NetProfile.devices.data.ProbeResultsModel',
	model: 'NetProfile.devices.data.ProbeResultsModel',
	sorters: [{
		direction: 'ASC',
		property: 'addr'
	}],
	remoteFilter: false,
	remoteSort: false,
	storeId: 'npstore_devices_ProbeResults',
	autoLoad: false,
	autoSync: false
});

