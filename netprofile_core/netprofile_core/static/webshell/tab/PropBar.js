Ext.define('NetProfile.tab.PropBar', {
	extend: 'Ext.tab.Panel',
	alias: 'widget.propbar',
	requires: [
		'Ext.tab.Panel',
		'Ext.util.KeyMap',
		'Ext.form.field.Text',
		'Ext.button.Button'
	],
	id: 'npws_propbar',
	stateId: 'npws_propbar',
	stateful: true,
	collapsible: false,
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
	submitText: 'Submit',

	initComponent: function()
	{
		this.tabCache = {};
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
						if(ev.ctrlKey)
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
		this.removeAll(true);
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
			tab_cfg = tab_cfg || {};
			Ext.apply(tab_cfg, {
				closable: true,
				tabConfig: {
					cls: 'record-tab-hdl'
				},
				listeners: Ext.apply(tab_cfg.listeners || {}, {
					removed: function(comp, ct, opts)
					{
						if(ct.tabCache.hasOwnProperty(tab_id))
							delete ct.tabCache[tab_id];
						return true;
					},
					scope: this
				})
			});
			this.tabCache[tab_id] = tab = this.add(tab_cfg);
		}
		this.setActiveTab(tab);
		return tab;
	},
	addConsoleTab: function(tab_id, tab_cfg, submit_fn)
	{
		Ext.apply(tab_cfg, {
			border: 0,
			bbar: [{
				xtype: 'textfield',
				itemId: 'prompt',
				shrinkWrap: 1,
				flex: 1,
				enableKeyEvents: true,
				listeners: {
					keydown: function(fld, ev)
					{
						if(ev.getKey() === ev.ENTER)
						{
							var me = this,
								val = me.getValue();

							ev.stopEvent();
							me.setValue('');
							if(submit_fn)
								submit_fn(val);
						}
					}
				}
			}, {
				xtype: 'button',
				itemId: 'submit',
				iconCls: 'ico-accept',
				text: this.submitText,
				handler: function()
				{
					var me = this,
						tbar = me.up('toolbar'),
						fld = tbar.getComponent('prompt'),
						val = fld.getValue();

					fld.setValue('');
					if(submit_fn)
						submit_fn(val);
				}
			}]
		});
		return this.addTab(tab_id, tab_cfg);
	},
	addRecordTab: function(module, model, cfg, record)
	{
		var rec_id = record.entityName + '.' + record.getId(),
			tab, rec_name;

		if(this.tabCache.hasOwnProperty(rec_id))
			tab = this.tabCache[rec_id];
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
						if(ct.tabCache.hasOwnProperty(rec_id))
							delete ct.tabCache[rec_id];
						return true;
					},
					scope: this
				}
			});
			this.tabCache[rec_id] = tab = this.add(cfg);
			tab.apiModule = module;
			tab.apiClass = model;
		}
		this.setActiveTab(tab);
		return tab;
	}
});

