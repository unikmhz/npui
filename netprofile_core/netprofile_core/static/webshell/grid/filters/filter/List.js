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
				autoLoad: false,
				autoDestory: true,
				buffered: false,
				pageSize: -1
			});
		}
		me.callParent([config]);
	}
});

