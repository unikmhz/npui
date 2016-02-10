/**
 * @class NetProfile.window.FileSelectWindow
 * @extends NetProfile.window.CenterWindow
 */
Ext.define('NetProfile.window.FileSelectWindow', {
	extend: 'NetProfile.window.CenterWindow',
	alias: 'widget.fileselectwindow',
	requires: [
		'NetProfile.panel.FileBrowser'
	],

	config: {
		minHeight: 350,
		minWidth: 650,
		width: 650,
		height: 350,

		singleSelection: true,
		showDelete: false,
		showRename: false,
		showUpload: true,
		showFolders: true
	},

	initComponent: function()
	{
		var me = this;

		me.items = [{
			xtype: 'filebrowser',
			singleSelection: me.singleSelection,
			showDelete: me.showDelete,
			showRename: me.showRename,
			showUpload: me.showUpload,
			showFolders: me.showFolders,
			stateId: null,
			stateful: false,
			onFileOpen: me.onFileOpen
		}];

		me.callParent(arguments);
	},
	onFileOpen: Ext.emptyFn
});

