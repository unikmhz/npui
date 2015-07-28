/**
 * @class NetProfile.form.field.NullableComboBox
 * @extends Ext.form.field.ComboBox
 */
Ext.define('NetProfile.form.field.NullableComboBox', {
	extend: 'Ext.form.field.ComboBox',
	alias: [
		'widget.nullablecombobox',
		'widget.nullablecombo'
	],

	config: {
		triggers: {
			clear: {
				cls: Ext.baseCSSPrefix + 'form-clear-trigger',
				weight: -1,
				handler: 'onTriggerClear'
			}
		}
	},

	onTriggerClear: function(ev)
	{
		var me = this,
			form = me.up('form'),
			hf;

		if(me.hiddenField && form)
		{
			hf = form.down('field[name=' + me.hiddenField + ']');
			if(hf)
				hf.setValue('');
			else
			{
				hf = form.getRecord();
				if(hf)
					hf.set(me.hiddenField, '');
			}
		}
		me.setValue(null);
	}
});

