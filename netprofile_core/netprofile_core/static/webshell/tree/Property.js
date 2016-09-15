/**
 * @class NetProfile.tree.Property
 * @extends Ext.tree.Panel
 */
Ext.define('NetProfile.tree.Property', {
	extend: 'Ext.tree.Panel',
	alias: 'widget.propertytree',
	requires: [
		'Ext.grid.column.Column',
		'Ext.grid.plugin.CellEditing',
		'Ext.grid.CellEditor',
		'Ext.tree.Column',
		'Ext.form.field.Text',
		'Ext.form.field.Number',
		'Ext.form.field.ComboBox',
		'NetProfile.data.PropertyTreeStore'
	],

	propText: 'Property',
	typeText: 'Type',
	valueText: 'Value',

	config: {
		rootType: 'object'
	},

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

		if(!me.store)
		{
			me.store = Ext.create('NetProfile.data.PropertyTreeStore', {
				root: {
					expanded: true,
					type: me.getRootType()
				}
			});
		}

		me.callParent();
	}
});

