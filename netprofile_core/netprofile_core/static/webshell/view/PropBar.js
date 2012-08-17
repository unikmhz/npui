Ext.define('NetProfile.view.PropBar', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.propbar',
	id: 'npws_propbar',
	stateId: 'npws_propbar',
	stateful: true,
	collapsible: true,
	hidden: true,
	animCollapse: true,
	layout: 'fit',
	title: 'Property bar',
	split: true,
	height: '40%',
	minHeight: 300,
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
});
