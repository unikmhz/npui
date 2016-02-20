/**
 * @class NetProfile.form.field.HardwareAddress
 * @extends Ext.form.field.Text
 */
Ext.define('NetProfile.form.field.HardwareAddress', {
	extend: 'Ext.form.field.Text',
	alias: 'widget.hwaddrfield',

	config: {
		selectOnFocus: true,
		fieldStyle: 'padding-left: 20px;',
		beforeBodyEl: '<div class="input-icon ico-hwaddr" unselectable="on">&nbsp;</div>'
	},

	invalidAddressText: 'Invalid hardware address',

	rxStandard: /^([\da-f]{1,2}):([\da-f]{1,2}):([\da-f]{1,2}):([\da-f]{1,2}):([\da-f]{1,2}):([\da-f]{1,2})$/i,
	rxWindows: /^([\da-f]{1,2})-([\da-f]{1,2})-([\da-f]{1,2})-([\da-f]{1,2})-([\da-f]{1,2})-([\da-f]{1,2})$/i,
	rxIEEE: /^([\da-f]{1,4})\.([\da-f]{1,4})\.([\da-f]{1,4})$/i,

	normalizeAddress: function(raw)
	{
		var me = this,
			chunks = [],
			rx, i, chunk;

		if(typeof(raw) !== 'string')
			return null;
		raw = Ext.String.trim(raw);
		if(raw === '')
			return null;

		if(rx = (me.rxStandard.exec(raw) || me.rxWindows.exec(raw)))
		{
			for(idx = 1; idx < rx.length; idx++)
			{
				chunk = rx[idx].toLowerCase();
				if(chunk.length === 1)
					chunk = '0' + chunk;
				chunks.push(chunk);
			}
		}
		else if(rx = me.rxIEEE.exec(raw))
		{
			for(idx = 1; idx < rx.length; idx++)
			{
				chunk = String("000" + rx[idx].toLowerCase());
				chunks.push(
					chunk.slice(-4, -2),
					chunk.slice(-2)
				);
			}
		}

		if(chunks.length === 6)
			return chunks.join(':');
		return null;
	},
	rawToValue: function(value)
	{
		return this.normalizeAddress(value);
	},
	valueToRaw: function(value)
	{
		return this.normalizeAddress(value);
	},
	getErrors: function(value)
	{
		var me = this,
			errors = me.callParent(arguments);

		if(!me.allowBlank && (me.normalizeAddress(value) === null))
			errors.push(me.invalidAddressText);
		return errors;
	}
});

