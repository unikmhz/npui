/**
 * @class NetProfile.tree.Property
 * @extends Ext.tree.Panel
 */
Ext.define('NetProfile.tree.Property', {
	extend: 'Ext.tree.Panel',
	alias: 'widget.propertytree',
	requires: [
		'NetProfile.data.PropertyTreeStore'
	],

	initComponent: function()
	{
		var me = this;

		me.callParent();
	}
});

