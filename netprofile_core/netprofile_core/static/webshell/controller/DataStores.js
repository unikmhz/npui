Ext.define('NetProfile.controller.DataStores', {
	extend: 'Ext.app.Controller',
	init: function()
	{
		this.stores = {};

		NetProfile.StoreManager = this;
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
				store.proxy.extraParams = { __ffilter: {} };
				if(this.extraParamRelProp)
					val = rec.get(this.extraParamRelProp);
				else
					val = rec.get(this.extraParamProp);
				store.proxy.extraParams.__ffilter[this.extraParamProp] = { eq: val };
			}
		}
	},
	getStore: function(module, model, grid, nocache, noautoload)
	{
		var me = this,
			store,
			store_cfg;

		if(!(module in this.stores))
			this.stores[module] = {};
		if((model in this.stores[module]) && !nocache)
		{
			store = this.stores[module][model];

			if(grid)
			{
				store.on('beforeload', this.onBeforeLoad, grid);
				if(grid.extraParams)
					store.proxy.extraParams = grid.extraParams;
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
			if(noautoload)
				store_cfg['autoLoad'] = false;
			if(grid)
			{
				store_cfg['listeners']['beforeload'] = {
					fn: this.onBeforeLoad,
					scope: grid
				};
				if(grid.extraParams)
					store_cfg['proxy']['extraParams'] = grid.extraParams;
			}

			var store = Ext.create(
				'NetProfile.store.' + module + '.' + model,
				store_cfg
			);
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

		if(store.sorters.getCount() > 0)
			store.initialSorters = store.sorters.getRange();

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
	}
});

