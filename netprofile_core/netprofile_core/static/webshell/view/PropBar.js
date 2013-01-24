Ext.define('NetProfile.view.PropBar', {
	extend: 'Ext.tab.Panel',
	alias: 'widget.propbar',
	requires: [
		'Ext.tab.Panel'
	],
	id: 'npws_propbar',
	stateId: 'npws_propbar',
	stateful: true,
	collapsible: false,
	header: false,
	hidden: true,
	layout: 'fit',
	split: false,
	height: '40%',
	minHeight: 300,
	border: 0,
	apiModule: null,
	apiClass: null,
	tabCache: {},
	items: [
	],
	tools: [],

	recordText: 'Record',

	initComponent: function() {
		this.tabCache = {};
		this.tools = [{
			itemId: 'close',
			type: 'close',
			handler: function() {
				this.hide();
			},
			scope: this
		}];
		this.callParent(arguments);

		this.on({
			beforeremove: function(cont, cmp, opts) {
				if(cmp.ownerCt != this)
					return true;
				if(this.items.length <= 1)
					this.hide();
				return true;
			},
			scope: this
		});
	},
	clearState: function()
	{
		this.tabCache = {};
		Ext.destroy(this.removeAll());
	},
	getApiModule: function()
	{
		return this.apiModule;
	},
	setApiModule: function(am)
	{
		if(this.apiModule != am)
			this.clearState();
		this.apiModule = am;
	},
	getApiClass: function()
	{
		return this.apiClass;
	},
	setApiClass: function(ac)
	{
		if(this.apiClass != ac)
			this.clearState();
		this.apiClass = ac;
	},
	setContext: function(am, ac)
	{
		if((this.apiModule != am) || (this.apiClass != ac))
			this.clearState();
		this.apiModule = am;
		this.apiClass = ac;
	},
	clearContext: function()
	{
		if((this.apiModule !== null) || (this.apiClass !== null))
			this.clearState();
		this.apiModule = null;
		this.apiClass = null;
	},
	clearAll: function()
	{
		this.hide();
		this.clearState();
		this.clearContext();
	},
	addRecordTab: function(cfg, record)
	{
		var tab, rec_name, rec_id;

		rec_id = record.getId();
		if(this.tabCache.hasOwnProperty(rec_id))
		{
			tab = this.tabCache[rec_id];
		}
		else
		{
			rec_name = record.get('__str__');
			if(!rec_name)
				rec_name = this.recordText + ' ' + rec_id;
			Ext.apply(cfg, {
				title: rec_name,
				record: record,
				closable: true,
				cls: 'record-tab',
				listeners: {
					removed: function(comp, ct, opts)
					{
						var rec_id;

						if(!comp.record)
							return true;
						rec_id = comp.record.getId();
						if(ct.tabCache.hasOwnProperty(rec_id))
							delete ct.tabCache[rec_id];
						return true;
					},
					scope: this
				}
			});
			this.tabCache[rec_id] = tab = this.add(cfg);
		}
		this.setActiveTab(tab);
		return tab;
	}
});

