Ext.define('NetProfile.view.PropBar', {
	extend: 'Ext.tab.Panel',
	alias: 'widget.propbar',
	requires: [
		'Ext.tab.Panel',
		'Ext.util.KeyMap'
	],
	id: 'npws_propbar',
	stateId: 'npws_propbar',
	stateful: true,
	collapsible: false,
//	title: 'Properties',
//	header: {
//		iconCls: 'ico-props'
//	},
//	headerPosition: 'right',
	hidden: true,
	layout: 'fit',
	split: false,
	height: '40%',
	minHeight: 300,
	border: 0,
	tabBar: {
		cls: 'np-propbar-tabbar'
	},
	tabCache: {},
	items: [
	],
	tools: [],

	recordText: 'Record',

	initComponent: function()
	{
		this.tabCache = {};
//		this.tools = [{
//			itemId: 'minimize',
//			type: 'minimize',
//			handler: function()
//			{
//				this.hide();
//			},
//			scope: this
//		}, {
//			itemId: 'close',
//			type: 'close',
//			handler: function()
//			{
//				this.clearAll();
//			},
//			scope: this
//		}];
		this.callParent(arguments);

		this.on({
			beforeremove: function(cont, cmp, opts)
			{
				if(cmp.ownerCt != this)
					return true;
				if(this.items.length <= 1)
					this.hide();
				return true;
			},
			scope: this
		});

		this.kmap = new Ext.util.KeyMap({
			target: Ext.getBody(),
			binding: [{
				key: 'w',
				fn: function(kc, ev)
				{
					var at = this.getActiveTab();

					if(at && ev.altKey)
					{
						ev.stopEvent();
						if(ev.shiftKey)
							this.clearAll();
						else
							this.clear(at);
					}
				},
				scope: this
			}]
		});
	},
	clearState: function()
	{
		this.tabCache = {};
		Ext.destroy(this.removeAll());
	},
	clearAll: function()
	{
		this.hide();
		this.clearState();
	},
	clear: function(at)
	{
		Ext.Object.each(this.tabCache, function(tci, tc)
		{
			if(at === tc)
			{
				delete this.tabCache[tci];
				this.remove(tc, true);
			}
		}, this);
	},
	addTab: function(tab_id, tab_cfg)
	{
		var tab;

		if(this.tabCache.hasOwnProperty(tab_id))
			tab = this.tabCache[tab_id];
		else
		{
			Ext.apply(tab_cfg, {
				record: record,
				closable: true,
				cls: 'record-tab',
				tabConfig: {
					cls: 'record-tab-hdl'
				},
				listeners: {
					removed: function(comp, ct, opts)
					{
						if(ct.tabCache.hasOwnProperty(tab_id))
							delete ct.tabCache[tab_id];
						return true;
					},
					scope: this
				}
			});
			this.tabCache[tab_id] = tab = this.add(cfg);
		}
		this.setActiveTab(tab);
		return tab;
	},
	addRecordTab: function(module, model, cfg, record)
	{
		var tab, rec_name;

		if(this.tabCache.hasOwnProperty(record.id))
			tab = this.tabCache[record.id];
		else
		{
			rec_name = record.get('__str__');
			if(!rec_name)
				rec_name = this.recordText + ' ' + record.getId();
			Ext.apply(cfg, {
				title: rec_name,
				record: record,
				closable: true,
				cls: 'record-tab',
				iconCls: 'ico-mod-' + model.toLowerCase(),
				tabConfig: {
					cls: 'record-tab-hdl'
				},
				listeners: {
					removed: function(comp, ct, opts)
					{
						if(!comp.record)
							return true;
						if(ct.tabCache.hasOwnProperty(record.id))
							delete ct.tabCache[record.id];
						return true;
					},
					scope: this
				}
			});
			this.tabCache[record.id] = tab = this.add(cfg);
			tab.apiModule = module;
			tab.apiClass = model;
		}
		this.setActiveTab(tab);
		return tab;
	}
});

