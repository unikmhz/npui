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

	initComponent: function()
	{
		this.menus = {};
		this.items = [];
		this.store = Ext.create('NetProfile.store.Menu');
		this.store.each(function(menu)
		{
			mname = menu.get('name');
			var tree = Ext.create('Ext.tree.Panel', {
				id: 'npmenu_tree_' + mname,
				stateId: 'npmenu_tree_' + mname,
				stateful: true,
				store: Ext.create('NetProfile.store.menu.' + mname),
				rootVisible: false,
				listeners: {
					beforeselect: this.onMenuBeforeSelect,
					select: this.onMenuSelect,
					scope: this,
					options: { menuId: mname }
				},
				useArrows: true,
				header: false,
				border: false,
				bodyCls: 'x-docked-noborder-top'
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
	onMenuBeforeSelect: function(row, record, idx, opts)
	{
		if(record.get('iconCls') == 'ico-module')
			return false;
		return true;
	},
	onMenuSelect: function(row, record, idx, opts)
	{
		var tok_old, tok_new;

		Ext.Object.each(this.menus, function(k, m)
		{
			if(opts.options.menuId === k)
				return;
			var sm = m.getSelectionModel();
			if(sm)
				sm.deselectAll();
		});
		if(record.get('xhandler'))
		{
			// FIXME
			this.doSelectMenuHandler(record.get('xhandler'), record.getId());
		}
		else if(record.get('xview'))
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
	doSelectMenuView: function(xview)
	{
		var mainbar = Ext.getCmp('npws_mainbar');

		if(!xview)
			return false;
		mainbar.replaceWith({
			region: 'center',
			xtype: xview,
			stateId: 'np' + xview,
			stateful: true,
			id: 'main_content'
		});
		return true;
	},
	doSelectMenuHandler: function(xhandler, xid)
	{
		if(!xhandler)
			return false;
		Ext.require(
			xhandler,
			function()
			{
				var mainbar, obj;

				obj = Ext.create(xhandler);
				if(obj.process)
					obj.process(xid);
				if(obj.getView)
				{
					mainbar = Ext.getCmp('npws_mainbar');
					mainbar.replaceWith(obj.getView(xid));
				}
				Ext.destroy(obj);
			},
			this
		);
		return true;
	},
	onHistoryChange: function(token)
	{
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
			this.doSelectMenuView(node.get('xview'));
			this.menus[pts[0]].getSelectionModel().select(node);
		}
		return true;
	}
});

