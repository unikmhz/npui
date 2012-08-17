Ext.define('Ext.ux.grid.SimpleSearchFeature', {
	extend: 'Ext.grid.feature.Feature',
	alias: 'feature.simplesearch',
	uses: ['Ext.form.field.Text'],
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
	 * @cfg {String} fieldEmptyText
	 * defaults to <tt>'Search...'</tt>.
	 */
	fieldEmptyText: 'Search...',
	/**
	 * @cfg {String} paramPrefix
	 * The url parameter prefix for the search string.
	 * Defaults to <tt>'__sstr'</tt>.
	 */
	paramPrefix: '__sstr',
	/**
	 * @cfg {Number} updateBuffer
	 * Number of milliseconds to defer store updates since the last search string change.
	 */
	updateBuffer: 500,
	// doesn't handle grid body events
	hasFeatureEvent: false,

	/** @private */
	constructor: function (config) {
		var me = this;

		config = config || {};
		Ext.apply(me, config);

		me.deferredUpdate = Ext.create('Ext.util.DelayedTask', me.reload, me);
	},

	attachEvents: function() {
		var me = this,
			view = me.view,
			grid = me.getGridPanel();

		me.bindStore(view.getStore(), true);

		grid.on({
			scope: me,
			beforestaterestore: me.applyState,
			beforestatesave: me.saveState,
			beforedestroy: me.destroy
		});

		// Add event and filters shortcut on grid panel
		grid.ssearch = me;
		grid.addEvents('ssearchupdate');

		me.createField();
		me.applyState(grid, grid.fstate || {});
	},

	/**
	 * @private Create a search field for the current configuration, destroying any existing ones first.
	 */
	createField: function() {
		var me = this,
			grid = me.getGridPanel(),
			topdock = grid.getDockedComponent('toolTop'),
			config,
			state;

		config = {
			iconCls: this.iconCls,
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
		};
		me.field = Ext.create('Ext.form.field.Text', config);
		topdock.add('->');
		topdock.add(me.field);
	},

	getValue: function () {
		return this.field.getValue();
	},

	setValue: function (value) {
		this.field.setValue(value);
	},

	clearValue: function(suppressEvent) {
		if(suppressEvent)
			this.field.suspendEvents();
		this.field.setValue('');
		if(suppressEvent)
			this.field.resumeEvents();
	},

	getGridPanel: function() {
		return this.view.up('gridpanel');
	},

	applyState: function (grid, state) {
		var me = this,
			key, filter;
		me.applyingState = true;
		me.field.setValue('');
		if (state.sstr)
			me.setValue(state.sstr);
		else
			me.setValue('');
		me.deferredUpdate.cancel();
		if (me.local)
			me.reload();
		delete me.applyingState;
		delete state.sstr;
	},

	/**
	 * Saves the state of search field
	 * @param {Object} grid
	 * @param {Object} state
	 * @return {Boolean}
	 */
	saveState: function (grid, state) {
		var sstr;
		if(this.field && !this.field.isDisabled())
		{
			sstr = this.field.getValue();
			return true;
		}
		return false;
	},

	/**
	 * @private
	 * Handler called by the grid 'beforedestroy' event
	 */
	destroy: function () {
		var me = this;
		Ext.destroyMembers(me, 'field');
		me.clearListeners();
	},

	/**
	 * Changes the data store bound to this view and refreshes it.
	 * @param {Ext.data.Store} store The store to bind to this view
	 */
	bindStore: function(store) {
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
	onBeforeLoad: function (store, options) {
		options.params = options.params || {};
		this.cleanParams(options.params);
		var params = this.buildQuery(this.getSearchData());
		Ext.apply(options.params, params);
	},

	/**
	 * @private
	 * Handler for store's load event when configured for local filtering
	 * @param {Object} store
	 */
	onLoad: function (store) {
		store.filterBy(this.getRecordFilter());
	},

	/** @private */
	reload: function () {
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
	getRecordFilter: function () {
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

	buildQuery: function (sdata) {
		var p = {};

		if(!sdata || !sdata.sstr)
			return p;
		p[this.paramPrefix] = sdata.sstr;
		return p;
	},

	/**
	 * Returns an Object containing current search query.
	 * @return {Object} sdata Current search query.
	 */
	getSearchData: function () {
		var sdata = {};

		if(this.field && !this.field.isDisabled())
			sdata['sstr'] = this.field.getValue();
		return sdata;
	},

	/**
	 * Removes filter related query parameters from the provided object.
	 * @param {Object} p Query parameters that may contain filter related fields.
	 */
	cleanParams: function (p) {
		delete p[this.paramPrefix];
	}
});

