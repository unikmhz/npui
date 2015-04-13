Ext.define('NetProfile.panel.MainBar', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.mainbar',
	requires: [
		'NetProfile.tab.PropBar'
	],
	id: 'npws_mainbar',
	stateId: 'npws_mainbar',
	stateful: true,
	layout: {
		type: 'border',
		padding: 0
	},
	mainWidget: null,
	items: [{
		region: 'south',
		xtype: 'propbar',
		split: true
	}],

	removeWidget: function()
	{
		if(this.mainWidget)
			this.remove(this.mainWidget, true);
		this.mainWidget = null;
	},
	replaceWith: function(comp)
	{
		this.removeWidget();
		this.mainWidget = this.add(comp);
		return this.mainWidget;
	}
});

