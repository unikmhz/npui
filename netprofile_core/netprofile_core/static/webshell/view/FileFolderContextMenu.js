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
	deleteText: 'Delete',

	initComponent: function()
	{
		this.items = [{
			text: this.createText
		}, {
			text: this.propText,
			iconCls: 'ico-props'
		}, '-', {
			text: this.deleteText,
			iconCls: 'ico-delete'
		}];
		this.callParent(arguments);
	}
});

