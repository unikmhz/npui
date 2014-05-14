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
	mountText: 'Mount',
	newFolderText: 'New Folder',
	deleteFolderText: 'Delete Folder',
	deleteFolderVerboseText: 'Are you sure you want to delete this folder?',

	allowCreate: true,
	allowRename: true,
	allowProperties: true,
	allowDelete: true,
	allowMount: true,

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
		}, {
			text: this.mountText,
			iconCls: 'ico-folder-mount',
			handler: function(btn, ev)
			{
				this.fireEvent('mount', ev);
			},
			scope: this,
			disabled: !this.allowMount
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

