Ext.define('NetProfile.view.ModelSelect', {
	extend: 'Ext.form.field.Trigger',
	alias: 'widget.modelselect',
	requires: [
		'Ext.window.Window'
	],
	apiModule: null,
	apiClass: null,
	hiddenField: null,
	trigger1Cls: 'x-form-clear-trigger',
	trigger2Cls: ' ',

	chooseText: 'Choose an object',

	initComponent: function()
	{
		if(!this.allowBlank)
		{
			this.trigger1Cls = this.trigger2Cls;
			this.onTrigger1Click = this.onTrigger2Click;
			this.trigger2Cls = undefined;
			this.onTrigger2Click = undefined;
		}
		this.callParent(arguments);
	},
	onTrigger1Click: function(ev)
	{
		var form = this.up('form'),
			hf = form.down('field[name=' + this.hiddenField + ']');
		if(hf)
			hf.setValue('');
		else
			form.getRecord().set(this.hiddenField, '');

		this.setValue('');
	},
	onTrigger2Click: function(ev)
	{
		var sel_win = Ext.create('Ext.window.Window', {
			layout: 'fit',
			minWidth: 500,
			maxHeight: 650,
			title: this.chooseText
		});

		var sel_grid_class = 'NetProfile.view.grid.'
			+ this.apiModule
			+ '.'
			+ this.apiClass;
		var form = this.up('form'),
			hf = form.down('field[name=' + this.hiddenField + ']');
		if(!hf)
			hf = this.hiddenField;
		var sel_grid = Ext.create(sel_grid_class, {
			rowEditing: false,
			actionCol: false,
			selectRow: true,
			selectField: this,
			selectIdField: hf,
			stateful: false
		});

		sel_win.add(sel_grid);
		sel_win.show();
	}
});

