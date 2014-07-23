/**
 * @class NetProfile.view.SimpleModelSelect
 * @extends Ext.form.field.ComboBox
 */
Ext.define('NetProfile.view.NullableComboBox', {
	extend: 'Ext.form.field.ComboBox',
	alias: 'widget.nullablecombobox',
	requires: [
	],
	apiModule: null,
	apiClass: null,
	hiddenField: null,
	extraParams: null,

	editable: false,
	valueField: '__str__',
	displayField: '__str__',
	trigger2Cls: 'x-form-clear-trigger',

	onTrigger2Click: function(ev)
	{
		var form = this.up('form'),
			hf = form.down('field[name=' + this.hiddenField + ']');
		if(hf)
			hf.setValue('');
		else
			form.getRecord().set(this.hiddenField, '');

		this.setValue('');
	},
});

