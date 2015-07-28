/**
 * @class NetProfile.tree.FileFolder
 * @extends Ext.tree.Panel
 */
Ext.define('NetProfile.tree.FileFolder', {
	extend: 'Ext.tree.Panel',
	alias: 'widget.filefoldertree',
	requires: [
	],

	initComponent: function()
	{
		var me = this;

		me.store = Ext.create('NetProfile.store.menu.folders');
		me.callParent(arguments);
	}
});

