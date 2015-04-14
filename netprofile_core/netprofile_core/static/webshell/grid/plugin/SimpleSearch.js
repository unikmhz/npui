Ext.define('NetProfile.grid.plugin.SimpleSearch', {
	extend: 'Ext.plugin.Abstract',
	alias: 'plugin.simplesearch',
	pluginId: 'simplesearch',
	requires: [
		'Ext.form.field.Text',
		'Ext.util.DelayedTask'
	],

	fieldEmptyText: 'Search...',
	autoReload: true,
	paramPrefix: '__sstr',
	updateBuffer: 500,

	constructor: function(config)
	{
		var me = this;
			config = config || {};

		Ext.apply(me, config);
		me.value = null;
		me.deferredUpdate = Ext.create('Ext.util.DelayedTask', me.reload, me);
	},
	init: function(grid)
	{
		var me = this,
			store = grid.getStore();

		me.grid = grid;
		me.field = null;
		grid.ssearch = me;
		me.createField();
		me.bindStore(store);
		me.gridListeners = {
			scope: me,
			beforestaterestore: me.applyState,
			beforestatesave: me.saveState
		};
		grid.on(me.gridListeners);
	},
	createField: function()
	{
		var me = this,
			grid = me.grid,
			topdock = grid.getDockedComponent('toolTop'),
			config;

		config = {
			cls: 'np-ssearch-field',
			iconCls: me.iconCls,
			emptyText: me.fieldEmptyText,
			hideLabel: true,
			listeners: {
				scope: me,
				change: function(field, newval, oldval)
				{
					var grid;

					// save grid state
					if(!this.applyingState)
					{
						this.value = newval;
						grid = this.grid;
						grid.saveState();
						grid.fireEvent('ssearchupdate', this, newval);
					}
					// restart the timer
					if(this.autoReload)
						this.deferredUpdate.delay(this.updateBuffer);
				}
			},
			value: me.value
		};
		me.field = Ext.create('Ext.form.field.Text', config);
		topdock.add(['->', me.field]);
	},
	getValue: function()
	{
		return this.value;
	},
	setValue: function(value)
	{
		var me = this,
			field = me.field;

		me.value = value;
		if(field)
			field.setValue(value);
	},
	clearValue: function(suppressEvent)
	{
		var me = this,
			field = me.field;

		me.value = null;
		if(field)
		{
			if(suppressEvent)
				field.suspendEvents();
			field.setValue('');
			if(suppressEvent)
				field.resumeEvents();
		}
	},
	applyState: function(grid, state)
	{
		var me = this;

		me.applyingState = true;
		if(state.sstr)
			me.setValue(state.sstr);
		else
			me.clearValue();
		me.deferredUpdate.cancel();

		delete me.applyingState;
		delete state.sstr;
	},
	saveState: function(grid, state)
	{
		var me = this,
			field = me.field;

		if(field && !field.isDisabled())
		{
			state.sstr = field.getValue();
			return true;
		}
		return false;
	},
	destroy: function()
	{
		var me = this,
			grid = me.grid;

		me.bindStore(null);
		if(grid.ssearch)
			grid.ssearch = null;
		grid.un(me.gridListeners);
		Ext.destroyMembers(me, 'field');
		me.value = null;
		me.grid = null;
		me.gridListeners = null;
	},
	bindStore: function(store)
	{
		var me = this;

		// Unbind from the old Store
		if(me.store && me.storeListeners)
			me.store.un(me.storeListeners);
		// Set up correct listeners
		if(store)
		{
			me.storeListeners = {
				scope: me,
				beforeload: me.onBeforeLoad
			};
			store.on(me.storeListeners);
		}
		else
			delete me.storeListeners;
		me.store = store;
	},
	onBeforeLoad: function(store, oper)
	{
		var me = this,
			params = oper.getParams() || {},
			sstr = me.getValue();

		store.lastExtraParams = store.lastExtraParams || {};
		if(me.paramPrefix in params)
			delete params[me.paramPrefix];
		if(me.paramPrefix in store.lastExtraParams)
			delete store.lastExtraParams[me.paramPrefix];
		if(sstr)
		{
			params[me.paramPrefix] = sstr;
			store.lastExtraParams[me.paramPrefix] = sstr;
		}
		oper.setParams(params);
	},
	reload: function()
	{
		var me = this,
			store = me.grid.getStore();

		me.deferredUpdate.cancel();
		store.loadPage(1);
	}
});

