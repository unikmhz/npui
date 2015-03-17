/**
 * @class NetProfile.controller.Users
 * @extends Ext.app.Controller
 */
Ext.define('NetProfile.controller.Users', {
	extend: 'Ext.app.Controller',
	requires: [
		'Ext.data.Store',
		'NetProfile.model.ConsoleMessage'
	],

	init: function()
	{
		this.control({
			'treepanel[id=npmenu_tree_users]': {
				load: this.onStoreLoad,
				itemclick: this.onUserClick
			}
		});
	},
	onStoreLoad: function(store, recs, succ, op, node, opts)
	{
		var uids, obj, i;

		if(NetProfile.rtActiveUIDs)
		{
			uids = NetProfile.rtActiveUIDs;
			NetProfile.rtActiveUIDs = null;

			Ext.Array.forEach(recs, function(rec)
			{
				var ids = rec.getId().split('-'),
					oid = parseInt(ids[1]);
				if(Ext.Array.contains(uids, oid))
					rec.set('iconCls', 'ico-status-online');
			});
		}
	},
	onUserClick: function(panel, rec, item, idx, ev)
	{
		var pbar = Ext.getCmp('npws_propbar'),
			ids = rec.getId().split('-'),
			ico = rec.get('iconCls'),
			rec_type = ids[0],
			rec_id = parseInt(ids[1]),
			str_id = 'cons:' + rec_type + ':' + rec_id,
			store = NetProfile.StoreManager.getConsoleStore(rec_type, rec_id),
			tab;

		if(ico !== 'ico-status-online')
			return;

		tab = pbar.addConsoleTab(str_id, {
			xtype: 'grid',
			title: rec.get('text'),
			iconCls: 'ico-conversation',
			store: store,
			viewConfig: {
				preserveScrollOnRefresh: true
			},
			columns: [{
				text: 'Date',
				dataIndex: 'ts',
				width: 120,
				xtype: 'datecolumn',
				format: Ext.util.Format.dateFormat + ' H:i:s'
			}, {
				text: 'Message',
				dataIndex: 'data',
				flex: 1,
				sortable: false,
				filterable: false,
				menuDisabled: true,
				editor: null,
				renderer: function(val, meta, rec)
				{
					var ret = '',
						from = rec.get('from'),
						btype = rec.get('bodytype'),
						cssPrefix = Ext.baseCSSPrefix,
						cls = [cssPrefix + 'cons-data'];

					if(from)
						ret += '<strong>' + Ext.String.htmlEncode(from) + ':</strong> ';
					if(btype in NetProfile.rtMessageRenderers)
						ret += NetProfile.rtMessageRenderers[btype](val, meta, rec);
					else
						ret += Ext.String.htmlEncode(val);
					return '<div class="' + cls.join(' ') + '">' + ret + '</div>';
				}
			}],
			listeners: {
				afterrender: function(grid)
				{
					grid.dropFile = new Ext.dd.DropZone(grid.getEl(), {
						ddGroup: 'ddFile',
						getTargetFromEvent: function(ev)
						{
							return grid;
						},
						onNodeOver: function(tgt, dd, ev, data)
						{
							return Ext.dd.DropZone.prototype.dropAllowed;
						},
						onNodeDrop: function(tgt, dd, ev, data)
						{
							var store = tgt.getStore();

							Ext.Array.each(data.records, function(file)
							{
								var rec = Ext.create('NetProfile.model.ConsoleMessage'),
									msg, val;

								val = {
									id: file.getId(),
									fname: file.get('fname'),
									mime: file.get('mime_img')
								};
								msg = {
									type: 'direct',
									msgtype: rec_type,
									to: rec_id,
									bodytype: 'file',
									msg: val
								};
								rec.set('ts', new Date());
								rec.set('from', NetProfile.currentUser);
								rec.set('bodytype', 'file');
								rec.set('data', val);
								store.add(rec);
								NetProfile.rtSocket.send(Ext.JSON.encode(msg));
							});
							return true;
						}
					});
				}
			}
		}, function(val)
		{
			if(!NetProfile.rtSocket)
				return;
			var msg = {
				type: 'direct',
				msgtype: rec_type,
				to: rec_id,
				msg:  val
			};
			var rec = Ext.create('NetProfile.model.ConsoleMessage');
			rec.set('ts', new Date());
			rec.set('from', NetProfile.currentUser);
			rec.set('data', val);
			store.add(rec);
			NetProfile.rtSocket.send(Ext.JSON.encode(msg));
		});
		tab.mon(store, 'add', function(st, recs, idx)
		{
			var view = tab.getView(),
				node = view.getNode(recs[0]);

			node.scrollIntoView();
		});
		pbar.show();
		tab.down('toolbar').getComponent('prompt').focus();
	}
});

