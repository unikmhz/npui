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
		'Ext.window.MessageBox',
		'Ext.ux.grid.FiltersFeature',
		'Ext.ux.grid.SimpleSearchFeature',
		'Ext.ux.CheckColumn',
		'Ext.ux.EnumColumn',
		'Ext.ux.IPAddressColumn',
		'NetProfile.view.ModelSelect'
	],
	rowEditing: true,
	simpleSearch: false,
	actionCol: true,
	selectRow: false,
	selectField: null,
	selectIdField: null,
	extraParams: null,
	apiModule: null,
	apiClass: null,
	detailPane: null,
	canCreate: false,
	canEdit: false,
	canDelete: false,
	border: 0,
	emptyText: 'Sorry, but no items were found.',
	dockedItems: [],
	plugins: [],
	viewConfig: {
		stripeRows: true,
		plugins: []
	},
	initComponent: function() {
		if(this.selectRow)
		{
			this.canCreate = false;
			this.canEdit = false;
			this.canDelete = false;
		}
		if(!this.canEdit)
			this.rowEditing = false;
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
		var tbitems = [{
			text: 'Search',
			tooltip: { text: 'Additional search filters.', title: 'Search' },
			iconCls: 'ico-find',
			handler: function() {
				return true;
			},
			scope: this
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
				return true;
			},
			scope: this
		}];
		if(this.canCreate)
			tbitems.push({
				text: 'Add',
				tooltip: { text: 'Add new object.', title: 'Add' },
				iconCls: 'ico-add',
				handler: function() {
					return true;
				},
				scope: this
			});
		this.dockedItems = [{
			xtype: 'toolbar',
			dock: 'top',
			itemId: 'toolTop',
			items: tbitems
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
					iconCls: 'ico-props',
					tooltip: 'Display object properties',
					handler: function(grid, rowidx, colidx, item, e, record)
					{
						return this.selectRecord(record);
					},
					scope: this
				}];
				if(this.canDelete)
					i.push({
						iconCls: 'ico-delete',
						tooltip: 'Delete object',
						handler: function(grid, rowidx, colidx, item, e, record)
						{
							if(this.store)
								Ext.MessageBox.confirm(
									'Delete object',
									'Are you sure you want to delete this object?<div class="np-object-frame">' + record.get('__str__') + '</div>',
									function(btn)
									{
										if(btn === 'yes')
											this.store.remove(record);
										return true;
									}.bind(this)
								);
							return true;
						},
						scope: this
					});
				if(i.length > 0)
					this.columns.push({
						xtype: 'actioncolumn',
						width: i.length * 20,
						items: i,
						sortable: false,
						resizable: false,
						menuDisabled: true,
						tooltip: 'Object actions'
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

		var store_cfg = {
			autoDestroy: true,
			listeners: {}
		};
		var pb = Ext.getCmp('npws_propbar');
		if(pb && !this.selectRow)
			store_cfg['listeners']['load'] = {
				fn: function() {
					Ext.destroy(this.removeAll());
				},
				scope: pb
			};
		if(this.extraParams)
			store_cfg['proxy'] = {
				type: this.apiModule + '_' + this.apiClass,
				extraParams: this.extraParams
			};

		if(!this.store && this.apiModule && this.apiClass)
			this.store = Ext.create(
				'NetProfile.store.' + this.apiModule + '.' + this.apiClass,
				store_cfg
			);

		this.callParent();

		this.addDocked({
			xtype: 'pagingtoolbar',
			dock: 'bottom',
			store: this.store,
			displayInfo: true
		});

		this.on({
			selectionchange: function(sel, recs, opts) {
				if(!sel.hasSelection() || (sel.getSelectionMode() != 'SINGLE'))
					return true;
				if(!recs || !recs.length)
					return true;
				return this.selectRecord(recs[0]);
			},
			itemdblclick: function(view, record, item, idx, ev, opts)
			{
				if(this.selectRow)
				{
					if(this.selectIdField)
					{
						if(Ext.isString(this.selectIdField))
							this.selectField.up('form').getRecord().set(this.selectIdField, record.getId());
						else
							this.selectIdField.setValue(record.getId());
					}
					if(this.selectField)
						this.selectField.setValue(record.get('__str__'));
					this.up('window').close();
				}
				return true;
			},
			scope: this
		});
	},
	selectRecord: function(record)
	{
		if(this.detailPane && !this.selectRow)
		{
			var pb = Ext.getCmp('npws_propbar');
			if(!pb)
				return true;
			pb.setContext(this.apiModule, this.apiClass);
			if(this.detailPane)
			{
				pb.addRecordTab(this.detailPane, record);
				pb.show();

				var view = this.getView(),
					node = view.getNode(record);
				if(node)
					node.scrollIntoView(view);
			}
		}
		return true;
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

