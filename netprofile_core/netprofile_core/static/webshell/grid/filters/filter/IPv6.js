Ext.define('NetProfile.grid.filters.filter.IPv6', {
	extend: 'NetProfile.grid.filters.filter.Number',
	alias: 'grid.filter.ipv6',
	uses: ['NetProfile.form.field.IPv6'],
	type: 'ipv6',

	emptyText: 'Enter IPv6 Address...',
	itemDefaults: {
		xtype: 'ipv6field',
		enableKeyEvents: true,
		hideEmptyLabel: false,
		labelSeparator: '',
		labelWidth: 29,
		selectOnFocus: false
	}
});

