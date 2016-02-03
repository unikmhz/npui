/**
 * @class NetProfile.window.ReportsWindow
 * @extends Ext.window.Window
 */
Ext.define('NetProfile.window.ReportsWindow', {
	extend: 'Ext.window.Window',
	alias: 'widget.reportswindow',
	requires: [
//		'Ext.resizer.Splitter',
		'Ext.chart.*'
	],

	config: {
		shrinkWrap: 3,
		minHeight: 300,
		minWidth: 600,
		iconCls: 'ico-chart'
	},

	titleText: 'Report viewer',

	grid: null,
	store: null,

	initComponent: function()
	{
		var me = this;

		if(!me.store)
			me.store = me.grid.getStore();

		me.title = me.titleText;
		me.dockedItems = [{
			xtype: 'panel',
			dock: 'left',
			hidden: false,
			border: 0,
			padding: '0 4 0 0',
			width: 220,
			resizable: {
				handles: 'e',
				pinned: true
			},
			layout: {
				type: 'accordion',
				multi: false
			},
			itemId: 'leftbar',
			items: []
		}];
		me.items = [{
			xtype: 'panel'
		}];

		me.callParent();
	}
});

