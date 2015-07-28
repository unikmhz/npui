Ext.define('NetProfile.controller.DataStores', {
	extend: 'Ext.app.Controller',
	requires: [
		'Ext.data.operation.Read'
	],
	init: function()
	{
		this.stores = {};
		this.cons_stores = {};

		NetProfile.StoreManager = this;

		this.control({
			'button[cls~=np-data-export]': {
				click: this.onDataExport
			},
			'checkcolumn' : {
				beforecheckchange: this.onCheckColumn
			}
		});
	},
	onCheckColumn: function(col, idx, checked)
	{
		if(col.readOnly)
			return false;
		return true;
	},
	onDataExport: function(btn, ev, opts)
	{
		var form = btn.up('form'),
			grid = form.up('grid'),
			store = grid.getStore(),
			proxy = store.getProxy(),
			oper, params, form_params, format;

		if(!store.lastOptions)
			return; // FIXME: report error
		oper = new Ext.data.operation.Read(store.lastOptions);
		params = proxy.getParams(oper);
		if(store.lastExtraParams)
			Ext.apply(params, store.lastExtraParams);
		format = form.itemId;
		form_params = form.getValues();
		if(form_params)
			Ext.apply(params, form_params);
		Ext.getCmp('npws_filedl').loadExport(grid.apiModule, grid.apiClass, format, params);
	},
	onBeforeLoad: function(store, op)
	{
		var rec,
			store,
			val;

		if(!this.extraParams && this.extraParamProp)
		{
			rec = this.up('panel[cls~=record-tab]');
			if(rec)
			{
				rec = rec.record;
				store = this.getStore();
				store.proxy.extraParams = { __ffilter: [] };
				if(this.extraParamRelProp)
					val = rec.get(this.extraParamRelProp);
				else
					val = rec.get(this.extraParamProp);
				store.proxy.extraParams.__ffilter.push({
					property: this.extraParamProp,
					operator: 'eq',
					value:    val
				});
			}
		}
	},
	getStore: function(module, model, grid, nocache, static_extra)
	{
		var me = this,
			store,
			store_cfg;

		static_extra = static_extra || {};
		if(!(module in this.stores))
			this.stores[module] = {};
		if((model in this.stores[module]) && !nocache)
		{
			store = this.stores[module][model];

			if(grid)
			{
				store.on('beforeload', this.onBeforeLoad, grid);
				if(grid.extraParams)
					Ext.apply(static_extra, grid.extraParams);
				store.proxy.extraParams = static_extra;
			}
		}
		else
		{
			store_cfg = {
				autoDestroy: false,
				listeners: {},
				proxy: {
					type: module + '_' + model
				}
			};
			if(grid)
			{
				store_cfg['listeners']['beforeload'] = {
					fn: this.onBeforeLoad,
					scope: grid
				};
				if(grid.extraParams)
					Ext.apply(static_extra, grid.extraParams);
			}
			store_cfg['proxy']['extraParams'] = static_extra;

			var store = Ext.create(
				'NetProfile.store.' + module + '.' + model,
				store_cfg
			);

			if(store.sorters && store.sorters.length)
			{
				store.initialSorters = [];
				store.sorters.each(function(isort)
				{
					store.initialSorters.push({
						'property'  : isort.getProperty(),
						'direction' : isort.getDirection()
					});
				});
			}
		}
		if(!store)
			throw 'Unable to create store for ' + module + ' ' + model;

		if(grid)
		{
			grid.on('beforedestroy', function()
			{
				var store = grid.getStore();
				store.removeListener('beforeload', me.onBeforeLoad, grid);
			});
		}

		store.on('update', function(store, rec, op, opts)
		{
			if(op == Ext.data.Model.COMMIT)
				NetProfile.StoreManager.refreshRelated(module, model, rec.getId(), store);
			return true;
		});

		if(!nocache)
			this.stores[module][model] = store;
		return store;
	},
	refreshRelated: function(module, model, rid, except)
	{
		if(!(module in NetProfile.StoreManager.stores))
			return;
		Ext.Object.each(NetProfile.StoreManager.stores[module], function(k, v)
		{
			if(v === except)
				return;
			if((k == model) && v.getById(rid))
				v.reload();
		});
	},
	getConsoleStore: function(type, id)
	{
		var str_id = 'cons:' + type + ':' + id,
			store = null;

		if(str_id in this.cons_stores)
			return this.cons_stores[str_id];
		else
			store = Ext.data.StoreManager.lookup(str_id);
		if(!store)
		{
			store = Ext.create('Ext.data.Store', {
				model: 'NetProfile.model.ConsoleMessage',
				storeId: str_id,
				autoLoad: true,
				autoSync: true,
				remoteFilter: false,
				remoteSort: false,
				sorters: [{
					direction: 'ASC',
					property: 'ts'
				}],
				proxy: {
					type: 'sessionstorage',
					id: str_id
				}
			});
			store.on('datachanged', function(st)
			{
				var total = st.getCount(),
					maxmsg = 50; // FIXME: make configurable

				if(total > maxmsg)
					st.removeAt(0, total - maxmsg);
			});
		}
		this.cons_stores[str_id] = store;
		return store;
	}
});

