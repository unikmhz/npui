Ext.define('Ext.ux.form.field.DateTime', {
	extend: 'Ext.form.field.Date',
	alias: 'widget.datetimefield',
	requires: [
		'Ext.ux.DateTimePicker'
	],

	initComponent: function()
	{
		this.format = this.format + ' ' + 'H:i:s';
		this.callParent();
	},
	// overwrite
	createPicker: function()
	{
		var me = this,
			format = Ext.String.format;

		return Ext.create('Ext.ux.DateTimePicker', {
			ownerCt: me.ownerCt,
			renderTo: document.body,
			floating: true,
			hidden: true,
			focusOnShow: true,
			minDate: me.minValue,
			maxDate: me.maxValue,
			disabledDatesRE: me.disabledDatesRE,
			disabledDatesText: me.disabledDatesText,
			disabledDays: me.disabledDays,
			disabledDaysText: me.disabledDaysText,
			format: me.format,
			showToday: me.showToday,
			startDay: me.startDay,
			minText: format(me.minText, me.formatDate(me.minValue)),
			maxText: format(me.maxText, me.formatDate(me.maxValue)),
			listeners: {
				scope: me,
				select: me.onSelect
			},
			keyNavConfig: {
				esc: function() {
					me.collapse();
				}
			}
		});
	},

	// PATCHED
	getErrors: function(value)
	{
		var me = this,
			format = Ext.String.format,
			errors = me.superclass.superclass.getErrors.apply(me, arguments),
			disabledDays = me.disabledDays,
			disabledDatesRE = me.disabledDatesRE,
			minValue = me.minValue,
			maxValue = me.maxValue,
			len = disabledDays ? disabledDays.length : 0,
			i = 0,
			svalue, fvalue, day, time;

		value = me.formatDate(value || me.processRawValue(me.getRawValue()));

		if(value === null || value.length < 1) // if it's blank and textfield didn't flag it then it's valid
			return errors;

		svalue = value;
		value = me.parseDate(value);
		if(!value)
		{
			errors.push(format(me.invalidText, svalue, Ext.Date.unescapeFormat(me.format)));
			return errors;
		}

		time = value.getTime();
		if(minValue && time < minValue.getTime())
			errors.push(format(me.minText, me.formatDate(minValue)));

		if(maxValue && time > maxValue.getTime())
			errors.push(format(me.maxText, me.formatDate(maxValue)));

		if(disabledDays)
		{
			day = value.getDay();

			for(; i < len; i++)
			{
				if(day === disabledDays[i])
				{
					errors.push(me.disabledDaysText);
					break;
				}
			}
		}

		fvalue = me.formatDate(value);
		if(disabledDatesRE && disabledDatesRE.test(fvalue))
			errors.push(format(me.disabledDatesText, fvalue));

		return errors;
	}
});

