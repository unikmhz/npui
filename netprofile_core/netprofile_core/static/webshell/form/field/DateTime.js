Ext.define('NetProfile.form.field.DateTime', {
	extend: 'Ext.form.field.Date',
	alias: [
		'widget.datetimefield',
		'widget.datetime'
	],
	requires: [
		'NetProfile.picker.DateTime'
	],

	format: 'Y-m-d H:i',
	altFormats: 'Y-m-d H:i|Y-m-d H:i:s|Y-m-d\\TH:i:s|Y-m-d\\TH:i:sP|C',

	timeFormat: 'g:i A',
	altTimeFormats: 'g:ia|g:iA|g:i a|g:i A|h:i|g:i|H:i|ga|ha|gA|h a|g a|g A|gi|hi|gia|hia|g|H|gi a|hi a|giA|hiA|gi A|hi A',

	createPicker: function()
	{
		var me = this,
			format = Ext.String.format;

		return new NetProfile.picker.DateTime({
			floating: true,
			focusable: false,
			hidden: true,
			pickerField: me,
			datePickerCfg: {
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
				keyNavConfig: {
					esc: function()
					{
						me.collapse();
					}
				}
			},
			timeFieldCfg: {
				snapToIncrement: me.snapTimeToIncrement || false,
				increment: me.timeIncrement || 15,
				minValue: me.minTimeValue,
				maxValue: me.maxTimeValue,
				format: me.timeFormat,
				altFormats: me.altTimeFormats
			},
			listeners: {
                scope: me,
                select: me.onSelect
			}
		});
	},
});

