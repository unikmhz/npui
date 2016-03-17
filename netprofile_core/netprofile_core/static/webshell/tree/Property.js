/**
 * @class NetProfile.tree.Property
 * @extends Ext.tree.Panel
 */
Ext.define('NetProfile.tree.Property', {
	extend: 'Ext.tree.Panel',
	alias: 'widget.propertytree',
	requires: [
		'Ext.grid.column.Column',
		'Ext.tree.Column',
		'NetProfile.data.PropertyTreeStore'
	],

	propText: 'Property',
	typeText: 'Type',
	valueText: 'Value',

	initComponent: function()
	{
		var me = this;

		me.columns = [{
			xtype: 'treecolumn',
			text: me.propText,
			dataIndex: 'name'
		}, {
			xtype: 'gridcolumn',
			text: me.typeText,
			dataIndex: 'type'
		}, {
			xtype: 'gridcolumn',
			text: me.valueText,
			dataIndex: 'value'
		}];

		me.callParent();
	}
});

