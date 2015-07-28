Ext.define('NetProfile.panel.SideBar', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.sidebar',
	requires: [
		'NetProfile.store.Menu',
		'Ext.tree.Panel',
		'Ext.tree.plugin.TreeViewDragDrop',
		'Ext.util.History',
		'Ext.state.Manager',
		'Ext.layout.container.Accordion',
		'NetProfile.toolbar.MainToolbar'
	],
	id: 'npws_sidebar',
	stateId: 'npws_sidebar',
	stateful: true,
	collapsible: true,
	animCollapse: true,
	layout: {
		type: 'accordion',
		multi: false
	},
	title: 'NetProfile',
	split: true,
	width: '15%',
	minWidth: 200,
	minHeight: 300,
	items: [],
	dockedItems: [{
		xtype: 'maintoolbar',
		dock: 'top'
	}],

	lastPanel: null,

	initComponent: function()
	{
		var me = this,
			token;

		Ext.History.init();
		me.applyState(Ext.state.Manager.getProvider().get(me.stateId));
		token = Ext.History.getToken();
		if(token)
		{
			token = token.split(':');
			if(token && (token.length === 2))
				token = token[0];
			else
				token = me.lastPanel;
		}
		else
			token = me.lastPanel;

		me.menus = {};
		me.items = [];
		me.store = Ext.create('NetProfile.store.Menu');
		me.store.each(function(menu)
		{
			var mname, tree, cfg;

			mname = menu.get('name');
			if(!token)
				token = mname;
			cfg = Ext.apply({
				id: 'npmenu_tree_' + mname,
				store: Ext.create('NetProfile.store.menu.' + mname),
				rootVisible: false,
				selModel: {
					ignoreRightMouseSelection: true
				},
				listeners: {
					afterlayout: me.onMenuAfterLayout,
					beforeselect: me.onMenuBeforeSelect,
					select: me.onMenuSelect,
					scope: me,
					options: { menuId: mname }
				},
				useArrows: true,
				header: false,
				border: false,
				bodyBorder: false
			}, menu.get('options') || {});
			tree = Ext.create('Ext.tree.Panel', cfg);

			if(NetProfile.model.customMenu && (mname in NetProfile.model.customMenu))
				NetProfile.model.customMenu[mname].setProxy(cfg.store.getProxy());

			me.menus[mname] = tree;

			me.items.push({
				id: 'npmenu_' + mname,
				layout: 'fit',
				collapsible: true,
				collapsed: ((token === mname) ? false : true),
				collapseFirst: false,
				title: menu.get('title'),
				items: [ tree ],
				tools: [{
					type: 'expand',
					handler: function() { this.expandAll(); },
					scope: tree
				}, {
					type: 'collapse',
					handler: function() { this.collapseAll(); },
					scope: tree
				}],
				listeners: {
					expand: function(p)
					{
						me.lastPanel = p.id.split('_')[1];
						me.saveState();
					}
				}
			});
		});
		me.callParent(arguments);

		me.on({
			afterrender: me.onAfterRender,
			scope: me
		});
	},
    getState: function()
	{
		var me = this,
			state = me.callParent();

		state = me.addPropertyToState(state, 'lastPanel');
		return state;
	},
	onMenuAfterLayout: function(tree, layout)
	{
		var sel = tree.getSelectionModel().getSelection(),
			view = tree.getView(),
			el;

		if(sel && (sel.length === 1))
		{
			sel = sel[0];
			el = view.getNode(sel);
			if(el)
				el.scrollIntoView();
		}
	},
	onMenuBeforeSelect: function(row, record, idx, opts)
	{
		if(record.get('iconCls') == 'ico-module')
			return false;
		return true;
	},
	onMenuSelect: function(row, record, idx, opts)
	{
		var me = this,
			tok_old, tok_new, toks, prec, menu;

		menu = me.store.findRecord('name', opts.options.menuId);
		Ext.Object.each(me.menus, function(k, m)
		{
			if(opts.options.menuId === k)
				return;
			var sm = m.getSelectionModel();
			if(sm)
				sm.deselectAll();
		});
		if(record.get('xhandler') || record.get('xview'))
		{
			if(menu.get('direct'))
			{
				toks = [record.getId()];
				prec = record;
				while(prec = prec.parentNode)
				{
					toks.unshift(prec.getId());
				}
				tok_new = opts.options.menuId + ':' + toks.join('/');
				tok_old = Ext.History.getToken();
				if(tok_old === null || (tok_old !== tok_new))
					Ext.History.add(tok_new);
			}
			else
			{
				tok_new = opts.options.menuId + ':' + record.getId();
				tok_old = Ext.History.getToken();
				if(tok_old === null || (tok_old !== tok_new))
					Ext.History.add(tok_new);
			}
		}

		return true;
	},
	onAfterRender: function()
	{
		var me = this;

		Ext.History.on({
			change: me.onHistoryChange,
			scope: me
		});
		me.onHistoryChange(Ext.History.getToken());
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
			}
		);
		return true;
	},
	onHistoryChange: function(token)
	{
		var me = this,
			pts, store, node, sub, menu, callback;

		if(token)
		{
			pts = token.split(':');
			if(pts.length !== 2)
				return true;
			store = Ext.getStore('npstore_menu_' + pts[0]);
			if(!store)
				return true;
			node = store.getNodeById(pts[1]);
			menu = me.getComponent('npmenu_' + pts[0]);
			if(menu)
				menu.expand();
			if(!node)
			{
				// TODO: need a more strict way of differentiating between IDs
				//       and paths in history tokens.
				sub = pts[1].split('/');
				if(sub.length == 0)
					return true;
				callback = function(node, store)
				{
					me.doSelectNode(node, pts[0]);
				};
				store.findNodeByPath(sub, callback);
			}
			else
				me.doSelectNode(node, pts[0]);
		}
		else if(me.lastPanel)
		{
			menu = me.getComponent('npmenu_' + me.lastPanel);
			if(menu)
				menu.expand();
		}
		return true;
	},
	doSelectNode: function(node, menuname)
	{
		var me = this;

		if(node.get('xview'))
			me.doSelectMenuView(node.get('xview'));
		if(node.get('xhandler'))
			me.doSelectMenuHandler(node.get('xhandler'), node.getId());
		if(menuname && (menuname in me.menus))
			me.menus[menuname].getSelectionModel().select([node], false, true);
	}
});

