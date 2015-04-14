/**
 * @class NetProfile.menu.FileFolder
 * @extends Ext.menu.Menu
 */
Ext.define('NetProfile.menu.FileFolder', {
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

	view: null,
	tree: null,
	folder: null,

	initComponent: function()
	{
		var me = this;

		this.items = [{
			itemId: 'item_create',
			text: me.createText,
			iconCls: 'ico-folder-tree',
			handler: 'onCreate',
			scope: me,
			disabled: true
		}, {
			itemId: 'item_rename',
			text: me.renameText,
			iconCls: 'ico-folder-ren',
			handler: 'onRename',
			scope: me,
			disabled: true
		}, {
			itemId: 'item_props',
			text: me.propText,
			iconCls: 'ico-props',
			handler: 'onProperties',
			scope: me,
			disabled: true
		}, {
			itemId: 'item_mount',
			text: me.mountText,
			iconCls: 'ico-folder-mount',
			handler: 'onMount',
			scope: me,
			disabled: true
		}, '-', {
			itemId: 'item_delete',
			text: me.deleteText,
			iconCls: 'ico-folder-del',
			handler: 'onDelete',
			scope: me,
			disabled: true
		}];
		me.callParent(arguments);
	},
	onCreate: function(item, ev)
	{
		var me = this,
			view = me.view,
			tree = me.tree,
			rec = me.folder,
			plug = tree.getPlugin('editor'),
			subrec, callback;

		callback = function()
		{
			var anim;

			if(!plug || !rec)
				return;
			subrec = new NetProfile.model.customMenu.folders({
				parentId: rec.getId(),
				allow_read: true,
				allow_write: true,
				allow_traverse: true,
				parent_write: rec.get('allow_write'),
				text: me.newFolderText // BUGS HORRIBLY ON EMPTY
			});
			rec.appendChild(subrec);
			// XXX: RACE CONDITION!
			anim = tree.getView().getAnimWrap(rec, false);
			if(anim && anim.isAnimating)
			{
				anim.animateEl.getActiveAnimation().on('afteranimate', function(an)
				{
					plug.startEdit(subrec, view.getHeaderAtIndex(0));
				}, me, { single: true });
			}
			else
				plug.startEdit(subrec, view.getHeaderAtIndex(0));
		}

		if(rec.isExpanded())
			callback();
		else
			rec.expand(false, callback);
		me.fireEvent('create', me, ev);
	},
	onRename: function(item, ev)
	{
		var me = this,
			view = me.view,
			tree = me.tree,
			rec = me.folder,
			plug = tree.getPlugin('editor');

		if(plug && rec)
			plug.startEdit(rec, view.getHeaderAtIndex(0));
		me.fireEvent('rename', me, ev);
	},
	onProperties: function(item, ev)
	{
		var me = this,
			rec = me.folder,
			is_root = (rec.getId() === 'root'),
			pb = Ext.getCmp('npws_propbar'),
			dp = NetProfile.view.grid.core.FileFolder.prototype.detailPane,
			store = NetProfile.StoreManager.getStore(
				'core', 'FileFolder',
				null, true
			),
			is_ro = false,
			ff = { __ffilter: [] };

		if(!pb || !rec || !dp || !store || is_root)
			return false;
		ff.__ffilter.push({
			property: store.model.prototype.idProperty,
			operator: 'eq',
			value:    parseInt(rec.getId())
		});
		if(!rec.get('parent_write') || !rec.get('allow_write'))
			is_ro = true;
		store.load({
			params: ff,
			callback: function(recs, op, success)
			{
				if(!success || !recs.length)
					return;
				var xrec = recs[0];
				xrec.readOnly = is_ro;
				pb.addRecordTab('core', 'FileFolder', dp, xrec);
				pb.show();
			},
			scope: me,
			synchronous: false
		});
		me.fireEvent('properties', me, ev);
	},
	onMount: function(item, ev)
	{
		var me = this,
			rec = me.folder,
			dl = Ext.getCmp('npws_filedl');

		// TODO: maybe signal permission denied somehow?
		if(!rec.get('allow_read') || !dl)
			return false;
		dl.load({
			url: Ext.String.format(
				'{0}/core/file/mount/{1}/{2}.davmount',
				NetProfile.baseURL,
				rec.getId(), rec.get('text')
			)
		});
		me.fireEvent('mount', me, ev);
		return true;
	},
	onDelete: function(item, ev)
	{
		var me = this,
			rec = me.folder,
			store = me.tree.getStore(),
			selmod = me.tree.getSelectionModel(),
			is_sel = selmod.isSelected(rec),
			prec = rec.parentNode;

		Ext.MessageBox.confirm(
			me.deleteFolderText,
			me.deleteFolderVerboseText,
			function(btn)
			{
				if(btn === 'yes')
				{
					if(is_sel)
					{
						if(prec)
							selmod.select(prec);
						else
							selmod.deselectAll(); // XXX: potential trouble
					}
					me.folder = null;
					rec.remove();
					store.sync();
				}
				return true;
			}
		);
		me.fireEvent('delete', me, ev);
	},
	setFolder: function(rec)
	{
		var me = this,
			is_root = (rec.getId() === 'root'),
			allow_read = rec.get('allow_read'),
			allow_write = rec.get('allow_write'),
			allow_traverse = rec.get('allow_traverse'),
			parent_write = rec.get('parent_write'),

			item_create = me.getComponent('item_create'),
			item_rename = me.getComponent('item_rename'),
			item_props = me.getComponent('item_props'),
			item_mount = me.getComponent('item_mount'),
			item_delete = me.getComponent('item_delete');

		me.folder = rec;

		item_create.setDisabled(!allow_traverse || !allow_write);
		item_rename.setDisabled(!parent_write || is_root);
		item_props.setDisabled(!allow_read || is_root);
		item_mount.setDisabled(!allow_read);
		item_delete.setDisabled(!parent_write || is_root);
	}
});

