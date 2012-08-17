Ext.define('NetProfile.view.ModelGrid', {
	extend: 'Ext.grid.Panel',
	alias: 'widget.modelgrid',
	requires: [
		'Ext.grid.*',
		'Ext.data.*',
		'Ext.util.*',
		'Ext.state.*',
		'Ext.form.*',
		'Ext.toolbar.Paging',
		'Ext.toolbar.TextItem',
		'Ext.ux.grid.FiltersFeature',
		'Ext.ux.grid.SimpleSearchFeature',
		'Ext.ux.CheckColumn',
		'Ext.ux.EnumColumn',
		'NetProfile.view.ModelSelect'
	],
	rowEditing: true,
	simpleSearch: false,
	actionCol: true,
	selectRow: false,
//	parentGrid: null,
	apiModule: null,
	apiClass: null,
	border: 0,
//	features: [{
//	}],
	dockedItems: [],
	plugins: [],
	viewConfig: {
		stripeRows: true,
		plugins: []
	},
	initComponent: function() {
		this.features = [{
			ftype: 'filters',
			multi: true,
			encode: false,
			local: false
		}];
		if(this.simpleSearch)
			this.features.push({
				ftype: 'simplesearch',
				multi: true,
				encode: false,
				local: false
			});
		this.dockedItems = [{
			xtype: 'toolbar',
			dock: 'top',
			itemId: 'toolTop',
			items: [{
				text: 'Search',
				tooltip: { text: 'Additional search filters.', title: 'Search' },
				iconCls: 'ico-find'
			}, {
				text: 'Clear',
				tooltip: { text: 'Clear filtering and sorting.', title: 'Clear' },
				iconCls: 'ico-clear',
				handler: function() {
					store = this.getStore();
					if(this.filters)
						this.filters.clearFilters(true);
					if(this.ssearch)
						this.ssearch.clearValue(true);
					store.sorters.clear();
					this.saveState();
					store.loadPage(1);
				},
				scope: this
			}]
		}];
		if(this.actionCol)
		{
			var has_action = false;
			this.columns.forEach(function(col) {
				if(col.xtype == 'actioncolumn')
					has_action = true;
			});
			if(!has_action)
			{
				var i = [{
					icon: '/static/core/img/props.png',
					tooltip: 'Display object properties',
					handler: function(grid, rowidx, colidx, item, e, record)
					{
						var pb = Ext.getCmp('npws_propbar');
						pb.show();
					}
				}];
				this.columns.push({
					xtype: 'actioncolumn',
					width: i.length * 20,
					items: i,
					sortable: false,
					resizable: false,
					menuDisabled: true
				});
			}
		}
		this.plugins = [];
		if(this.rowEditing)
			this.plugins.push({
				ptype: 'rowediting',
				autoCancel: true,
				clicksToEdit: 2,
				clicksToMoveEditor: 1
			});

		if(!this.store && this.apiModule && this.apiClass)
			this.store = Ext.create('NetProfile.store.' + this.apiModule + '.' + this.apiClass, {
				autoDestroy: true
			});

		this.callParent();

		this.addDocked({
			xtype: 'pagingtoolbar',
			dock: 'bottom',
			store: this.store,
			displayInfo: true
		});
	},
	applyState: function(state)
	{
		var me = this,
			columns = me.columns;
		me.fstate = state;
		me.callParent(arguments);
		me.columns = columns;
	}
});

