/**
 * @class NetProfile.form.field.IPv4
 * @extends Ext.form.FieldContainer
 */
Ext.define('NetProfile.form.field.IPv4', {
	extend: 'Ext.form.FieldContainer',
	mixins: {
		field: 'Ext.form.field.Field'
	},
	alias: 'widget.ipv4field',
	requires: [
		'Ext.form.field.Number',
		'Ext.button.Button'
	],

	statics: {
		ipRegEx: /^\s*\d+\.\d+\.\d+\.\d+\s*$/,
		filterValue: function(val)
		{
			if((val === null) || (val === undefined) || (val === ''))
				return null;
			if(Ext.isArray(val))
				return new ipaddr.IPv4(val);
			if(Ext.isObject(val))
			{
				if(val instanceof ipaddr.IPv4)
					return val;
				else if('octets' in val)
					return new ipaddr.IPv4(val.octets);
				return null;
			}
			return ipaddr.IPv4.parse(val);
		}
	},

	octetErrorText: 'Octet {0}: {1}',
	blankText: 'This field can not be blank',

	config: {
		layout: {
			type: 'hbox',
			align: 'end',
			enableSplitters: false
		},
		octetFieldCfg: {
			xtype: 'numberfield',
			allowBlank: true,
			allowDecimals: false,
			allowExponential: false,
			enableKeyEvents: true,
			fieldStyle: 'text-align: right;',
			maxLength: 3,
			maxValue: 255,
			minValue: 0,
			msgTarget: 'none',
			hideLabel: true,
			hideTrigger: true,
			width: '2.5em',
			selectOnFocus: true,
			submitValue: false
		},
		clearBtnCfg: {
			xtype: 'button',
			iconCls: 'ico-clear',
			margin: '0 0 0 3',
			tooltip: 'Clear field'
		},
		separatorCfg: {
			xtype: 'component',
			border: false,
			html: '.',
			padding: '0 2 3 2'
		}
	},

	initComponent: function()
	{
		var me = this,
			cfg;

		me.callParent(arguments);
		me.initField();

		me.oct = [
			me.createOctet(1, me.value ? me.value.octets[0] : null),
			me.createOctet(2, me.value ? me.value.octets[1] : null),
			me.createOctet(3, me.value ? me.value.octets[2] : null),
			me.createOctet(4, me.value ? me.value.octets[3] : null)
		];

		if(me.allowBlank && !me.readOnly)
		{
			cfg = Ext.apply({
				listeners: {
					scope: me,
					click: 'onClear'
				}
			}, me.clearBtnCfg);
			me.clearBtn = me.add(cfg);
		}
		else
			me.clearBtn = null;

		me.on({
			destroy: function(cmp)
			{
				Ext.destroyMembers(cmp, 'oct', 'clearBtn');
			}
		});
	},
	initValue: function()
	{
		var me = this;

		me.value = me.statics().filterValue(me.value);
		me.mixins.field.initValue.call(me);
	},
	resetOriginalValue: function()
	{
		var me = this;

		Ext.each(me.oct, function(oct)
		{
			oct.resetOriginalValue();
		});
		me.mixins.field.resetOriginalValue.call(me);
	},
	getErrors: function(value)
	{
		var me = this,
			errs = me.mixins.field.getErrors(value),
			err;

		if(me.asyncErrors && me.asyncErrors.length)
			errs = errs.concat(me.asyncErrors);
		if(!me.allowBlank && me.isBlank())
			errs.push(me.blankText);
		Ext.each(me.oct, function(oct, idx)
		{
			var err = oct.getErrors(),
				i = 0;
			for(; i < err.length; i++)
			{
				errs.push(Ext.String.format(me.octetErrorText, idx + 1, err[i]));
			}
		});
		return errs;
	},
	validate: function()
	{
		var me = this,
			errors,
			isValid,
			wasValid;

		if(me.disabled)
			isValid = true;
		else
		{
			errors = me.getErrors();
			isValid = Ext.isEmpty(errors);
			wasValid = me.wasValid;
			if(isValid)
				me.unsetActiveError();
			else
				me.setActiveError(errors);
		}

		if(isValid !== wasValid)
		{
			me.wasValid = isValid;
			me.fireEvent('validitychange', me, isValid);
			me.updateLayout();
		}

		return isValid;
	},
	createOctet: function(octnum, octval, cfg)
	{
		var me = this,
			oct = Ext.apply(
				me.octetFieldCfg || {},
				cfg || {}
			);

		oct.itemId = 'oct' + octnum;
		if(typeof(octval) === 'number')
			octval = octval.toString();
		oct.value = octval;
		if(typeof(me.readOnly) === 'boolean')
			oct.readOnly = me.readOnly;
		if(typeof(me.disabled) === 'boolean')
			oct.disabled = me.disabled;
		oct = me.add(oct);
		oct.on({
			scope: me,
			change: 'onFieldChange',
			keydown: 'onFieldKeyDown'
		});
		if(octnum < 4)
			me.add(me.separatorCfg);
		return oct;
	},
	onFieldChange: function(fld, newval, oldval)
	{
		var me = this,
			ipre = me.statics().ipRegEx,
			sval = String(fld.getRawValue());

		if(ipre.test(sval))
		{
			me.setValue(sval);
			return true;
		}
		me.parseFields();
		me.fireEvent('fieldchange', me, fld, newval, oldval);
		return true;
	},
	onFieldKeyDown: function(fld, ev)
	{
		var me = this,
			k = ev.getKey(),
			octnum;

		if((k === 190) || (k === ev.NUM_PERIOD))
		{
			octnum = parseInt(fld.getItemId().substr(3, 1));
			if(octnum < 4)
			{
					ev.stopEvent();
					me.oct[octnum].focus();
			}
		}
	},
	onClear: function(btn, ev)
	{
		var me = this;
		this.clearValue();
		return true;
	},
	getFieldValues: function()
	{
		var me = this;

		return me.oct.map(function(oct)
		{
			return oct.getRawValue();
		});
	},
	updateFields: function()
	{
		var me = this,
			octval;

		if(me.value)
			octval = me.value.toByteArray();
		else
			octval = ['', '', '', ''];
		Ext.each(me.oct, function(oct, octnum)
		{
			oct.setRawValue(octval[octnum].toString());
		});
	},
	isBlank: function()
	{
		var me = this,
			blank = true;

		Ext.each(me.oct, function(oct)
		{
			var octval = oct.getValue();
			if((octval !== null) && (octval !== ''))
				blank = false;
		});
		return blank;
	},
	parseFields: function()
	{
		var me = this,
			oldval = me.value,
			oct = me.getFieldValues(),
			ectr = 0,
			newval = null;

		if(!me.allowBlank && me.isBlank())
		{
			me.validate();
			return me;
		}
		try
		{
			oct = oct.map(function(o)
			{
				if((o === null) || (o === undefined) || (o === ''))
					ectr ++;
				return parseInt(o) || 0;
			});
			if(ectr < 4)
				newval = new ipaddr.IPv4(oct);
		}
		catch(e)
		{
			me.validate();
			me.markInvalid([e]);
			return me;
		}
		if(newval)
			return me.setValue(newval);
		return me.clearValue();
	},
	setValue: function(val)
	{
		var me = this,
			oldval = me.value,
			fire = false;

		me.value = me.statics().filterValue(val);
		me.updateFields();
		if(me.value !== oldval && ((me.value === null) || (oldval === null)))
			fire = true;
		else if(me.value && oldval && !me.value.match(oldval, 32))
			fire = true;
		if(fire)
			me.fireEvent('change', me, me.value, oldval);
		return me;
	},
	clearValue: function()
	{
		var me = this,
			oldval = me.value;

		me.value = null;
		me.updateFields();
		if(oldval !== null)
			me.fireEvent('change', me, null, oldval);
		return me;
	},
});

