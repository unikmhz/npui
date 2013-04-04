/**
 * @class NetProfile.controller.FileFolders
 * @extends Ext.app.Controller
 */
Ext.define('NetProfile.controller.FileFolders', {
	extend: 'Ext.app.Controller',
	requires: [
		'NetProfile.view.FileFolderContextMenu'
	],

	init: function()
	{
		this.control({
			'treepanel[id=npmenu_tree_folders]': {
				itemcontextmenu: this.onFolderCtxMenu
			}
		});
	},
	onFolderCtxMenu: function(el, rec, item, idx, ev)
	{
		var menu;

		ev.stopEvent();
//		console.log('EL', el);
//		console.log('REC', rec);
//		console.log('ITEM', item);
//		console.log('IDX', idx);
//		console.log('THIS', this);

		menu = Ext.create('NetProfile.view.FileFolderContextMenu', {
			record: rec
		});
		menu.showAt(ev.getXY());
		return false;
	}
});

