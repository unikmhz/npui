/**
 * @class NetProfile.form.field.Money
 * @extends Ext.form.field.Number
 */
Ext.define('NetProfile.form.field.Money', {
	extend: 'Ext.form.field.Number',
	alias: 'widget.moneyfield',

	config: {
		decimalPrecision: 8,
		allowExponential: false,
		submitLocaleSeparator: false,
		selectOnFocus: true,
		fieldStyle: 'text-align: right',
		beforeBodyEl: '<div class="input-icon ico-money" unselectable="on">&nbsp;</div>'
	}
});

