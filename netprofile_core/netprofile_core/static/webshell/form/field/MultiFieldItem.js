/**
 * @class NetProfile.form.field.MultiFieldItem
 * @extends Ext.form.FieldContainer
 */
Ext.define('NetProfile.form.field.MultiFieldItem', {
	extend: 'Ext.form.FieldContainer',
	mixins: {
		field: 'Ext.form.field.Field'
	},
	alias: 'widget.multifielditem',

	addFieldText: 'Add Field',
	removeFieldText: 'Remove Field',
	upText: 'Move Up',
	downText: 'Move Down',

	addBtnCfg: {
		xtype: 'button',
		iconCls: 'ico-plus'
	},
	removeBtnCfg: {
		xtype: 'button',
		iconCls: 'ico-minus'
	},
	upBtnCfg: {
		xtype: 'button',
		iconCls: 'ico-arrow-up'
	},
	downBtnCfg: {
		xtype: 'button',
		iconCls: 'ico-arrow-down'
	},

	readOnly: false,
	showUp: true,
	showDown: true,
	showAdd: false,
	showRemove: true,

	layout: {
		type: 'hbox',
		align: 'middle',
		defaultMargins: {
			right: 2
		},
		pack: 'end'
	},
	width: '100%',

	initComponent: function()
	{
		var me = this;

		if(!me.items)
			me.items = [];
		me.fieldLength = me.items.length;
		if(me.showUp && !me.readOnly)
			me.items.push(Ext.apply({}, me.upBtnCfg, {
				itemId: 'btn-up',
				tooltip: me.upText,
				handler: function(btn, ev)
				{
					me.fireEvent('moveup', me, ev);
				}
			}));
		if(me.showDown && !me.readOnly)
			me.items.push(Ext.apply({}, me.downBtnCfg, {
				itemId: 'btn-down',
				tooltip: me.downText,
				handler: function(btn, ev)
				{
					me.fireEvent('movedown', me, ev);
				}
			}));
		if(me.showAdd && !me.readOnly)
			me.items.push(Ext.apply({}, me.addBtnCfg, {
				itemId: 'btn-add',
				tooltip: me.addFieldText,
				handler: function(btn, ev)
				{
					me.fireEvent('additem', me, ev);
				}
			}));
		if(me.showRemove && !me.readOnly)
			me.items.push(Ext.apply({}, me.removeBtnCfg, {
				itemId: 'btn-remove',
				tooltip: me.removeFieldText,
				handler: function(btn, ev)
				{
					me.fireEvent('removeitem', me, ev);
				}
			}));
		me.callParent(arguments);
	},
	getValue: function()
	{
		if(this.fieldLength > 1)
		{
			// TODO
		}
		var el = this.items.first();

		if(el && el.getValue)
			return el.getValue();
	},
	setValue: function(val)
	{
		if(this.fieldLength > 1)
		{
			// TODO
		}
		var el = this.items.first();

		if(el && el.setValue)
			return el.setValue(val);
	},
	isValid: function()
	{
		var valid = true,
			idx, el;

		for(idx = 0; idx < this.fieldLength; idx++)
		{
			el = this.items.getAt(idx);
			if(!el || !el.isValid || !el.isValid())
				valid = false;
		}
		return valid;
	}
});

