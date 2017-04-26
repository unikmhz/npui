/**
 * @class NetProfile.tree.Property
 * @extends Ext.tree.Panel
 */
Ext.define('NetProfile.tree.Property', {
	extend: 'Ext.tree.Panel',
	alias: 'widget.propertytree',
	requires: [
		'Ext.grid.column.Column',
		'Ext.grid.plugin.CellEditing',
		'Ext.grid.CellEditor',
		'Ext.tree.Column',
		'Ext.form.field.Text',
		'Ext.form.field.Number',
		'Ext.form.field.ComboBox',
		'Ext.data.ArrayStore',
		'NetProfile.data.PropertyTreeStore'
	],

	propText: 'Property',
	typeText: 'Type',
	valueText: 'Value',
	addText: 'Add node',
	addTipText: 'Add new node as a child of selected node.',
	deleteText: 'Delete node',
	deleteTipText: 'Delete selected node.',

	propMap: {
		'object': 'Object',
		'array':  'Array',
		'string': 'String',
		'int':    'Integer',
		'float':  'Float',
		'bool':   'Boolean',
		'null':   'Null'
	},
	typesWithChildren: ['object', 'array'],

	config: {
		viewConfig: {
			selectionModel: {
				type: 'rowmodel',
				mode: 'SINGLE',
				allowDeselect: true
			}
		},
		plugins: {
			ptype: 'cellediting'
		},
		rootType: 'null'
	},

	initComponent: function()
	{
		var me = this,
			typeData = [];

		Ext.Object.each(me.propMap, function(propid, propname)
		{
			typeData.push({ id: propid, value: propname });
		});

		me.columns = [{
			xtype: 'treecolumn',
			text: me.propText,
			dataIndex: 'name',
			editor: {
				xtype: 'textfield'
			}
		}, {
			xtype: 'gridcolumn',
			text: me.typeText,
			dataIndex: 'type',
			width: 60,
			renderer: function(value, meta, record, rowidx, colidx, store)
			{
				if(value in me.propMap)
					return me.propMap[value];
				return value;
			},
			editor: {
				xtype: 'combobox',
				allowBlank: false,
				editable: false,
				queryMode: 'local',
				displayField: 'value',
				valueField: 'id',
				forceSelection: true,
				store: {
					xtype: 'simplestore',
					fields: ['id', 'value'],
					data: typeData
				}
			}
		}, {
			xtype: 'gridcolumn',
			text: me.valueText,
			dataIndex: 'value',
			flex: 1,
			editor: {
				xtype: 'textfield'
			}
		}];

		me.lbar = [{
			itemId: 'add',
			iconCls: 'ico-add',
			tooltip: { text: me.addTipText, title: me.addText },
			disabled: true,
			handler: 'onButtonAdd',
			scope: me
		}, {
			itemId: 'del',
			iconCls: 'ico-delete',
			tooltip: { text: me.deleteTipText, title: me.deleteText },
			disabled: true,
			handler: 'onButtonDelete',
			scope: me
		}];

		if(!me.store)
		{
			me.store = Ext.create('NetProfile.data.PropertyTreeStore', {
				root: {
					expanded: true,
					type: me.getRootType()
				}
			});
		}

		me.callParent(arguments);

		me.on('selectionchange', 'onSelectionChange', me);
		me.store.on('update', 'onModelUpdate', me);
	},
	getJSValue: function()
	{
		return this.store.getRoot().getJSValue();
	},
	setJSValue: function(val)
	{
		var me = this,
			root = me.store.getRoot();

		root.setJSValue(val);
		me.setRootType(root.get('type'));
	},
	onSelectionChange: function(tree, rec, idx)
	{
		var me = this,
			tbar = me.down('toolbar'),
			btn_add = tbar.getComponent('add'),
			btn_del = tbar.getComponent('del');

		if(rec && (rec.length === 1))
		{
			rec = rec[0];
			btn_add.setDisabled(!Ext.Array.contains(me.typesWithChildren, rec.get('type')));
			btn_del.setDisabled(rec.isRoot());
		}
		else
		{
			btn_add.setDisabled(true);
			btn_del.setDisabled(true);
		}
	},
	onModelUpdate: function(store, rec, op, mod, details)
	{
		var me = this;

		if(!Ext.Array.contains(me.typesWithChildren, rec.get('type')))
			rec.removeAll(true);
		if(me.selection === rec)
			me.onSelectionChange(me, [rec], -1);
	},
	onButtonAdd: function(btn, ev)
	{
		var me = this,
			pnode = me.selection,
			cnode;

		if(!pnode || !Ext.Array.contains(me.typesWithChildren, pnode.get('type')))
			return;

		cnode = new NetProfile.data.PropertyTreeModel({
			name: '',
			type: 'string',
			value: ''
		});
		pnode.expand();
		pnode.appendChild(cnode);
	},
	onButtonDelete: function(btn, ev)
	{
		var me = this,
			pnode = me.selection;

		if(pnode && !pnode.isRoot())
			pnode.remove(true);
	}
});

