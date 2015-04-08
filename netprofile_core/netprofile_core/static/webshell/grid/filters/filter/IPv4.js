/**
 * Filter type for {@link Ext.grid.column.Number number columns}.
 *
 * Based on Ext.grid.filters.filter.Number.
 */
Ext.define('NetProfile.grid.filters.filter.IPv4', {
	extend: 'NetProfile.grid.filters.filter.TriFilter',
	alias: 'grid.filter.ipv4',
	uses: ['NetProfile.form.field.IPv4'],
	type: 'ipv4',

	config: {
		fields: {
			ge: {
				iconCls: Ext.baseCSSPrefix + 'grid-filters-gt',
				margin: '0 0 3px 0'
			},
			le: {
				iconCls: Ext.baseCSSPrefix + 'grid-filters-lt',
				margin: '0 0 3px 0'
			},
			eq: {
				iconCls: Ext.baseCSSPrefix + 'grid-filters-eq',
				margin: 0
			}
		}
	},

	itemDefaults: {
		xtype: 'ipv4field',
		allowBlank: true,
		hideEmptyLabel: false,
		labelSeparator: '',
		labelWidth: 29
	},
	menuDefaults: {
		// A menu with only form fields needs some body padding. Normally this padding
		// is managed by the items, but we have no normal menu items.
		bodyPadding: 3,
		showSeparator: false
	},

	createMenu: function()
	{
		var me = this,
			listeners = {
				scope: me,
				change: me.onIPValueChange
			},
			itemDefaults = me.getItemDefaults(),
			menuItems = me.menuItems,
			fields = me.getFields(),
			field, i, len, key, item, cfg;

		me.callParent();

		me.fields = {};

		for(i = 0, len = menuItems.length; i < len; i++)
		{
			key = menuItems[i];
			if(key !== '-')
			{
				field = fields[key];

				cfg = {
					value: (me.filter && me.filter[key] ? me.filter[key].getValue() : null),
					labelClsExtra: Ext.baseCSSPrefix + 'grid-filters-icon ' + field.iconCls
				};

				if(itemDefaults)
					Ext.merge(cfg, itemDefaults);

				Ext.merge(cfg, field);
				delete cfg.iconCls;

				me.fields[key] = item = me.menu.add(cfg);

				item.filter = me.filter[key];
				item.filterKey = key;
				item.on(listeners);
			}
			else
				me.menu.add(key);
		}
	},
	getValue: function(field)
	{
		var value = {};
		value[field.filterKey] = field.getValue();
		return value;
	},
	onIPValueChange: function(field, newval)
	{
		var me = this,
			updateBuffer = me.updateBuffer;

		if(updateBuffer)
			me.task.delay(updateBuffer, null, null, [me.getValue(field)]);
		else
			me.setValue(me.getValue(field));
	}
});

