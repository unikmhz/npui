/**
 * @class NetProfile.form.field.PropertyTree
 * @extends Ext.form.FieldContainer
 */
Ext.define('NetProfile.form.field.PropertyTree', {
	extend: 'Ext.form.FieldContainer',
	mixins: {
		field: 'Ext.form.field.Field'
	},
	alias: 'widget.proptreefield',
	requires: [
		'NetProfile.tree.Property'
	],
	config: {
		treeCfg: {
			xtype: 'propertytree',
			height: 100,
			minHeight: 100,
			scrollable: 'vertical',
			resizable: true
		},
		layout: 'fit'
	},

	initComponent: function()
	{
		var me = this,
			tree_cfg = {};

		Ext.apply(tree_cfg, {
			itemId: 'tree'
		}, me.getTreeCfg());
		me.items = [tree_cfg];

		me.callParent();
	},
	getValue: function()
	{
		var me = this,
			tree = me.getComponent('tree');

		return tree.getJSValue();
	},
	setValue: function(val)
	{
		var me = this,
			tree = me.getComponent('tree');

		return tree.setJSValue(val);
	}
});
