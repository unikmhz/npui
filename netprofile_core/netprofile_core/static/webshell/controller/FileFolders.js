/**
 * @class NetProfile.controller.FileFolders
 * @extends Ext.app.Controller
 */
Ext.define('NetProfile.controller.FileFolders', {
	extend: 'Ext.app.Controller',
	requires: [
		'NetProfile.model.core.File',
		'NetProfile.model.core.FileFolder',
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
					var rec = ev.record;

					if(!rec || !rec.get('parent_write'))
						return false;
					if(rec.getId() === 'root')
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
		var is_root = (rec.getId() === 'root'),
			menu;

		ev.stopEvent();
		menu = Ext.create('NetProfile.view.FileFolderContextMenu', {
			allowProperties: !is_root,
			allowRename: rec.get('parent_write') && !is_root,
			allowDelete: rec.get('parent_write') && !is_root
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
						text: menu.newFolderText // BUGS HORRIBLY ON EMPTY
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
			'delete': function(ev)
			{
				Ext.MessageBox.confirm(
					menu.deleteFolderText,
					menu.deleteFolderVerboseText,
					function(btn)
					{
						if(btn === 'yes')
							rec.remove(true);
						return true;
					},
					this
				);
			},
			properties: function(ev)
			{
				var pb = Ext.getCmp('npws_propbar'),
					dp = NetProfile.view.grid.core.FileFolder.prototype.detailPane,
					store = NetProfile.StoreManager.getStore(
						'core',
						'FileFolder',
						null, true, true
					),
					can_wr = true,
					ff = { __ffilter: [] },
					xrec;

				if(!pb || !rec || !dp || !store)
					return false;
				ff.__ffilter.push({
					property: store.model.prototype.idProperty,
					operator: 'eq',
					value:    parseInt(rec.getId())
				});
				if(is_root || !rec.get('parent_write'))
					can_wr = false;
				store.load({
					params: ff,
					callback: function(recs, op, success)
					{
						if(!success || !recs.length)
							return;
						var xrec = recs[0];
						xrec.readOnly = !can_wr || !rec.get('allow_write');
						pb.addRecordTab('core', 'FileFolder', dp, xrec);
						pb.show();
					},
					scope: this,
					synchronous: false
				});
			},
			mount: function(ev)
			{
				// TODO: maybe signal permission denied somehow?
				if(!rec.get('allow_read'))
					return false;
				var dl = Ext.getCmp('npws_filedl');
				if(!dl)
					return false;
				dl.load({
					url: Ext.String.format(
						'{0}/core/file/mount/{1}/{2}.davmount',
						NetProfile.baseURL,
						rec.getId(), rec.get('text')
					)
				});
				return true;
			},
			scope: this
		});
		menu.showAt(ev.getXY());
		return false;
	}
});

