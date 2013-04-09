/**
 * @class NetProfile.controller.FileFolders
 * @extends Ext.app.Controller
 */
Ext.define('NetProfile.controller.FileFolders', {
	extend: 'Ext.app.Controller',
	requires: [
		'NetProfile.model.core.File',
		'NetProfile.view.FileFolderContextMenu'
	],

	init: function()
	{
		this.control({
			'treepanel[id=npmenu_tree_folders]': {
				afterrender: this.onAfterRender,
				itemcontextmenu: this.onFolderCtxMenu,
				beforeedit: function(ed, ev)
				{
					if(!ev.record || !ev.record.get('parent_write'))
						return false;
				},
				edit: function(ed, ev)
				{
					var st = ed.grid.getStore();
					if(!ev.record || !ev.record.get('parent_write'))
						return false;
					if(st)
						st.sync();
				}
			}
		});
	},
	onAfterRender: function(tp)
	{
		var view = tp.getView();

		if(!view)
			return;
		view.on({
			drop: function(node, data, overModel, dropPos)
			{
				var drop_ff = false,
					panel, store;

				if(!Ext.isElement(node) || !data || !data.records)
					return;
				Ext.Array.forEach(data.records, function(rec)
				{
					if(rec instanceof NetProfile.model.customMenu.folders)
						drop_ff = true;
				});
				if(drop_ff)
				{
					panel = data.view.ownerCt;
					store = panel.getStore();
					if(store)
						store.sync();
				}
			},
			beforedrop: function(node, data, overModel, dropPos, dropHdl)
			{
				var stores = [],
					can_write = false,
					drop_ff = false,
					ffid;

				if(dropPos !== 'append')
					return false;
				if(!Ext.isElement(node) || !overModel || !data || !data.records)
				{
					dropHdl.cancelDrop(); // FIXME: <-- what's that for?
					return false;
				}
				if(overModel.getId() == 'root')
				{
					if(NetProfile.rootFolder)
					{
						ffid = NetProfile.rootFolder.id;
						can_write = NetProfile.rootFolder.allow_write;
					}
					else
					{
						ffid = null;
						can_write = true; // FIXME
					}
				}
				else
				{
					ffid = parseInt(overModel.getId());
					can_write = overModel.get('allow_write');
				}
				if(!can_write)
				{
					dropHdl.cancelDrop(); // FIXME: <-- what's that for?
					return false;
				}
				Ext.Array.forEach(data.records, function(rec)
				{
					if(rec instanceof NetProfile.model.core.File)
					{
						rec.set('ffid', ffid);
						if(rec.store && !(rec.store in stores))
							stores.push(rec.store);
					}
					else if(rec instanceof NetProfile.model.customMenu.folders)
						drop_ff = true;
				});
				Ext.Array.forEach(stores, function(st)
				{
					st.sync();
					st.reload();
				});
				if(!drop_ff)
					dropHdl.cancelDrop();
				return true;
			}
		});
	},
	onFolderCtxMenu: function(el, rec, item, idx, ev)
	{
		var menu;

		ev.stopEvent();
		menu = Ext.create('NetProfile.view.FileFolderContextMenu', {
			allowRename: rec.get('parent_write'),
			allowDelete: rec.get('parent_write')
		});
		menu.on({
			create: function(ev)
			{
				var tree = el.up('treepanel'),
					plug = tree.getPlugin('editor'),
					subrec, cb;

				cb = function()
				{
					var anim;

					if(!plug || !rec)
						return;
					subrec = new NetProfile.model.customMenu.folders({
						parentId: rec.getId(),
						parent_write: rec.get('allow_write'),
						text: 'New Folder' // BUGS HORRIBLY ON EMPTY
					});
					rec.appendChild(subrec);
					// XXX: RACE CONDITION!
					anim = tree.getView().getAnimWrap(rec, false);
					if(anim && anim.isAnimating)
					{
						anim.animateEl.getActiveAnimation().on('afteranimate', function(an)
						{
							plug.startEdit(subrec, el.getHeaderAtIndex(0));
						}, this, { single: true });
					}
					else
						plug.startEdit(subrec, el.getHeaderAtIndex(0));
				};

				if(rec.isExpanded())
					cb();
				else
					rec.expand(false, cb);
			},
			rename: function(ev)
			{
				var plug = el.up('treepanel').getPlugin('editor');

				if(plug && rec)
					plug.startEdit(rec, el.getHeaderAtIndex(0));
			},
			scope: this
		});
		menu.showAt(ev.getXY());
		return false;
	}
});

