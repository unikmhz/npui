/**
 * @class NetProfile.form.field.Grid
 * @extends Ext.form.FieldContainer
 */
Ext.define('NetProfile.form.field.Grid', {
	extend: 'Ext.form.FieldContainer',
	mixins: {
		field: 'Ext.form.field.Field'
	},
	alias: 'widget.gridfield',
	requires: [
		'Ext.grid.Panel',
		'Ext.grid.column.Column',
		'Ext.grid.plugin.CellEditing',
		'Ext.grid.CellEditor',
		'Ext.data.ArrayStore'
	],

	addText: 'Add row',
	addTipText: 'Add new row.',
	deleteText: 'Delete row',
	deleteTipText: 'Delete selected row.',

	config: {
		gridCfg: {
			xtype: 'grid',
			store: {
				xtype: 'array'
			},
			height: 100,
			minHeight: 100,
			scrollable: 'vertical',
			resizable: true,
			plugins: {
				ptype: 'cellediting'
			}
		},
		layout: 'fit'
	},

	initComponent: function()
	{
		var me = this,
			grid_cfg = {};

		Ext.apply(grid_cfg, {
			itemId: 'grid'
		}, me.getGridCfg());

		grid_cfg.lbar = [{
			itemId: 'add',
			iconCls: 'ico-add',
			tooltip: { text: me.addTipText, title: me.addText },
			disabled: true,
			handler: 'onButtonAdd',
			scope: me
		}, {
			itemId: 'del',
			iconCls: 'ico-delete',
			tooltip: { text: me.deleteTipText, title: me.deleteText },
			disabled: true,
			handler: 'onButtonDelete',
			scope: me
		}];

		me.items = [grid_cfg];

		me.callParent();
	},
	getValue: function()
	{
		var me = this,
			grid = me.getComponent('grid'),
			store = grid.getStore(),
			ret = [];

		store.each(function(item)
		{
			ret.push(item.getData());
		});

		return ret;
	},
	setValue: function(val)
	{
		var me = this,
			grid = me.getComponent('grid'),
			store = grid.getStore();

		store.setData(val);
	}
});
