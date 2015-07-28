/**
 * @class NetProfile.grid.ModelGrid
 * @extends Ext.grid.Panel
 */
Ext.define('NetProfile.grid.ModelGrid', {
	extend: 'Ext.grid.Panel',
	alias: 'widget.modelgrid',
	requires: [
		'Ext.grid.*',
		'Ext.data.*',
		'Ext.util.*',
		'Ext.state.*',
		'Ext.form.*',
		'Ext.menu.*',
		'Ext.toolbar.Paging',
		'Ext.toolbar.TextItem',
		'Ext.window.MessageBox',
		'Ext.event.Event',
		'NetProfile.grid.column.EnumColumn',
		'NetProfile.form.field.DateTime',
		'NetProfile.form.field.IPv4',
		'NetProfile.form.field.IPv6',
		'NetProfile.form.field.Password',
		'NetProfile.form.DynamicCheckboxGroup',
		'Ext.ux.form.TinyMCETextArea',
		'NetProfile.window.CenterWindow',
		'NetProfile.form.field.ModelSelect',
		'NetProfile.form.field.SimpleModelSelect',
		'NetProfile.form.field.FileSelect',
		'NetProfile.form.field.NullableComboBox',
		'NetProfile.panel.Wizard',
		'NetProfile.grid.filters.filter.Date',
		'NetProfile.grid.filters.filter.Number',
		'NetProfile.grid.filters.filter.List',
		'NetProfile.grid.filters.filter.IPv4',
		'NetProfile.grid.filters.filter.IPv6',
		'NetProfile.grid.plugin.SimpleSearch',
		'NetProfile.grid.plugin.ExtraSearch'
	],
	rowEditing: false,
	simpleSearch: false,
	extraSearch: null,
	actionCol: true,
	propBar: true,
	selectRow: false,
	selectField: null,
	selectIdField: null,
	extraParams: null,
	extraParamProp: null,
	extraParamRelProp: null,
	apiModule: null,
	apiClass: null,
	detailPane: null,
	hideColumns: null,
	createControllers: null,
	canCreate: false,
	canEdit: false,
	canDelete: false,
	canExport: true,
	border: 0,
	scrollable: 'vertical',
	extraActions: [],

	emptyText: 'Sorry, but no items were found.',
	clearText: 'Clear',
	clearTipText: 'Clear filtering and sorting.',
	addText: 'Add',
	addTipText: 'Add new object.',
	addWindowText: 'Add new object',
	propTipText: 'Display object properties',
	deleteTipText: 'Delete object',
	deleteMsgText: 'Are you sure you want to delete this object?',
	actionTipText: 'Object actions',
	exportText: 'Export',

	viewConfig: {
		stripeRows: true
	},
	initComponent: function()
	{
		var create_kmap = false,
			kmap_binds, plugins;

		this._create_ctl = {};
		this.tabConfig = { cls: 'record-tab-hdl' };
		if(this.selectRow)
		{
			this.canCreate = false;
			this.canEdit = false;
			this.canDelete = false;
		}
		if(!this.detailPane)
			this.rowEditing = true;
		if(!this.canEdit)
			this.rowEditing = false;
		if(this.plugins && this.plugins.length)
			plugins = Ext.Array.clone(this.plugins);
		else
			plugins = [{
				ptype: 'gridfilters',
				defaultFilterTypes: {
					'boolean' : 'boolean',
					'int'     : 'npnumber',
					'date'    : 'npdate',
					'number'  : 'npnumber'
				}
			}];
		if(this.simpleSearch)
			plugins.push({
				ptype: 'simplesearch'
			});
		if(this.extraSearch)
			plugins.push({
				ptype: 'extrasearch'
			});
		var tbitems = [{
			text: this.clearText,
			tooltip: { text: this.clearTipText, title: this.clearText },
			iconCls: 'ico-clear',
			handler: this.onPressReset,
			scope: this
		}];
		if(this.canCreate)
			tbitems.push({
				text: this.addText,
				tooltip: { text: this.addTipText, title: this.addText },
				iconCls: 'ico-add',
				itemId: 'addBtn',
				handler: function()
				{
					return this.spawnCreateWizard();
				},
				scope: this
			});
		if(this.canExport)
			tbitems.push({
				iconCls: 'ico-download',
				text: this.exportText,
				menu: { xtype: 'exportmenu' }
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
			Ext.Array.forEach(this.columns, function(col)
			{
				if(col.xtype == 'actioncolumn')
					has_action = true;
			}, this);
			if(!has_action)
			{
				var i = [];
				if(this.detailPane)
					i.push({
						iconCls: 'ico-props',
						tooltip: this.propTipText,
						handler: function(grid, rowidx, colidx, item, e, record)
						{
							return this.selectRecord(record);
						},
						scope: this
					});
				if(this.extraActions && this.extraActions.length)
				{
					var extra_i = [];
					var ea_handler = function(grid, rowidx, colidx, item, e, record)
					{
						if(item && item.itemId && grid && grid.ownerCt)
							grid.ownerCt.fireEvent('action_' + item.itemId, grid, item, e, record);
						return true;
					};

					Ext.Array.forEach(this.extraActions, function(ea)
					{
						ea.scope = this;
						ea.handler = ea_handler;
						extra_i.push(ea);
					}, this);
					i = i.concat(extra_i);
				}
				if(this.canDelete)
					i.push({
						iconCls: 'ico-delete',
						tooltip: this.deleteTipText,
						handler: function(grid, rowidx, colidx, item, e, record)
						{
							if(this.store)
								Ext.MessageBox.confirm(
									this.deleteTipText,
									Ext.String.format('{0}<div class="np-object-frame">{1}</div>', this.deleteMsgText, record.get('__str__')),
									function(btn)
									{
										if(btn === 'yes')
										{
											if(record.store && record.store.getById(record.getId()))
											{
												var st = record.store;
												st.remove(record);
											}
											else if(this.store.getById(record.getId()))
												this.store.remove(record);
											else
												record.erase();
										}
										return true;
									},
									this
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
						tooltip: this.actionTipText
					});
			}
		}
		if(this.rowEditing)
			plugins.push({
				ptype: 'rowediting',
				autoCancel: true,
				clicksToEdit: 2,
				clicksToMoveEditor: 1
			});

		if(!this.store && this.apiModule && this.apiClass)
			this.store = NetProfile.StoreManager.getStore(this.apiModule, this.apiClass, this, !this.stateful);

		// This is a hack to apply all plugin state/listeners before
		// gridfilters forces our store to load.
		plugins.reverse();

		this.plugins = plugins;
		this.callParent();

		this.addDocked({
			xtype: 'pagingtoolbar',
			dock: 'bottom',
			store: this.store,
			displayInfo: NetProfile.userSettings.datagrid_showrange
		});

		this._scrollDelta = 0;
		this.scrollPager = new Ext.util.DelayedTask(this.onPageScroll, this);

		this.on({
			beforedestroy: function(grid)
			{
				if(this._create_ctl.length > 0)
				{
					Ext.destroy(this._create_ctl);
					this._create_ctl = [];
				}
				if(this.kmap)
				{
					this.kmap.destroy();
					this.kmap = null;
				}
			},
			beforerender: function(grid)
			{
				var st = this.getStore();

				if(st && !st.isLoaded() && !st.isLoading())
					st.load();

				Ext.Array.forEach(this.columns, function(col)
				{
					if(grid.hideColumns && Ext.Array.contains(grid.hideColumns, col.dataIndex))
						col.hidden = true;
				});
			},
			afterrender: function(grid)
			{
				grid.on('wheel', function(ev)
				{
					var delta;

					if(ev.altKey)
					{
						ev.stopEvent();
						if(Ext.isGecko)
							delta = -ev.browserEvent.deltaY;
						else
							delta = ev.getWheelDelta();
						if(ev.ctrlKey)
							delta *= 1000;
						grid._scrollDelta += delta;
						grid.scrollPager.delay(70);
					}
				}, grid, { element: 'body' });
			},
			selectionchange: function(sel, recs, opts)
			{
				if(this.selectRow) // FIXME: add a way to open objects from modelselect
					return true;
				if(!sel.hasSelection() || (sel.getSelectionMode() != 'SINGLE'))
					return true;
				if(!recs || !recs.length)
					return true;
				return this.selectRecord(recs[0]);
			},
			beforeitemdblclick: function(view, record, item, idx, ev, opts)
			{
				if(this.selectRow)
				{
					if(this.selectIdField)
					{
						if(Ext.isString(this.selectIdField))
						{
							var form = this.selectField.up('form'),
								rec = form.getRecord();
							if(rec)
								rec.set(this.selectIdField, record.getId());
							else if(this.selectField.hiddenField)
								form.getForm().findField(this.selectField.hiddenField).setValue(record.getId());
							else
								form.getForm().findField(this.selectIdField).setValue(record.getId());
						}
						else
							this.selectIdField.setValue(record.getId());
					}
					if(this.selectField)
						this.selectField.setValue(record.get('__str__'));
					this.up('window').close();
				}
				else
					this.selectRecord(record);
				return true;
			},
			scope: this
		});

		if(this.id === 'main_content')
			create_kmap = true;
		if(create_kmap)
		{
			kmap_binds = [{
				key: 'r',
				fn: function(kc, ev)
				{
					if(ev.altKey)
					{
						ev.stopEvent();
						this.onPressReset();
					}
				},
				scope: this
			}];
			if(this.simpleSearch)
				kmap_binds.push({
					key: 's',
					fn: function(kc, ev)
					{
						var fld;

						if(ev.altKey)
						{
							fld = this.down('textfield[cls~=np-ssearch-field]');
							if(fld)
							{
								ev.stopEvent();
								fld.focus();
								fld.selectText();
							}
						}
					},
					scope: this
				});
			if(this.canCreate)
				kmap_binds.push({
					key: 'c',
					fn: function(kc, ev)
					{
						if(ev.altKey && this.canCreate)
							this.spawnCreateWizard();
					},
					scope: this
				});

			this.kmap = new Ext.util.KeyMap({
				target: Ext.getBody(),
				binding: kmap_binds
			});
		}
	},
	onPageScroll: function()
	{
		var me = this,
			store = me.getStore(),
			curpg = store.currentPage,
			maxpg = Math.ceil(store.getTotalCount() / store.getPageSize()),
			delta = me._scrollDelta || 0;

		me._scrollDelta = 0;

		if((delta > 0) && (curpg > 1))
		{
			if(delta >= 1000)
				store.loadPage(1);
			else
				store.previousPage();
		}
		else if((delta < 0) && (curpg < maxpg))
		{
			if(delta <= -1000)
				store.loadPage(maxpg);
			else
				store.nextPage();
		}
	},
	onPressReset: function()
	{
		store = this.getStore();
		store.blockLoad(); // undocumented API of Ext.data.ProxyStore
		store.lastExtraParams = {};
		if(this.filters)
			this.filters.clearFilters(true);
		if(this.ssearch)
			this.ssearch.clearValue(true);
		if(this.xsearch)
			this.xsearch.clearValue(true);
		store.sorters.clear();
		if(store.initialSorters && store.initialSorters.length)
			store.sorters.add(store.initialSorters);
		this.saveState();
		store.unblockLoad(); // undocumented API of Ext.data.ProxyStore
		store.loadPage(1);
		return true;
	},
	selectRecord: function(record)
	{
		var pb, dp, poly, api_mod, api_class;

		api_mod = this.apiModule;
		api_class = this.apiClass;
		dp = this.detailPane;
		poly = record.get('__poly');
		if(poly && ((api_mod !== poly[0]) || (api_class !== poly[1])))
		{
			api_mod = poly[0];
			api_class = poly[1];
			dp = NetProfile.view.grid[api_mod][api_class].prototype.detailPane;
			var ff,
				store = NetProfile.StoreManager.getStore(
					api_mod,
					api_class,
					null, true
				);
			if(!store)
				return false;
			ff = { __ffilter: [{
				property: store.model.prototype.idProperty,
				operator: 'eq',
				value:    parseInt(record.getId())
			}] };
			store.load({
				params: ff,
				callback: function(recs, op, success)
				{
					var pb;

					pb = Ext.getCmp('npws_propbar');
					if(success && pb && dp && (recs.length === 1))
					{
						pb.addRecordTab(api_mod, api_class, dp, recs[0]);
						pb.show();
					}
				},
				scope: this,
				synchronous: false
			});
			return true;
		}

		if(this.propBar && dp && !this.selectRow)
		{
			pb = Ext.getCmp('npws_propbar');
			if(!pb)
				return true;
			if(dp)
			{
				pb.addRecordTab(api_mod, api_class, dp, record);
				pb.show();

				var view = this.getView(),
					node = view.getNode(record);
				if(node)
					node.scrollIntoView();
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
	},
	spawnCreateWizard: function()
	{
		var me = this,
			wiz_win, wiz;

		if(!me.canCreate)
			return false;
		wiz_win = Ext.create('NetProfile.window.CenterWindow', {
			title: me.addWindowText,
			modal: true
		});
		wiz = Ext.create('NetProfile.panel.Wizard', {
			stateful: false,
			wizardCls: me.apiClass,
			createInto: me.store,
			actionApi: 'create_wizard_action'
		});
		if(me.createControllers)
		{
			Ext.require(
				me.createControllers,
				function()
				{
					var ctl = me.createControllers;

					if(Ext.isString(ctl))
						ctl = [ ctl ];
					if(Ext.isArray(ctl))
					{
						Ext.Array.forEach(ctl, function(cclass)
						{
							if(!(cclass in me._create_ctl))
								me._create_ctl[cclass] = Ext.create(cclass, {
									caller: me
								});
							if(me._create_ctl[cclass].observeWizard)
								me._create_ctl[cclass].observeWizard(wiz);
						});
					}
					wiz_win.add(wiz);
					wiz_win.show();
				}
			);
			return true;
		}
		wiz_win.add(wiz);
		wiz_win.show();

		return true;
	},
	spawnWizard: function(wname)
	{
		var wiz_win = Ext.create('NetProfile.window.CenterWindow', {
			title: 'FIXME',
			modal: true
		});
		var wiz = Ext.create('NetProfile.panel.Wizard', {
			stateful: false,
			wizardCls: this.apiClass,
			createInto: this.store,
			wizardName: wname,
			createApi: 'get_wizard',
			actionApi: 'wizard_action'
		});
		// Do these apply to non-create wizards?
		if(this.createControllers)
		{
			Ext.require(
				this.createControllers,
				function()
				{
					var ctl = this.createControllers,
						me = this;
					if(Ext.isString(ctl))
						ctl = [ ctl ];
					if(Ext.isArray(ctl))
					{
						Ext.Array.forEach(ctl, function(cclass)
						{
							if(!(cclass in me._create_ctl))
								me._create_ctl[cclass] = Ext.create(cclass, {
									caller: me
								});
							if(me._create_ctl[cclass].observeWizard)
								me._create_ctl[cclass].observeWizard(wiz);
						});
					}
					wiz_win.add(wiz);
					wiz_win.show();
				},
				this
			);
			return true;
		}
		wiz_win.add(wiz);
		wiz_win.show();

		return true;
	}
});

