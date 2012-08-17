Ext.define('NetProfile.view.SideBar', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.sidebar',
	requires: [
		'NetProfile.store.Menu',
		'Ext.tree.Panel',
		'NetProfile.view.TopBar'
	],
	id: 'npws_sidebar',
	stateId: 'npws_sidebar',
	stateful: true,
	collapsible: true,
	animCollapse: true,
	layout: 'accordion',
	title: 'NetProfile',
	split: true,
	width: '15%',
	minWidth: 200,
	minHeight: 300,
	items: [],
	dockedItems: [{
		xtype: 'topbar',
		dock: 'top'
	}],

	initComponent: function() {
		this.lastLoaded = null;
		this.items = [];
		this.store = Ext.create('NetProfile.store.Menu');
		this.store.each(function(menu) {
			mname = menu.get('name');
			var tree = Ext.create('Ext.tree.Panel', {
				id: 'npmenu_tree_' + mname,
				stateId: 'npmenu_tree_' + mname,
				stateful: true,
				store: Ext.create('NetProfile.store.menu.' + mname),
				rootVisible: false,
				listeners: {
					select: this.onMenuSelect,
					scope: this
				},
				useArrows: true,
				border: false
			});

			this.items.push({
				id: 'npmenu_' + mname,
				stateId: 'npmenu_' + mname,
				stateful: true,
				layout: 'fit',
				title: menu.get('title'),
				items: [ tree ]
			});
		}, this);
		this.callParent(arguments);
	},
	onMenuSelect: function(row, record, idx, opts)
	{
		var xview = record.get('xview'),
			mainbar = Ext.getCmp('npws_mainbar');

		if(xview)
		{
			if(this.lastLoaded)
				Ext.destroy(mainbar.remove(this.lastLoaded));
			this.lastLoaded = mainbar.add({
				region: 'center',
				xtype: xview,
				stateId: 'np' + xview,
				stateful: true
			});
		}

		return true;
	}
});

