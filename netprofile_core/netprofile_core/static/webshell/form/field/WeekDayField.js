/**
 * @class NetProfile.form.field.WeekDayField
 * @extends Ext.form.FieldContainer
 */
Ext.define('NetProfile.form.field.WeekDayField', {
	extend: 'Ext.form.FieldContainer',
	mixins: {
		field: 'Ext.form.field.Field'
	},
	alias: 'widget.weekdays',
	requires: [
		'Ext.form.Label',
		'Ext.form.field.Checkbox'
	],

	layout: {
		type: 'table',
		columns: 2,
	},
	checkBoxCfg: {
		xtype: 'checkbox',
		labelAlign: 'right',
		labelSeparator: ''
	},

	value: 0,

	initComponent: function()
	{
		var me = this,
			xval = (parseInt(me.value) & 0x7f),
			items = [],
			i;

		for(i = 0; i < 7; i++)
		{
			items.push(Ext.apply({
				fieldLabel: Ext.Date.dayNames[(i == 6) ? 0 : (i + 1)],
				itemId: 'day' + i
			}, me.checkBoxCfg));
		}
		me.value = xval;
		me.items = items;
		me.callParent(arguments);
		Ext.Array.forEach(me.query('checkbox'), function(cb)
		{
			cb.on('change', me.updateValueFromChecked, me);
		});
		me.initField();
		me.on({
			beforerender: me.onBeforeRender
		});
	},
	onBeforeRender: function(me)
	{
		me.updateCheckedFromValue();
	},
	_getMaskFromId: function(cbid)
	{
		return 1 << parseInt(cbid.substring(3));
	},
	getValue: function()
	{
		return this.value;
	},
	setValue: function(val)
	{
		var me = this;

		me.value = (parseInt(val) & 0x7f);
		if(me.rendered)
			me.updateCheckedFromValue();
	},
	updateCheckedFromValue: function()
	{
		var me = this,
			xval = (me.value & 0x7f),
			mask;

		Ext.Array.forEach(me.query('checkbox'), function(cb)
		{
			mask = me._getMaskFromId(cb.getItemId());
			cb.suspendEvents();
			if(xval & mask)
				cb.setValue(true);
			else
				cb.setValue(false);
			cb.resumeEvents();
			cb.resetOriginalValue();
		});
	},
	updateValueFromChecked: function()
	{
		var me = this,
			xval = 0,
			mask;

		Ext.Array.forEach(me.query('checkbox'), function(cb)
		{
			mask = me._getMaskFromId(cb.getItemId());
			if(cb.getValue())
				xval |= mask;
			else
				xval &= ~mask;
		});
		me.value = (xval & 0x7f);
	}
});

