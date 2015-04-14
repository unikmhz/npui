/**
 * @class NetProfile.controller.FileFolders
 * @extends Ext.app.Controller
 */
Ext.define('NetProfile.controller.FileFolders', {
	extend: 'Ext.app.Controller',
	requires: [
		'NetProfile.model.core.File',
		'NetProfile.model.core.FileFolder',
		'NetProfile.menu.FileFolder'
	],

	init: function()
	{
		this.control({
			'treepanel[id=npmenu_tree_folders]': {
				afterrender: this.onAfterRender,
				itemcontextmenu: this.onFolderCtxMenu,
				beforeedit: function(ed, ev)
				{
					var rec = ev.record;

					if(!rec || !rec.get('parent_write'))
						return false;
					if(rec.getId() === 'root')
						return false;
				},
				edit: function(ed, ev)
				{
					var st = ed.grid.getStore(),
						selmod = ed.grid.getSelectionModel(),
						rec;
					if(!ev.record || !ev.record.get('parent_write'))
						return false;
					rec = ev.record;
					if(st)
						st.sync({
							success: function(batch, opts)
							{
								selmod.deselectAll();
								selmod.select(rec);
							}
						});
				},
				canceledit: function(ed, ev)
				{
					var selmod = ed.grid.getSelectionModel(),
						rec = ev.record,
						prec = rec.parentNode,
						is_sel = selmod.isSelected(rec);

					if(is_sel)
					{
						if(prec)
							selmod.select(prec);
						else
							selmod.deselectAll();
					}
					if(rec.phantom)
						rec.remove();
				}
			}
		});
	},
	onAfterRender: function(tp)
	{
		var view = tp.getView(),
			root;

		root = tp.getStore().getById('root');
		if(root && NetProfile.rootFolder)
		{
			root.set('allow_read', NetProfile.rootFolder.allow_read);
			root.set('allow_write', NetProfile.rootFolder.allow_write);
			root.set('allow_traverse', NetProfile.rootFolder.allow_traverse);
			root.set('parent_write', NetProfile.rootFolder.parent_write);
		}

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
					ffid, rr, rec;

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
				for(rr in data.records)
				{
					rec = data.records[rr];
					if(rec instanceof NetProfile.model.customMenu.folders)
					{
						if(!rec.get('parent_write'))
						{
							dropHdl.cancelDrop(); // FIXME: <-- what's that for?
							return false;
						}
						drop_ff = true;
					}
				}
				Ext.Array.forEach(data.records, function(rec)
				{
					if(rec instanceof NetProfile.model.core.File)
					{
						rec.set('ffid', ffid);
						if(rec.store && !(rec.store in stores))
							stores.push(rec.store);
					}
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
		ev.stopEvent();
		if(!el.ctxMenu)
		{
			el.ctxMenu = Ext.create('NetProfile.menu.FileFolder', {
				view: el,
				tree: el.up('treepanel')
			});
			el.ctxMenu.setFolder(rec);
		}
		else
		{
			el.ctxMenu.hide();
			el.ctxMenu.setFolder(rec);
		}
		el.ctxMenu.showAt(ev.getXY());
		return false;
	}
});

