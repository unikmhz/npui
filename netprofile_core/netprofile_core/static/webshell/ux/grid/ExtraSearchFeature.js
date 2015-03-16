Ext.define('Ext.ux.grid.ExtraSearchFeature', {
	extend: 'Ext.grid.feature.Feature',
	alias: 'feature.extrasearch',
	requires: [
		'Ext.menu.Menu',
		'Ext.container.ButtonGroup',
		'Ext.form.*'
	],
	/**
	 * @cfg {Boolean} autoReload
	 * Defaults to true, reloading the datasource when a field change happens.
	 * Set this to false to prevent the datastore from being reloaded if there
	 * are changes to the filters.  See <code>{@link #updateBuffer}</code>.
	 */
	autoReload: true,
	/**
	 * @cfg {Boolean} local
	 * <tt>true</tt> to use Ext.data.Store filter functions (local filtering)
	 * instead of the default (<tt>false</tt>) server side filtering.
	 */
	local: false,
	/**
	 * @cfg {String} paramPrefix
	 * The url parameter prefix for the search string.
	 * Defaults to <tt>'__xfilter'</tt>.
	 */
	paramPrefix: '__xfilter',
	/**
	 * @cfg {Number} updateBuffer
	 * Number of milliseconds to defer store updates since the last search string change.
	 */
	updateBuffer: 500,
	// doesn't handle grid body events
	hasFeatureEvent: false,

	fieldDefaults: {
	},

	searchText: 'Search',
	searchTipText: 'Additional search filters.',
	advSearchText: 'Advanced search',
	clearText: 'Clear',

	/** @private */
	constructor: function(config)
	{
		var me = this;

		config = config || {};
		Ext.apply(me, config);

		me.deferredUpdate = Ext.create('Ext.util.DelayedTask', me.reload, me);
	},

	attachEvents: function()
	{
		var me = this,
			view = me.view,
			grid = me.getGridPanel();

		if(grid.extraSearch && (grid.extraSearch.length > 0))
		{
			me.bindStore(view.getStore(), true);

			grid.on({
				scope: me,
				beforestaterestore: me.applyState,
				beforestatesave: me.saveState,
				beforedestroy: me.destroy
			});

			// Add event and filters shortcut on grid panel
			grid.xsearch = me;
			grid.addEvents('xsearchupdate');

			me.createUI();
			me.applyState(grid, grid.fstate || {});
		}
	},

	/**
	 * @private Create a search button and UI.
	 */
	createUI: function()
	{
		var me = this,
			grid = me.getGridPanel(),
			topdock = grid.getDockedComponent('toolTop'),
			config, menui, srch, state;

		srch = [];
		menui = [];

		if(grid.extraSearch)
		{
			Ext.Array.each(grid.extraSearch, function(sf)
			{
				var name = sf.name;

				Ext.apply(sf, {
					itemId: name,
					listeners: {
						change: function(field, newval, oldval)
						{
							// save grid state
							if(!this.applyingState)
							{
								var grid = this.getGridPanel();
								grid.saveState();
								grid.fireEvent('xsearchupdate', this, field.getValue());
							}
							// restart the timer
							if(this.autoReload)
								this.deferredUpdate.delay(this.updateBuffer);
						},
						scope: me
					},
					cls: 'xsearch-item'
				});
				if(sf.store && Ext.isString(sf.store))
					sf.store = Ext.create(sf.store, {
						buffered: false,
						pageSize: -1
					});
				srch.push(sf);

				sf = {
					xtype: 'button',
					text: me.clearText,
					iconCls: 'ico-clear',
					listeners: {
						click: function(el, ev)
						{
							this.up('buttongroup').getComponent(name).setValue(null);
						}
					}
				};
				srch.push(sf);
			}, me);
			menui.push({
				xtype: 'buttongroup',
				collapsible: true,
				titleCollapse: true,
				title: me.advSearchText,
				titleAlign: 'left',
				hideCollapseTool: true,
				animCollapse: false,
				columns: 2,
				defaults: {
					margin: 3,
					labelAlign: 'right'
				},
				items: srch
			});
		}
		config = {
			text: me.searchText,
			tooltip: { text: me.searchTipText, title: me.searchText },
			iconCls: 'ico-find'
		};
		if(menui.length > 0)
		{
			config.menu = {
				xtype: 'menu',
				items: menui
			};
			me.btn = Ext.create('Ext.button.Button', config);
			topdock.add(me.btn);
		}

/*			iconCls: this.iconCls,a
			emptyText: this.fieldEmptyText,
			hideLabel: true,
			listeners: {
				scope: this,
				change: function(field, newval, oldval) {
					// save grid state
					if(!this.applyingState)
					{
						var grid = this.getGridPanel();
						grid.saveState();
						grid.fireEvent('ssearchupdate', this, field.getValue());
					}
					// restart the timer
					if(this.autoReload)
						this.deferredUpdate.delay(this.updateBuffer);
				}
			}
		};*/
	},

	getValue: function()
	{
		var me = this,
			ret = {},
			fl, fv;

		if(!me.btn || !me.btn.menu)
			return {};
		fl = me.btn.menu.query('[cls~=xsearch-item]');
		Ext.Array.each(fl, function(fld)
		{
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
			fl, fname, fclass;

		if(!Ext.isObject(value))
			value = {};
		fl = me.btn.menu.query('[cls~=xsearch-item]');
		Ext.Array.each(fl, function(fld)
		{
			fname = fld.getName();
			fclass = Ext.getClassName(fld);

			switch(fclass)
			{
				case 'Ext.form.field.ComboBox':
					fld.suspendEvents();
					if(value.hasOwnProperty(fname))
						fld.select(value[fname]);
					else
						fld.clearValue();
					fld.resumeEvents();
					break;
				case 'Ext.ux.form.DynamicCheckboxGroup':
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
			fl, fname, fclass;

		if(!me.btn || !me.btn.menu)
			return;
		fl = me.btn.menu.query('[cls~=xsearch-item]');
		Ext.Array.each(fl, function(fld)
		{
			fclass = Ext.getClassName(fld);
			switch(fclass)
			{
				case 'Ext.form.field.ComboBox':
					fld.suspendEvents();
					fld.clearValue();
					fld.resumeEvents();
					break;
				case 'Ext.ux.form.DynamicCheckboxGroup':
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

	getGridPanel: function()
	{
		return this.view.up('gridpanel');
	},

	applyState: function(grid, state)
	{
		var me = this,
			up = false;
		me.applyingState = true;
		if(state && state.hasOwnProperty('xfilter'))
		{
			me.setValue(state.xfilter);
			up = true;
		}
		me.deferredUpdate.cancel();
		if(me.local && up)
			me.reload();
		delete me.applyingState;
		if(up)
			delete state.xfilter;
	},

	/**
	 * Saves the state of search field
	 * @param {Object} grid
	 * @param {Object} state
	 * @return {Boolean}
	 */
	saveState: function(grid, state)
	{
		var xs;

		xs = this.getValue();
		if(xs)
		{
			state.xfilter = xs;
			return true;
		}
		return false;
	},

	/**
	 * @private
	 * Handler called by the grid 'beforedestroy' event
	 */
	destroy: function()
	{
		var me = this;
		if(me.btn)
		{
			Ext.destroy(me.btn);
			delete me.btn;
		}
		me.clearListeners();
	},

	/**
	 * Changes the data store bound to this view and refreshes it.
	 * @param {Ext.data.Store} store The store to bind to this view
	 */
	bindStore: function(store)
	{
		var me = this;

		// Unbind from the old Store
		if (me.store && me.storeListeners) {
			me.store.un(me.storeListeners);
		}

		// Set up correct listeners
		if (store) {
			me.storeListeners = {
				scope: me
			};
			if (me.local) {
				me.storeListeners.load = me.onLoad;
			} else {
				me.storeListeners['before' + (store.buffered ? 'prefetch' : 'load')] = me.onBeforeLoad;
			}
			store.on(me.storeListeners);
		} else {
			delete me.storeListeners;
		}
		me.store = store;
	},

	/**
	 * @private
	 * Handler for store's beforeload event when configured for remote filtering
	 * @param {Object} store
	 * @param {Object} options
	 */
	onBeforeLoad: function(store, options)
	{
		options.params = options.params || {};
		this.cleanParams(options.params);
		var params = this.buildQuery(this.getSearchData());
		Ext.apply(options.params, params);
		store.lastExtraParams = store.lastExtraParams || {};
		Ext.apply(store.lastExtraParams, params);
	},

	/**
	 * @private
	 * Handler for store's load event when configured for local filtering
	 * @param {Object} store
	 */
	onLoad: function(store)
	{
		store.filterBy(this.getRecordFilter());
	},

	/** @private */
	reload: function()
	{
		var me = this,
			store = me.view.getStore();

		if (me.local) {
			store.clearFilter(true);
			store.filterBy(me.getRecordFilter());
			store.sort();
		} else {
			me.deferredUpdate.cancel();
			if (store.buffered) {
				store.pageMap.clear();
			}
			store.loadPage(1);
		}
	},

	/**
	 * Method factory that generates a record validator for the search string
	 * of invokation.
	 * @private
	 */
	getRecordFilter: function()
	{
		//var f = [], len, i;
		//this.filters.each(function (filter) {
		//	if (filter.active) {
		//		f.push(filter);
		//	}
		//});

		//len = f.length;
		//return function (record) {
		//	for (i = 0; i < len; i++) {
		//		if (!f[i].validateRecord(record)) {
		//			return false;
		//		}
		//	}
		//	return true;
		//};
	},

	buildQuery: function(sdata)
	{
		var r = {};

		if(sdata)
			r[this.paramPrefix] = sdata;
		return r;
	},

	/**
	 * Returns an Object containing current search query.
	 * @return {Object} sdata Current search query.
	 */
	getSearchData: function () {
		var p, i, sdata = {};

		p = this.getValue();
		for(i in p)
		{
			if((p[i] !== undefined) && (p[i] !== null))
				sdata[i] = p[i];
		}
		return sdata;
	},

	/**
	 * Removes filter related query parameters from the provided object.
	 * @param {Object} p Query parameters that may contain filter related fields.
	 */
	cleanParams: function(p)
	{
		delete p[this.paramPrefix];
	}
});

