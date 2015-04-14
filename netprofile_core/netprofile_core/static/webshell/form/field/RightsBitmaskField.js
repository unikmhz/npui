/**
 * @class NetProfile.form.field.RightsBitmaskField
 * @extends Ext.form.FieldContainer
 */
Ext.define('NetProfile.form.field.RightsBitmaskField', {
	extend: 'Ext.form.FieldContainer',
	mixins: {
		field: 'Ext.form.field.Field'
	},
	alias: 'widget.filerights',
	requires: [
		'Ext.form.Label',
		'Ext.form.field.Checkbox'
	],

	ownerText: 'Owner',
	groupText: 'Group',
	otherText: 'Other',
	readText: 'Read',
	writeText: 'Write',
	executeText: 'Execute',
	traverseText: 'Traverse',

	layout: {
		type: 'table',
		itemCls: 'np-rights-el',
		columns: 4,
		tableAttrs: {
			cls: 'x-table-layout np-rights-tbl'
		}
	},
	vLabelCfg: {
		xtype: 'label',
		cellCls: 'vlabel'
	},
	hLabelCfg: {
		xtype: 'label',
		cellCls: 'hlabel'
	},
	checkBoxCfg: {
		xtype: 'checkbox',
		width: '100%'
	},
	isDirectory: false,

	value: 0,

	initComponent: function()
	{
		var me = this,
			xval = (parseInt(me.value) & 0x01ff),
			cbcfg;

		cbcfg = Ext.apply({
			disabled: !!me.disabled,
			readOnly: !!me.readOnly
		}, me.checkBoxCfg);
		me.value = xval;
		me.items = [
			Ext.apply({}, me.hLabelCfg),
			Ext.apply({ text: me.ownerText }, me.vLabelCfg),
			Ext.apply({ text: me.groupText }, me.vLabelCfg),
			Ext.apply({ text: me.otherText }, me.vLabelCfg),
			Ext.apply({ text: me.readText }, me.hLabelCfg),
			Ext.apply({ itemId: 'u_r' }, cbcfg),
			Ext.apply({ itemId: 'g_r' }, cbcfg),
			Ext.apply({ itemId: 'o_r' }, cbcfg),
			Ext.apply({ text: me.writeText }, me.hLabelCfg),
			Ext.apply({ itemId: 'u_w' }, cbcfg),
			Ext.apply({ itemId: 'g_w' }, cbcfg),
			Ext.apply({ itemId: 'o_w' }, cbcfg),
			Ext.apply({ text: (me.isDirectory ? me.traverseText : me.executeText) }, me.hLabelCfg),
			Ext.apply({ itemId: 'u_x' }, cbcfg),
			Ext.apply({ itemId: 'g_x' }, cbcfg),
			Ext.apply({ itemId: 'o_x' }, cbcfg)
		];
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
		var idx = cbid.split('_'),
			mask = 0;

		if(idx.length !== 2)
			throw 'Invalid checkbox ID';
		switch(idx[1])
		{
			case 'r':
				mask = 0x4;
				break;
			case 'w':
				mask = 0x2;
				break;
			case 'x':
				mask = 0x1;
				break;
			default:
				throw 'Invalid checkbox ID';
				break;
		}
		switch(idx[0])
		{
			case 'u':
				mask <<= 6;
				break;
			case 'g':
				mask <<= 3;
				break;
			case 'o':
				break;
			default:
				throw 'Invalid checkbox ID';
				break;
		}
		return mask;
	},
	getValue: function()
	{
		return this.value;
	},
	setValue: function(val)
	{
		var me = this;

		me.value = (parseInt(val) & 0x01ff);
		if(me.rendered)
			me.updateCheckedFromValue();
	},
	updateCheckedFromValue: function()
	{
		var me = this,
			xval = (me.value & 0x01ff),
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
		me.value = (xval & 0x01ff);
	}
});

