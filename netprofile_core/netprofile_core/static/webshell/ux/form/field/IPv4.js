/**
 * @class Ext.ux.form.field.IPv4
 * @extends Ext.form.field.Base
 */
Ext.define('Ext.ux.form.field.IPv4', {
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
	createInput: function(idx, oct)
	{
		var fdname = 'oct' + idx,
			ctname = fdname + 'Ct';

		this[ctname] = Ext.query('.ipv4-field-input' + idx, this.el.dom)[0];
		this[fdname] = Ext.create('Ext.form.field.Number', Ext.apply(
			{},
			{
				renderTo: this[ctname],
				allowBlank: this.allowBlank ? true : false,
				disabled: this.disabled ? true : false,
				parentComponent: this,
				itemId: fdname,
				enableKeyEvents: true,
				value: (oct && (oct.length === 4)) ? oct[idx - 1] : "",
				listeners: {
					change: function(fld, val)
					{
						var ipre = /^\s*\d+\.\d+\.\d+\.\d+\s*$/,
							sval = String(fld.getRawValue());

						if(ipre.test(sval))
						{
							this.parentComponent.setRawValue(sval);
							return true;
						}
						this.parentComponent.parseFields();
						return true;
					},
					keydown: function(fld, ev)
					{
						var k = ev.getKey();

						if((k === 190) || (ev.getKey() === ev.NUM_PERIOD))
						{
							ev.stopEvent();
							k = parseInt(this.itemId.substr(3, 1));
							if(k < 4)
								this.parentComponent['oct' + (k + 1)].focus();
						}
					}
				}
			},
			this.octetFieldProto || {}
		));
		this[fdname].getEl().dom.removeAttribute('name');
	},
	onRender: function(pn, idx)
	{
		var i, oct;

		this.callParent([pn, idx]);

		if(this.value)
			oct = this.value.toOctets();
		else
			oct = false;

		for(i = 1; i < 5; i++)
			this.createInput(i, oct);

		i = Ext.query('.ipv4-field-btns', this.el.dom)[0];

		if(this.allowBlank && !this.readOnly)
		{
			this.clearBtn = Ext.create('Ext.button.Button', {
				iconCls: 'ico-clear',
				renderTo: i,
				tooltip: this.clearTipText,
				shrinkWrap: 0,
				height: 22,
				width: 22,
				listeners: {
					click: function(fld, ev)
					{
						if(!this.disabled)
							this.clearValue();
					},
					scope: this
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
		return [
			this.oct1.getValue(),
			this.oct2.getValue(),
			this.oct3.getValue(),
			this.oct4.getValue()
		];
	},
	updateFields: function()
	{
		var oct = this.value.toOctets();

		if(this.oct1)
			this.oct1.setRawValue(oct[0]);
		if(this.oct2)
			this.oct2.setRawValue(oct[1]);
		if(this.oct3)
			this.oct3.setRawValue(oct[2]);
		if(this.oct4)
			this.oct4.setRawValue(oct[3]);
	},
	parseFields: function()
	{
		try
		{
			this.value = new NetProfile.data.IPv4Address();
			this.value.setOctets(this.getFieldOctets());
		}
		catch(e)
		{
			this.validate();
			this.markInvalid([e]);
			return false;
		}
		this.validate();
		return true;
	},
	setRawValue: function(val)
	{
		if((val === null) || (val === ''))
			return this.clearValue();
		if(Ext.isObject(val))
		{
			if(Ext.getClassName(val) !== 'NetProfile.data.IPv4Address')
				throw "Supplied with an unknown object type";
		}
		else
			val = new NetProfile.data.IPv4Address(val);
		this.value = val;
		this.updateFields();
		return true;
	},
	clearValue: function()
	{
		this.value = null;
		if(this.oct1)
			this.oct1.setRawValue('');
		if(this.oct2)
			this.oct2.setRawValue('');
		if(this.oct3)
			this.oct3.setRawValue('');
		if(this.oct4)
			this.oct4.setRawValue('');
		return true;
	},
	isValid: function()
	{
		var valid = true;

		if(this.disabled)
			return true;
		if(this.oct1 && !this.oct1.isValid())
			valid = false;
		if(this.oct2 && !this.oct2.isValid())
			valid = false;
		if(this.oct3 && !this.oct3.isValid())
			valid = false;
		if(this.oct4 && !this.oct4.isValid())
			valid = false;

		if(!valid)
		{
			if(!this.preventMark)
				this.markInvalid();
			return false;
		}
		if(!this.preventMark)
			this.clearInvalid();
		return true;
	}
});

