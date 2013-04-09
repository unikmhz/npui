/**
 * @class NetProfile.view.FileFolderContextMenu
 * @extends Ext.menu.Menu
 */
Ext.define('NetProfile.view.FileFolderContextMenu', {
	extend: 'Ext.menu.Menu',
	require: [
		'Ext.menu.*'
	],

	createText: 'Create Subfolder',
	propText: 'Properties',
	renameText: 'Rename',
	deleteText: 'Delete',

	allowCreate: true,
	allowRename: true,
	allowProperties: true,
	allowDelete: true,

	listeners: {
		hide: function(menu)
		{
			Ext.destroy(menu);
		}
	},

	initComponent: function()
	{
		this.items = [{
			text: this.createText,
			iconCls: 'ico-folder-tree',
			handler: function(btn, ev)
			{
				this.fireEvent('create', ev);
			},
			scope: this,
			disabled: !this.allowCreate
		}, {
			text: this.renameText,
			iconCls: 'ico-folder-ren',
			handler: function(btn, ev)
			{
				this.fireEvent('rename', ev);
			},
			scope: this,
			disabled: !this.allowRename
		}, {
			text: this.propText,
			iconCls: 'ico-props',
			handler: function(btn, ev)
			{
				this.fireEvent('properties', ev);
			},
			scope: this,
			disabled: !this.allowProperties
		}, '-', {
			text: this.deleteText,
			iconCls: 'ico-folder-del',
			handler: function(btn, ev)
			{
				this.fireEvent('delete', ev);
			},
			scope: this,
			disabled: !this.allowDelete
		}];
		this.callParent(arguments);
	}
});

