/**
 * @class NetProfile.view.ModelGrid
 * @extends Ext.grid.Panel
 */
Ext.define('NetProfile.view.ModelGrid', {
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
		'Ext.EventObject',
		'Ext.ux.grid.FiltersFeature',
		'Ext.ux.grid.SimpleSearchFeature',
		'Ext.ux.grid.ExtraSearchFeature',
		'Ext.ux.CheckColumn',
		'Ext.ux.EnumColumn',
		'Ext.ux.IPAddressColumn',
		'Ext.ux.form.field.DateTime',
		'Ext.ux.form.field.IPv4',
		'Ext.ux.form.field.Password',
		'Ext.ux.form.DynamicCheckboxGroup',
		'Ext.ux.form.TinyMCETextArea',
		'Ext.ux.window.CenterWindow',
		'Ext.ux.RowExpander',
		'NetProfile.view.ModelSelect',
		'NetProfile.view.SimpleModelSelect',
		'NetProfile.view.NullableComboBox'
	],
	rowEditing: true,
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
	border: 0,

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

	dockedItems: [],
	plugins: [],
	viewConfig: {
		stripeRows: true,
		plugins: []
	},
	initComponent: function()
	{
		this._create_ctl = {};
		this.tabConfig = { cls: 'record-tab-hdl' };
		if(this.selectRow)
		{
			this.canCreate = false;
			this.canEdit = false;
			this.canDelete = false;
		}
		if(!this.canEdit)
			this.rowEditing = false;
		if(!this.features)
			this.features = [];
		this.features.push({
			ftype: 'filters',
			multi: true,
			encode: false,
			local: false
		});
		if(this.extraSearch)
			this.features.push({
				ftype: 'extrasearch',
				local: false
			});
		if(this.simpleSearch)
			this.features.push({
				ftype: 'simplesearch',
				local: false
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
					var wiz_win = Ext.create('Ext.ux.window.CenterWindow', {
						title: this.addWindowText,
						modal: true
					});
					var wiz = Ext.create('NetProfile.view.Wizard', {
						stateful: false,
						wizardCls: this.apiClass,
						createInto: this.store,
						actionApi: 'create_wizard_action'
					});
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
			Ext.Array.forEach(this.columns, function(col)
			{
				if(col.xtype == 'actioncolumn')
					has_action = true;
			}, this);
			if(!has_action)
			{
				var i = [{
					iconCls: 'ico-props',
					tooltip: this.propTipText,
					handler: function(grid, rowidx, colidx, item, e, record)
					{
						return this.selectRecord(record);
					},
					scope: this
				}];
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
												record.destroy();
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
			this.plugins.push({
				ptype: 'rowediting',
				autoCancel: true,
				clicksToEdit: 2,
				clicksToMoveEditor: 1
			});

		if(!this.store && this.apiModule && this.apiClass)
			this.store = NetProfile.StoreManager.getStore(this.apiModule, this.apiClass, this, !this.stateful);

		this.callParent();

		this.addDocked({
			xtype: 'pagingtoolbar',
			dock: 'bottom',
			store: this.store,
			displayInfo: NetProfile.userSettings.datagrid_showrange
		});

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
				Ext.Array.forEach(this.columns, function(col)
				{
					if(grid.hideColumns && Ext.Array.contains(grid.hideColumns, col.dataIndex))
						col.hidden = true;
				});
			},
			selectionchange: function(sel, recs, opts)
			{
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
					return false;
				}
				return true;
			},
			scope: this
		});

		var kmap_binds = [{
			key: Ext.EventObject.LEFT,
			fn: function(kc, ev)
			{
				var st = this.getStore();

				if(st && ev.ctrlKey)
				{
					ev.stopEvent();
					if(st.currentPage > 1)
					{
						if(ev.shiftKey)
							st.loadPage(1);
						else
							st.previousPage();
					}
				}
			},
			scope: this
		}, {
			key: Ext.EventObject.RIGHT,
			fn: function(kc, ev)
			{
				var st = this.getStore(),
					maxpg = Math.ceil(st.getTotalCount() / st.pageSize);

				if(st && ev.ctrlKey)
				{
					ev.stopEvent();
					if(st.currentPage < maxpg)
					{
						if(ev.shiftKey)
							st.loadPage(maxpg);
						else
							st.nextPage();
					}
				}
			},
			scope: this
		}, {
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

		this.kmap = new Ext.util.KeyMap({
			target: Ext.getBody(),
			binding: kmap_binds
		});
	},
	onPressReset: function()
	{
		store = this.getStore();
		if(this.filters)
			this.filters.clearFilters(true);
		if(this.ssearch)
			this.ssearch.clearValue(true);
		if(this.xsearch)
			this.xsearch.clearValue(true);
		store.sorters.clear();
		if(store.initialSorters)
			store.sorters.addAll(store.initialSorters);
		this.saveState();
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
					null, true, true
				);
			if(!store)
				return false;
			ff = { __ffilter: {} };
			ff.__ffilter[store.model.prototype.idProperty] = { eq: parseInt(record.getId()) };
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
	spawnWizard: function(wname)
	{
		var wiz_win = Ext.create('Ext.ux.window.CenterWindow', {
			title: 'FIXME',
			modal: true
		});
		var wiz = Ext.create('NetProfile.view.Wizard', {
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

