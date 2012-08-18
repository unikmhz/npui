Ext.define('NetProfile.view.ModelSelect', {
	extend: 'Ext.form.field.Trigger',
	alias: 'widget.modelselect',
	requires: [
	],
	apiModule: null,
	apiClass: null,
	onTriggerClick: function(ev) {
		var sel_win = Ext.create('Ext.window.Window', {
			layout: 'fit',
			minWidth: 500,
			maxHeight: 650,
			title: 'Choose an object'
		});

		var sel_grid_class = 'NetProfile.view.grid.'
			+ this.apiModule
			+ '.'
			+ this.apiClass;
		var sel_grid = Ext.create(sel_grid_class, {
			rowEditing: false,
			actionCol: false,
			selectRow: true,
			stateful: false
		});

		sel_win.show();
		sel_win.add(sel_grid);
	}
});

