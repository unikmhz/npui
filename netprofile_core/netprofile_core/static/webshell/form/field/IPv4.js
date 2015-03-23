/**
 * @class NetProfile.form.field.IPv4
 * @extends Ext.form.field.Base
 */
Ext.define('NetProfile.form.field.IPv4', {
	extend: 'Ext.form.field.Base',
	alias: 'widget.ipv4field',
	requires: [
		'Ext.form.field.Number',
		'Ext.button.Button'
	],
	fieldSubTpl: [
		'<div class="ipv4-field-input1" style="display: inline-block; vertical-align: bottom;"></div>',
		'<div class="ipv4-field-input1-spacer" style="display: inline-block; padding: 0 3px; vertical-align: baseline;">.</div>',
		'<div class="ipv4-field-input2" style="display: inline-block; vertical-align: bottom;"></div>',
		'<div class="ipv4-field-input2-spacer" style="display: inline-block; padding: 0 3px; vertical-align: baseline;">.</div>',
		'<div class="ipv4-field-input3" style="display: inline-block; vertical-align: bottom;"></div>',
		'<div class="ipv4-field-input3-spacer" style="display: inline-block; padding: 0 3px; vertical-align: baseline;">.</div>',
		'<div class="ipv4-field-input4" style="display: inline-block; vertical-align: bottom;"></div>',
		'<div class="ipv4-field-btns" style="display: inline-block; vertical-align: bottom; padding-left: 5px;"></div>',
		'<div class="ipv4-field-hidden"></div>',
		{
			disableFormats: true
		}
	],
	defaults: {
		border: 0
	},
	clearTipText: 'Clear field',
	octetFieldProto: {
		xtype: 'numberfield',
		maxLength: 3,
		allowDecimals: false,
		allowNegative: false,
		minValue: 0,
		maxValue: 255,
		hideLabel: true,
		hideTrigger: true,
		width: 30,
		submitValue: false,
		selectOnFocus: true,
		fieldStyle: 'text-align: right;'
	},
	value: null,
	createInput: function(idx, oct)
	{
		var me = this,
			el = me.getEl(),
			fdname = 'oct' + idx,
			ctname = fdname + 'Ct';

//		me[ctname] = Ext.query('.ipv4-field-input' + idx, this.el.dom)[0];
		me[ctname] = el.query('.ipv4-field-input' + idx)[0];
		me[fdname] = Ext.create('Ext.form.field.Number', Ext.apply(
			{},
			{
				renderTo: me[ctname],
				allowBlank: me.allowBlank ? true : false,
				disabled: me.disabled ? true : false,
				parentComponent: me,
				itemId: fdname,
				enableKeyEvents: true,
				value: (oct && (oct.length === 4)) ? oct[idx - 1] : '',
				submitValue: false,
				listeners: {
					change: function(fld, val)
					{
						var ipre = /^\s*\d+\.\d+\.\d+\.\d+\s*$/,
							sval = String(fld.getRawValue()),
							oldval;

						if(ipre.test(sval))
						{
							oldval = me.value;
							me.setRawValue(sval);
							if((oldval === null) || (me.value && (oldval.toString() != me.value.toString())))
								me.fireEvent('change', me, me.value, oldval);
							return true;
						}
						me.parseFields();
						return true;
					},
					keydown: function(fld, ev)
					{
						var k = ev.getKey(),
							octnum = parseInt(this.itemId.substr(3, 1));

						if(octnum < 4)
						{
							if((k === 190) || (k === ev.NUM_PERIOD) || (k === ev.TAB))
							{
								ev.stopEvent();
								me['oct' + (octnum + 1)].focus();
							}
						}
					}
				}
			},
			me.octetFieldProto || {}
		));
//		me[fdname].getEl().dom.removeAttribute('name');
	},
	onRender: function(pn, idx)
	{
		var me = this,
			el = me.getEl(),
			i, oct;

		me.callParent([pn, idx]);

		if(me.value)
			oct = me.value.toByteArray();
		else
			oct = false;

		for(i = 1; i < 5; i++)
			me.createInput(i, oct);

		i = el.query('.ipv4-field-btns')[0];

		if(me.allowBlank && !me.readOnly)
		{
			me.clearBtn = Ext.create('Ext.button.Button', {
				iconCls: 'ico-clear',
				renderTo: i,
				tooltip: me.clearTipText,
				shrinkWrap: 0,
				height: 22,
				width: 22,
				listeners: {
					click: function(fld, ev)
					{
						if(!me.disabled)
						{
							var oldval = me.value;

							me.clearValue();
							if(oldval !== null)
								me.fireEvent('change', me, me.value, oldval);
						}
					}
				}
			});
		}
	},
	getRawValue: function()
	{
		return this.value;
	},
	getFieldOctets: function()
	{
		var me = this;

		if(!me.oct1.isValid() || !me.oct2.isValid() || !me.oct3.isValid() || !me.oct4.isValid())
			throw 'Invalid octets found'
		return [
			me.oct1.getValue(),
			me.oct2.getValue(),
			me.oct3.getValue(),
			me.oct4.getValue()
		];
	},
	updateFields: function()
	{
		var me = this,
			oct = me.value.toByteArray();

		if(me.oct1)
			me.oct1.setRawValue(oct[0]);
		if(me.oct2)
			me.oct2.setRawValue(oct[1]);
		if(me.oct3)
			me.oct3.setRawValue(oct[2]);
		if(me.oct4)
			me.oct4.setRawValue(oct[3]);
	},
	parseFields: function()
	{
		var me = this,
			oldval = me.value,
			oct, ectr = 0;

		try
		{
			oct = me.getFieldOctets();
			oct = Ext.Array.map(oct, function(o)
			{
				if((o === null) || (o === undefined) || (o === ''))
				{
					ectr ++;
					if(!me.allowBlank)
						throw 'Invalid octets found'
				}
				return parseInt(o) || 0;
			});
			if(ectr === 4)
				me.value = null;
			else
				me.value = new ipaddr.IPv4(oct);
		}
		catch(e)
		{
			me.validate();
			me.markInvalid([e]);
			return false;
		}
		if(me.validate() && ((oldval && !me.value.match(oldval, 32)) || !oldval))
			me.fireEvent('change', me, me.value, oldval);
		return true;
	},
	setRawValue: function(val)
	{
		var me = this;

		if((val === null) || (val === undefined) || (val === ''))
			return me.clearValue();
		if(Ext.isObject(val))
		{
			if(!(val instanceof ipaddr.IPv4))
				throw "Supplied with an unknown object type";
		}
		else
			val = ipaddr.IPv4.parse(val);
		me.value = val;
		me.updateFields();
		return true;
	},
	clearValue: function()
	{
		var me = this;

		me.value = null;
		if(me.oct1)
			me.oct1.setRawValue('');
		if(me.oct2)
			me.oct2.setRawValue('');
		if(me.oct3)
			me.oct3.setRawValue('');
		if(me.oct4)
			me.oct4.setRawValue('');
		return true;
	},
	isValid: function()
	{
		var me = this,
			valid = true;

		if(me.disabled)
			return true;
		if(me.oct1 && !me.oct1.isValid())
			valid = false;
		if(me.oct2 && !me.oct2.isValid())
			valid = false;
		if(me.oct3 && !me.oct3.isValid())
			valid = false;
		if(me.oct4 && !me.oct4.isValid())
			valid = false;

		if(!valid)
		{
			if(!me.preventMark)
				me.markInvalid();
			return false;
		}
		if(!me.preventMark)
			me.clearInvalid();
		return true;
	}
});

