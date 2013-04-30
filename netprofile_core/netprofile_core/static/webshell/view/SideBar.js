Ext.define('NetProfile.view.SideBar', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.sidebar',
	requires: [
		'NetProfile.store.Menu',
		'Ext.tree.Panel',
		'Ext.tree.plugin.TreeViewDragDrop',
		'Ext.util.History',
		'Ext.state.Manager',
		'Ext.ux.grid.plugin.ManualEditing',
		'Ext.layout.container.Accordion',
		'NetProfile.view.TopBar'
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
		xtype: 'topbar',
		dock: 'top'
	}],

	lastPanel: null,

	initComponent: function()
	{
		var token;

		Ext.History.init();
		this.applyState(Ext.state.Manager.getProvider().get(this.stateId));
		token = Ext.History.getToken();
		if(token)
		{
			token = token.split(':');
			if(token && (token.length === 2))
				token = token[0];
			else
				token = this.lastPanel;
		}
		else
			token = this.lastPanel;

		this.menus = {};
		this.items = [];
		this.store = Ext.create('NetProfile.store.Menu');
		this.store.each(function(menu)
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
					beforeselect: this.onMenuBeforeSelect,
					select: this.onMenuSelect,
					scope: this,
					options: { menuId: mname }
				},
				useArrows: true,
				header: false,
				border: false,
				bodyCls: 'x-docked-noborder-top'
			}, menu.get('options') || {});
			tree = Ext.create('Ext.tree.Panel', cfg);

			this.menus[mname] = tree;

			this.items.push({
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
						this.lastPanel = p.id.split('_')[1];
						this.saveState();
					},
					scope: this
				}
			});
		}, this);
		this.callParent(arguments);

		this.on({
			afterrender: this.onAfterRender,
			scope: this
		});
	},
    getState: function()
	{
		var state = this.callParent();

		state = this.addPropertyToState(state, 'lastPanel');
		return state;
	},
	onMenuBeforeSelect: function(row, record, idx, opts)
	{
		if(record.get('iconCls') == 'ico-module')
			return false;
		return true;
	},
	onMenuSelect: function(row, record, idx, opts)
	{
		var tok_old, tok_new, toks, prec, menu;

		menu = this.store.findRecord('name', opts.options.menuId);
		Ext.Object.each(this.menus, function(k, m)
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
		var me = this,
			pts, store, node, sub, item, menu;

		if(token)
		{
			pts = token.split(':');
			if(pts.length != 2)
				return true;
			store = Ext.getStore('npstore_menu_' + pts[0]);
			if(!store)
				return true;
			node = store.getNodeById(pts[1]);
			menu = this.getComponent('npmenu_' + pts[0]);
			if(menu)
				menu.expand();
			if(!node)
			{
				sub = pts[1].split('/');
				if(sub.length == 0)
					return true;
				item = sub.shift();
				node = store.getNodeById(item);
				if(!node)
					return true;
				if(sub.length > 0)
				{
					var rec_exp;

					rec_exp = function(ch)
					{
						var find_id, find_node = null;

						find_id = sub.shift();
						Ext.Array.forEach(ch, function(item)
						{
							if(item.getId() == find_id)
								find_node = item;
						});
						if(!find_node)
							return;
						if(sub.length > 0)
						{
							if(find_node.isExpanded())
								rec_exp(find_node.childNodes);
							else
								find_node.expand(false, rec_exp);
						}
						else
							me.doSelectNode(find_node, pts[0]);
					};

					if(node.isLoading())
					{
						store.on('load', function(st, xnode, recs)
						{
							if(node.isExpanded())
								rec_exp(recs);
							else
								node.expand(false, rec_exp);
							return true;
						}, me, { single: true });
						node.expand();
					}
					else if(node.isExpanded())
						rec_exp(node.childNodes);
					else
						node.expand(false, rec_exp);
				}
				else
					this.doSelectNode(node, pts[0]);
				return true;
			}
			this.doSelectNode(node, pts[0]);
		}
		else if(this.lastPanel)
		{
			menu = this.getComponent('npmenu_' + this.lastPanel);
			if(menu)
				menu.expand();
		}
		return true;
	},
	doSelectNode: function(node, menu)
	{
		if(node.get('xview'))
			this.doSelectMenuView(node.get('xview'));
		if(node.get('xhandler'))
			this.doSelectMenuHandler(node.get('xhandler'), node.getId());
		if(menu)
			this.menus[menu].selectPath(node.getPath());
	}
});

