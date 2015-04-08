/**
 * @class NetProfile.form.field.IPv6
 * @extends Ext.form.field.Text
 */
Ext.define('NetProfile.form.field.IPv6', {
	extend: 'Ext.form.field.Text',
	alias: 'widget.ipv6field',

	invalidAddressText: 'Invalid IPv6 address',

	setValue: function(val)
	{
		if(Ext.isObject(val) && !(val instanceof ipaddr.IPv6) && ('parts' in val))
			val = new ipaddr.IPv6(val.parts);
		return this.callParent(arguments);
	},
	rawToValue: function(raw)
	{
		if((raw === null) || (raw === undefined) || (raw === ''))
			return null;
		if(!ipaddr.IPv6.isValid(raw))
			return null;
		return ipaddr.IPv6.parse(raw);
	},
	validator: function(value)
	{
		if(this.allowBlank && (value === ''))
			return true;
		if(!ipaddr.IPv6.isValid(value))
			return this.invalidAddressText;
		return true;
	}
});

