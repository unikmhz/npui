Ext.define('NetProfile.view.PropBar', {
	extend: 'Ext.tab.Panel',
	alias: 'widget.propbar',
	requires: [
		'Ext.tab.Panel'
	],
	id: 'npws_propbar',
	stateId: 'npws_propbar',
	stateful: true,
	collapsible: true,
	headerPosition: 'right',
	header: {
		xtype: 'header',
		titleAlign: 'right'
	},
//	header: false,
	hidden: true,
	animCollapse: true,
	layout: 'fit',
//	title: 'Property bar',
	split: true,
	height: '40%',
	minHeight: 300,
	border: 0,
	record: null,
	apiModule: null,
	apiClass: null,
	items: [
	],
	tools: [],

	initComponent: function() {
		this.tools = [{
			itemId: 'refresh',
			type: 'refresh',
			tooltip: 'Repopulate property bar.',
			handler: function() {
			},
			scope: this
		}, {
			itemId: 'close',
			type: 'close',
			tooltip: 'Close property bar.',
			handler: function() {
				this.hide();
			},
			scope: this
		}];
		this.callParent(arguments);
	},
	getRecord: function()
	{
		return this.record;
	},
	setRecord: function(rec)
	{
		this.record = rec;
	},
	getApiModule: function()
	{
		return this.apiModule;
	},
	setApiModule: function(am)
	{
		this.apiModule = am;
	},
	getApiClass: function()
	{
		return this.apiClass;
	},
	setApiClass: function(ac)
	{
		this.apiClass = ac;
	},
	setContext: function(record, am, ac)
	{
		this.record = record;
		this.apiModule = am;
		this.apiClass = ac;
	}
});
