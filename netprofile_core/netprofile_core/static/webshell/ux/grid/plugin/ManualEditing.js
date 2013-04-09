Ext.define('Ext.ux.grid.plugin.ManualEditing', {
	alias: 'plugin.manualediting',
	extend: 'Ext.grid.plugin.CellEditing',

	// Work around the workaround
	// See Ext.tree.View:onItemDblClick
	clicksToEdit: 3,

	initEditTriggers: function()
	{
		var me = this,
			view = me.view;

		me.initAddRemoveHeaderEvents();
		view.on('render', me.initKeyNavHeaderEvents, me, { single: true });
	}
});

