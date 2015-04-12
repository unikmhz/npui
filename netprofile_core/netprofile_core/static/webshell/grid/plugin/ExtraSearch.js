Ext.define('NetProfile.grid.plugin.ExtraSearch', {
	extend: 'Ext.plugin.Abstract',
	alias: 'plugin.extrasearch',
	pluginId: 'extrasearch',
	requires: [
		'Ext.button.Button',
		'Ext.form.Panel',
		'Ext.layout.container.Accordion',
		'Ext.menu.Menu',
		'Ext.util.DelayedTask'
	],

	searchText: 'Search',
	searchTipText: 'Additional search filters.',
	advSearchText: 'Advanced search',
	clearText: 'Clear',

	autoReload: true,
	paramPrefix: '__xfilter',
	updateBuffer: 500,

	constructor: function(config)
	{
		var me = this;
			config = config || {};

		Ext.apply(me, config);
		me.value = {};
		me.deferredUpdate = Ext.create('Ext.util.DelayedTask', me.reload, me);
	},
	init: function(grid)
	{
		var me = this,
			store = grid.getStore();

		me.grid = grid;
		me.btn = null;
		grid.xsearch = me;

		if(grid.extraSearch && grid.extraSearch.length)
		{
			me.createUI();
			me.bindStore(store);
			me.gridListeners = {
				scope: me,
				beforestaterestore: me.applyState,
				beforestatesave: me.saveState
			};
			grid.on(me.gridListeners);
		}
	},
	createUI: function()
	{
		var me = this,
			grid = me.grid,
			topdock = grid.getDockedComponent('toolTop'),
			srch = [],
			menui = [],
			config, state;

		if(grid.extraSearch && grid.extraSearch.length)
		{
			Ext.Array.each(grid.extraSearch, function(sf)
			{
				var name = sf.name;

				Ext.apply(sf, {
					itemId: name,
					listeners: {
						scope: me,
						change: function(field, newval, oldval)
						{
							var grid;

							// save grid state
							if(!this.applyingState)
							{
								this.value[name] = newval;
								grid = this.grid;
								grid.saveState();
								grid.fireEvent('xsearchupdate', this, newval);
							}
							// restart the timer
							if(this.autoReload)
								this.deferredUpdate.delay(this.updateBuffer);
						}
					},
					value: me.value[name],
					cls: 'xsearch-item'
				});
				if(sf.store && !sf.store.isStore)
					sf.store = Ext.create(sf.store, {
						pageSize: -1
					});
				srch.push(sf);

				sf = {
					xtype: 'button',
					text: me.clearText,
					iconCls: 'ico-clear',
					cellCls: 'np-valign-top',
					listeners: {
						click: function(el, ev)
						{
							this.up('panel').getComponent(name).setValue(null);
						}
					}
				};
				srch.push(sf);
			}, me);

			menui.push({
				xtype: 'panel',
				iconCls: 'ico-find-plus',
				title: me.advSearchText,
				defaults: {
					margin: 5,
					labelAlign: 'right'
				},
				layout: {
					type: 'table',
					columns: 2
				},
				items: srch
			});
		}
		if(menui.length > 0)
		{
			config = {
				text: me.searchText,
				tooltip: { text: me.searchTipText, title: me.searchText },
				iconCls: 'ico-find',
				menu: {
					xtype: 'menu',
					plain: true,
					layout: 'fit',
					showSeparator: false,
					defaults: {
						plain: true
					},
					items: [{
						xtype: 'panel',
						layout: {
							type: 'accordion',
							align: 'stretch'
						},
						items: menui
					}]
				}
			};
			me.btn = Ext.create('Ext.button.Button', config);
			topdock.add(me.btn);
		}
	},
	getValue: function()
	{
		var me = this,
			ret = {},
			fl;

		if(!me.btn || !me.btn.menu)
			return {};
		fl = me.btn.menu.query('[cls~=xsearch-item]');
		Ext.Array.each(fl, function(fld)
		{
			var fv;

			fv = fld.getValue();
			if(Ext.isObject(fv))
				Ext.apply(ret, fv);
			else
				ret[fld.getName()] = fv;
		});
		return ret;
	},
	setValue: function(value)
	{
		var me = this,
			fl;

		if(!Ext.isObject(value))
			value = {};
		this.value = value;
		if(!me.btn || !me.btn.menu)
			return;
		fl = me.btn.menu.query('[cls~=xsearch-item]');
		Ext.Array.each(fl, function(fld)
		{
			var fname, fclass;

			fname = fld.getName();
			fclass = Ext.getClassName(fld);

			switch(fclass)
			{
				case 'Ext.form.field.ComboBox':
				case 'NetProfile.form.field.NullableComboBox':
					fld.suspendEvents();
					if(value.hasOwnProperty(fname))
						fld.select(value[fname]);
					else
						fld.clearValue();
					fld.resumeEvents();
					break;
				case 'NetProfile.form.DynamicCheckboxGroup':
					fld.suspendEvents();
					if(value.hasOwnProperty(fname))
						fld.setValue(value[fname]);
					else
						fld.setValue([]);
					fld.resumeEvents();
					break;
				default:
					if(value.hasOwnProperty(fname))
						fld.setRawValue(value[fname]);
					else
						fld.setRawValue('');
					break;
			}
		});
	},
	clearValue: function(suppressEvent)
	{
		var me = this,
			fl;

		if(!me.btn || !me.btn.menu)
			return;
		fl = me.btn.menu.query('[cls~=xsearch-item]');
		Ext.Array.each(fl, function(fld)
		{
			var fclass = Ext.getClassName(fld);

			switch(fclass)
			{
				case 'Ext.form.field.ComboBox':
				case 'NetProfile.form.field.NullableComboBox':
					fld.suspendEvents();
					fld.clearValue();
					fld.resumeEvents();
					break;
				case 'NetProfile.form.DynamicCheckboxGroup':
					fld.suspendEvents();
					fld.setValue([]);
					fld.resumeEvents();
					break;
				default:
					fld.setRawValue('');
					break;
			}
		});
	},
	applyState: function(grid, state)
	{
		var me = this;

		me.applyingState = true;
		if(state.xfilter)
			me.setValue(state.xfilter);
		else
			me.clearValue();
		me.deferredUpdate.cancel();

		delete me.applyingState;
		delete state.xfilter;
	},
	saveState: function(grid, state)
	{
		var me = this,
			values = me.getValue();

		if(values)
		{
			state.xfilter = values;
			return true;
		}
		return false;
	},
	destroy: function()
	{
		var me = this,
			grid = me.grid;

		me.bindStore(null);
		if(grid.xsearch)
			grid.xsearch = null;
		grid.un(me.gridListeners);
		Ext.destroyMembers(me, 'btn');
		me.value = {};
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
			xfilter = me.getValue();

		store.lastExtraParams = store.lastExtraParams || {};
		if(me.paramPrefix in params)
			delete params[me.paramPrefix];
		if(me.paramPrefix in store.lastExtraParams)
			delete store.lastExtraParams[me.paramPrefix];
		if(xfilter)
		{
			params[me.paramPrefix] = xfilter;
			store.lastExtraParams[me.paramPrefix] = xfilter;
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

