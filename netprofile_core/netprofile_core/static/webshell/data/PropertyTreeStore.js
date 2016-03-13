/**
 * @class NetProfile.data.PropertyTreeStore
 * @extends Ext.data.TreeStore
 */
Ext.define('NetProfile.data.PropertyTreeStore', {
	extend: 'Ext.data.TreeStore',
	alias: 'store.proptree',
	model: 'NetProfile.data.PropertyTreeModel',
	requires: [
		'Ext.data.proxy.Memory'
	],
	autoLoad: true,
	autoSync: true,
	proxy: {
		type: 'memory'
	},
	root: {
		expanded: true
	}
});

