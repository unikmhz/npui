Ext.define('NetProfile.view.SideBar', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.sidebar',
	requires: [
		'NetProfile.store.Menu',
		'Ext.tree.Panel',
		'Ext.util.History',
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
		this.menus = {};
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
					scope: this,
					options: { menuId: mname }
				},
				useArrows: true,
				border: false
			});

			this.menus[mname] = tree;

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

		Ext.History.init();

		this.on({
			afterrender: this.onAfterRender,
			scope: this
		});
	},
	onMenuSelect: function(row, record, idx, opts)
	{
		var tok_old, tok_new;

		if(record.get('xview'))
		{
			tok_new = opts.options.menuId + ':' + record.getId();
			tok_old = Ext.History.getToken();
			if(tok_old === null || (tok_old !== tok_new))
				Ext.History.add(tok_new);
		}

		return true;
	},
	onAfterRender: function()
	{
		this.onHistoryChange(Ext.History.getToken());
		Ext.History.on({
			change: this.onHistoryChange,
			scope: this
		});
	},
	doSelectMenuItem: function(xview)
	{
		var mainbar = Ext.getCmp('npws_mainbar');

		if(!xview)
			return false;
		if(this.lastLoaded)
		{
			Ext.destroy(mainbar.remove(this.lastLoaded));
			this.lastLoaded = null;
		}
		this.lastLoaded = mainbar.add({
			region: 'center',
			xtype: xview,
			stateId: 'np' + xview,
			stateful: true,
			id: 'main_content'
		});
		return true;
	},
	onHistoryChange: function(token) {
		var pts, store, node;

		if(token)
		{
			pts = token.split(':');
			if(pts.length != 2)
				return true;
			store = Ext.getStore('npstore_menu_' + pts[0]);
			if(!store)
				return true;
			node = store.getNodeById(pts[1]);
			if(!node)
				return true;
			this.doSelectMenuItem(node.get('xview'));
			this.menus[pts[0]].getSelectionModel().select(node);
		}
		return true;
	}
});

