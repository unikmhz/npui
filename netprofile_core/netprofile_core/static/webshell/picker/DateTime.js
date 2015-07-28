Ext.define('NetProfile.picker.DateTime', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.datetimepicker',
	requires: [
		'Ext.button.Button',
		'Ext.picker.Date',
		'Ext.form.field.Time'
	],

	applyText: 'Apply',
	cancelText: 'Cancel',

	layout: {
		type: 'vbox',
		align: 'stretchmax'
	},

	initComponent: function()
	{
		var me = this;

		me.items = [Ext.apply({
			itemId: 'date',
			xtype: 'datepicker',
			margin: 2,
			border: 0,
			pickerField: me.pickerField,
			listeners: {
				select: me.onSelect,
				scope: me
			}
		}, me.datePickerCfg || {}), Ext.apply({
			itemId: 'time',
			xtype: 'timefield',
			submitValue: false,
			margin: '0 2 0 2',
			listeners: {
				select: function(cmp, record)
				{
					return this.onSelect(cmp, cmp.getValue());
				},
				scope: me
			}
		}, me.timeFieldCfg || {}), {
			xtype: 'panel',
			layout: {
				type: 'hbox',
				pack: 'center',
				padding: 2
			},
			border: 0,
			items: [{
				xtype: 'button',
				iconCls: 'ico-accept',
				text: me.applyText,
				handler: function(btn, ev)
				{
					var handler = me.handler;

					me.fireEvent('select', me, me.value);
					if(handler)
						handler.call(me.scope || me, me, me.value);
				}
			}, {
				xtype: 'button',
				iconCls: 'ico-cancel',
				text: me.cancelText,
				handler: function(btn, ev)
				{
					if(me && me.pickerField)
						me.pickerField.collapse();
				}
			}]
		}];

		this.callParent(arguments);
	},
	onSelect: function(cmp, newval)
	{
		var me = this,
			itemId = cmp.getItemId(),
			value = me.value || new Date();

		value.setSeconds(0);
		value.setMilliseconds(0);
		switch(itemId)
		{
			case 'date':
				value.setFullYear(newval.getFullYear());
				value.setMonth(newval.getMonth());
				value.setDate(newval.getDate());
				break;
			case 'time':
				value.setHours(newval.getHours());
				value.setMinutes(newval.getMinutes());
				break;
			default:
				throw "Invalid itemId";
		}
		me.value = value;
	},
	initEvents: function()
	{
		var me = this;

		me.callParent();
		if(!me.focusable)
		{
			me.el.on({
				mousedown: function(ev)
				{
					ev.preventDefault();
				}
			});
		}
	},
	update: function()
	{
		var me = this,
			value = me.value || new Date(),
			dateval, timeval, cmp;

		value.setSeconds(0);
		value.setMilliseconds(0);
		dateval = Ext.clone(value);
		timeval = Ext.clone(value);

		cmp = me.getComponent('date');
		if(cmp)
			cmp.setValue(Ext.Date.clearTime(dateval));
		cmp = me.getComponent('time');
		if(cmp)
			cmp.setValue(timeval);
		return me;
	},
	setValue: function(newval)
	{
		this.value = newval;
		return this.update();
	}
});

