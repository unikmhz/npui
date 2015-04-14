Ext.define('NetProfile.grid.filters.filter.List', {
	extend: 'Ext.grid.filters.filter.List',
	alias: 'grid.filter.nplist',

	type: 'nplist',

	constructor: function(config)
	{
		var me = this;

		if('optStore' in config)
		{
			config['store'] = Ext.create(config['optStore'], {
				pageSize: -1
			});
		}
		me.callParent([config]);
	},
	createMenuItems: function(store)
	{
		var me = this,
			menu = me.menu,
			len = store.getCount(),
			contains = Ext.Array.contains,
			initValues = [],
			listeners, itemDefaults, record, gid, idValue, idField, labelValue, labelField, i, item, processed;

		if(me.filter)
			initValues = me.filter.getValue();
		// B/c we're listening to datachanged event, we need to make sure there's a menu.
		if(len && menu)
		{
			listeners = {
				checkchange: me.onCheckChange,
				scope: me
			};

			itemDefaults = me.getItemDefaults();
			menu.suspendLayouts();
			menu.removeAll(true);
			gid = me.single ? Ext.id() : null;
			idField = me.idField;
			labelField = me.labelField;

			processed = [];

			for(i = 0; i < len; i++)
			{
				record = store.getAt(i);
				idValue = record.get(idField);
				labelValue = record.get(labelField);

				// Only allow unique values.
				if(labelValue == null || contains(processed, idValue))
					continue;

				processed.push(labelValue);

				// Note that the menu items will be set checked in filter#activate() if the value of the menu
				// item is in the cfg.value array.
				item = menu.add(Ext.apply({
					text: labelValue,
					group: gid,
					value: idValue,
					listeners: listeners
				}, itemDefaults));
				item.checked = (initValues.indexOf(idValue) !== -1);
			}

			menu.resumeLayouts(true);
		}
	},
	setStoreFilter: function(options)
	{
		var me = this,
			value = me.value,
			filter = me.filter,
			contains, i, len, val, list;

		// If there are user-provided values we trust that they are valid (an empty array IS valid!).
		if(value)
		{
			if(!Ext.isArray(value))
				value = [value];
			filter.setValue(value);
		}

		if(me.active && me.loaded)
		{
			me.preventFilterRemoval = true;
			me.addStoreFilter(filter);
			me.preventFilterRemoval = false;
		}
	}
});

