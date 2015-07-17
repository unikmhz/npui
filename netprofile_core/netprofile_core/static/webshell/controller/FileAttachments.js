/**
 * @class NetProfile.controller.FileAttachments
 * @extends Ext.app.Controller
 */
Ext.define('NetProfile.controller.FileAttachments', {
	extend: 'Ext.app.Controller',

	init: function()
	{
		this.control({
			'modelgrid[componentCls~=file-attach]': {
				beforeitemdblclick: function(gr, rec, item, idx, ev)
				{
					var dl = Ext.getCmp('npws_filedl');
					if(!dl)
						return false;
					dl.loadFileById(rec.get('fileid'));
					return false;
				},
				afterrender: this.onAfterRender
			}
		});
	},
	onAfterRender: function(me)
	{
		var view = me.getView();

		if(!view)
			return;
		view.on({
			beforedrop: function(node, data, overModel, dropPos, dropHdl)
			{
				var me = this,
					grid = me.ownerCt,
					relkey = grid.extraParamProp,
					store = grid.getStore(),
					to_add = [],
					rec, ent_id;

				rec = this.up('panel[cls~=record-tab]');
				if(!rec || !rec.record || !grid.canCreate)
					return false;
				rec = rec.record;

				if(!data || !data.records)
				{
					dropHdl.cancelDrop(); // FIXME: <-- what's that for?
					return false;
				}
				Ext.Array.forEach(data.records, function(frec)
				{
					if(frec instanceof NetProfile.model.core.File)
					{
						if(!frec.get('allow_read') || !frec.get('allow_access'))
							return;
						var addf = { fileid: frec.getId() };
						addf[relkey] = rec.getId();
						to_add.push(addf);
					}
				});
				if(to_add.length > 0)
				{
					store.add(to_add);
				}
				dropHdl.cancelDrop();
				return true;
			},
			scope: view
		});
	}
});
