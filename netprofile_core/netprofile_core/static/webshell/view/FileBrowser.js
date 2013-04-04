/**
 * @class NetProfile.view.FileBrowser
 * @extends Ext.form.Panel
 */
Ext.define('NetProfile.view.FileBrowser', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.filebrowser',
	stateId: 'npws_filebrowser',
	stateful: true,
	requires: [
		'Ext.form.*',
		'Ext.menu.*',
		'NetProfile.store.core.File',
		'NetProfile.view.FileIconView'
	],

	border: 0,
	layout: 'fit',

	store: null,
	view: null,
	folder: null,
	viewType: 'icon',
	sortType: 'fname',
	sortDir: 'ASC',
	searchStr: null,
	uploadUrl: NetProfile.baseURL + '/core/file/ul',

	viewText: 'View',
	viewAsIconsText: 'Icons',
	viewAsListText: 'List',
	viewAsGridText: 'Grid',

	sortText: 'Sort',
	sortByNameText: 'By Filename',
	sortByCTimeText: 'By Creation Time',
	sortByMTimeText: 'By Modification Time',
	sortBySizeText: 'By Size',

	sortAscText: 'Sort Ascending',
	sortDescText: 'Sort Descending',

	btnDeleteText: 'Delete',

	deleteTipText: 'Delete File',
	deleteMsgText: 'Are you sure you want to delete selected file?',
	deleteManyTipText: 'Delete Files',
	deleteManyMsgText: 'Are you sure you want to delete selected files?',

	btnUploadText: 'Upload',

	uploadTitleText: 'Upload Files',
	uploadCloseText: 'Close',
	uploadAddText: 'Add',
	uploadUploadText: 'Upload',
	uploadRemoveText: 'Remove',
	uploadWaitMsg: 'Uploading Files...',

	btnPropsText: 'Properties',
	btnDownloadText: 'Download',

	searchEmptyText: 'Search...',

	initComponent: function()
	{
		if(!this.store)
			this.store = Ext.create('NetProfile.store.core.File', {
				autoDestroy: true,
				autoLoad: false,
				buffered: false,
				pageSize: -1
			});
		this.ctxMenu = Ext.create('Ext.menu.Menu', {
			items: [{
				text: this.btnPropsText,
				iconCls: 'ico-props'
			}, {
				itemId: 'dl_item',
				text: this.btnDownloadText,
				iconCls: 'ico-save',
				handler: function(btn, ev)
				{
					var rec;

					rec = this.ctxMenu.record;
					if(!rec)
						return false;
					return this.onFileOpen(rec);
				},
				scope: this
			}, '-', {
				itemId: 'del_item',
				text: this.btnDeleteText,
				iconCls: 'ico-delete',
				handler: function(btn, ev)
				{
					var rec;

					rec = this.ctxMenu.record;
					if(!rec)
						return false;
					if(!Ext.isArray(rec))
						rec = [rec];
					return this.deleteRecords(rec);
				},
				scope: this
			}]
		});
		this.selectedRecords = [];
		this.tbar = [{
			text: this.viewText,
			iconCls: 'ico-view',
			menu: [{
				itemId: 'icon',
				text: this.viewAsIconsText,
				checked: true,
				group: 'view',
				checkHandler: this.onViewChange,
				scope: this
			}, {
				itemId: 'list',
				text: this.viewAsListText,
				checked: false,
				group: 'view',
				checkHandler: this.onViewChange,
				scope: this
			}, {
				itemId: 'grid',
				text: this.viewAsGridText,
				checked: false,
				group: 'view',
				checkHandler: this.onViewChange,
				scope: this
			}]
		}, {
			text: this.sortText,
			iconCls: 'ico-sort',
			menu: [{
				itemId: 'fname',
				text: this.sortByNameText,
				checked: true,
				group: 'sort',
				checkHandler: this.onSortChange,
				scope: this
			}, {
				itemId: 'ctime',
				text: this.sortByCTimeText,
				checked: false,
				group: 'sort',
				checkHandler: this.onSortChange,
				scope: this
			}, {
				itemId: 'mtime',
				text: this.sortByMTimeText,
				checked: false,
				group: 'sort',
				checkHandler: this.onSortChange,
				scope: this
			}, {
				itemId: 'size',
				text: this.sortBySizeText,
				checked: false,
				group: 'sort',
				checkHandler: this.onSortChange,
				scope: this
			}, '-', {
				itemId: 'ASC',
				text: this.sortAscText,
				checked: true,
				group: 'sdir',
				checkHandler: this.onSortDirChange,
				scope: this
			}, {
				itemId: 'DESC',
				text: this.sortDescText,
				checked: true,
				group: 'sdir',
				checkHandler: this.onSortDirChange,
				scope: this
			}]
		}, '-', {
			text: this.btnDeleteText,
			iconCls: 'ico-delete',
			itemId: 'btn_delete',
			disabled: true,
			handler: function(btn, ev)
			{
				var me = this;

				this.deleteRecords(this.selectedRecords, function()
				{
					me.selectedRecords = [];
				});
			},
			scope: this
		}, '-', {
			text: this.btnUploadText,
			iconCls: 'ico-upload',
			itemId: 'btn_upload',
			disabled: true,
			menu: {
				xtype: 'menu',
				layout: 'fit',
				showSeparator: false,
				resizable: true,
				defaults: {
					plain: true
				},
				items: [{
					xtype: 'form',
					url: this.uploadUrl,
					layout: 'anchor',
					defaults: {
						anchor: '100%'
					},
					minWidth: 300,
					minHeight: 200,
					title: this.uploadTitleText,
					items: [],
					buttons: [{
						text: this.uploadCloseText,
						iconCls: 'ico-cancel',
						handler: function(btn, ev)
						{
							var xform = this.up('form');

							Ext.Array.forEach(
								xform.query('container[cls~=np-file-upload-cont]'),
								function(cont) { this.remove(cont, true); }, xform
							);
							this.up('menu').hide();
						}
					}, '->', {
						text: this.uploadAddText,
						iconCls: 'ico-add',
						handler: function(btn, ev)
						{
							var xform = btn.up('form');
							if(xform)
								xform.add(this.getUploadField());
						},
						scope: this
					}, {
						text: this.uploadUploadText,
						iconCls: 'ico-upload',
						handler: function(btn, ev)
						{
							var xform = this.getUploadForm(),
								form = xform.getForm();

							if(form && form.isValid())
							{
								form.submit({
									params: this.getUploadParams(),
									success: function(rform, act)
									{
										var xform = rform.owner;

										this.updateStore();
										Ext.Array.forEach(
											xform.query('container[cls~=np-file-upload-cont]'),
											function(cont) { this.remove(cont, true); }, xform
										);
										xform.up('menu').hide();
									},
									failure: function(rform, act)
									{
									},
									scope: this,
									waitMsg: this.uploadWaitMsg
								});
							}
						},
						scope: this
					}]
				}],
				listeners: {
					beforeshow: function(m)
					{
						var f = m.down('form');

						if(f)
						{
							Ext.Array.forEach(
								f.query('container[cls~=np-file-upload-cont]'),
								function(cont) { this.remove(cont, true); }, f
							);
							f.add(this.getUploadField());
						}
					},
					scope: this
				}
			}
		}, '->', {
			xtype: 'textfield',
			cls: 'np-ssearch-field',
			itemId: 'search_fld',
			hideLabel: true,
			emptyText: this.searchEmptyText,
			listeners: {
				change: function(fld, newval, oldval)
				{
					this.fireEvent('searchchange', newval);
				},
				scope: this
			}
		}];
		this.callParent(arguments);

		this.on({
			beforedestroy: this.onBeforeDestroy,
			beforerender: this.onBeforeRender,
			folderupdate: this.onFolderUpdate,
			searchchange: {
				fn: this.onSearchChange,
				buffer: 500
			}
		});
	},
    getState: function()
	{
		var state = this.callParent();

		state = this.addPropertyToState(state, 'viewType');
		state = this.addPropertyToState(state, 'sortType');
		state = this.addPropertyToState(state, 'sortDir');
		return state;
	},
	onBeforeDestroy: function(me)
	{
		if(me.store)
		{
			Ext.destroy(me.store);
			me.store = null;
		}
		if(me.ctxMenu)
		{
			me.ctxMenu.hide();
			Ext.destroy(me.ctxMenu);
			me.ctxMenu = null;
		}
		return true;
	},
	onBeforeRender: function(me)
	{
		Ext.Array.forEach(me.query('menucheckitem[group=view]'), function(cki)
		{
			if(cki.itemId == me.viewType)
				cki.setChecked(true);
			else
				cki.setChecked(false);
		});
		Ext.Array.forEach(me.query('menucheckitem[group=sort]'), function(cki)
		{
			if(cki.itemId == me.sortType)
				cki.setChecked(true);
			else
				cki.setChecked(false);
		});
		Ext.Array.forEach(me.query('menucheckitem[group=sdir]'), function(cki)
		{
			if(cki.itemId == me.sortDir)
				cki.setChecked(true);
			else
				cki.setChecked(false);
		});
		this.renderView();
		this.fireEvent('folderupdate', this);
		return true;
	},
	setFolder: function(frec)
	{
		this.fireEvent('beforefolderupdate', this, frec);
		this.folder = frec;
		this.updateStore();
		this.fireEvent('folderupdate', this);
	},
	updateStore: function()
	{
		var qparam;

		if(this.folder === null)
			qparam = { __ffilter: { ffid: { eq: null } } };
		else
			qparam = { __ffilter: { ffid: { eq: this.folder.getId() } } };
		// TODO: insert other search criteria here
		if(this.searchStr)
			qparam.__sstr = this.searchStr;
		qparam.__sort = [{ direction: this.sortDir, property: this.sortType }];
		this.store.load({
			params: qparam,
			callback: function(recs, op, success)
			{
				this.fireEvent('load', this, recs, op, success);
			},
			scope: this,
			synchronous: false
		});
	},
	renderView: function()
	{
		this.fireEvent('beforerenderview', this);
		if(this.view)
		{
			this.remove(this.view, true);
			this.view = null;
		}
		switch(this.viewType)
		{
			case 'icon':
				this.view = this.add({
					xtype: 'fileiconview',
					store: this.store,
					listeners: {
						selectionchange: function(dv, nodes)
						{
							this.onSelectionChange(nodes);
						},
						itemdblclick: function(el, rec, item, idx, ev)
						{
							this.onFileOpen(rec, ev);
						},
						itemcontextmenu: function(el, rec, item, idx, ev)
						{
							var can_act = true,
								is_sel = this.view.isSelected(item),
								mi;

							ev.stopEvent();
							if(this.folder && !this.folder.get('allow_write'))
								can_act = false;
							else if(!rec.get('allow_write'))
								can_act = false;
							mi = this.ctxMenu.getComponent('del_item');
							if(mi)
								mi.setDisabled(!can_act);
							if(is_sel && (this.selectedRecords.length > 1))
								can_act = false;
							else
								can_act = rec.get('allow_read');
							mi = this.ctxMenu.getComponent('dl_item');
							if(mi)
								mi.setDisabled(!can_act);
							if(is_sel && (this.selectedRecords.length > 1))
								this.ctxMenu.record = this.selectedRecords;
							else
								this.ctxMenu.record = rec;
							this.ctxMenu.showAt(ev.getXY());
							return false;
						},
						filesdropped: function(view, files, ev)
						{
							this.uploadFileList(files);
						},
						scope: this
					}
				});
				break;
			case 'list':
				break;
			case 'grid':
				break;
			default:
				break;
		}
	},
	onSearchChange: function(sstr)
	{
		if(this.searchStr !== sstr)
		{
			this.searchStr = sstr;
			this.updateStore();
		}
	},
	onSelectionChange: function(nodes)
	{
		var tbar, cmp;

		this.selectedRecords = nodes;
		tbar = this.down('toolbar[dock=top]');
		if(!tbar)
			return;
		cmp = tbar.getComponent('btn_delete');
		if(cmp)
		{
			if(this.folder && !this.folder.get('allow_write'))
				cmp.setDisabled(true);
			else if(nodes.length)
			{
				var can_delete = true;

				Ext.Array.forEach(nodes, function(n)
				{
					if(!n.get('allow_write'))
						can_delete = false;
				});
				if(can_delete)
					cmp.setDisabled(false);
			}
			else
				cmp.setDisabled(true);
		}
	},
	onFolderUpdate: function(me)
	{
		var tbar = me.down('toolbar[dock=top]'),
			btn_upload = tbar.getComponent('btn_upload');

		if(me.folder)
		{
			if(btn_upload)
			{
				if(me.folder.get('allow_write'))
					btn_upload.setDisabled(false);
				else
					btn_upload.setDisabled(true);
			}
		}
		else
		{
			if(btn_upload)
				btn_upload.setDisabled(false);
		}
	},
	onFileOpen: function(rec, ev)
	{
		// TODO: maybe signal permission denied somehow?
		if(!rec.get('allow_read'))
			return false;
		var dl = Ext.getCmp('npws_filedl');
		if(!dl)
			return false;
		dl.load({
			url: Ext.String.format(
				'{0}/core/file/dl/{1}/{2}',
				NetProfile.baseURL,
				rec.getId(), rec.get('fname')
			)
		});
		return true;
	},
	onViewChange: function(cki, checked)
	{
		if(checked && (this.viewType !== cki.itemId))
		{
			this.viewType = cki.itemId;
			this.renderView();
			this.saveState();
		}
	},
	onSortChange: function(cki, checked)
	{
		if(checked && (this.sortType !== cki.itemId))
		{
			this.sortType = cki.itemId;
			this.saveState();
			this.updateStore();
		}
	},
	onSortDirChange: function(cki, checked)
	{
		if(checked && (this.sortDir !== cki.itemId))
		{
			this.sortDir = cki.itemId;
			this.saveState();
			this.updateStore();
		}
	},
	getUploadField: function()
	{
		var cfg = {
			xtype: 'container',
			cls: 'np-file-upload-cont',
			layout: {
				type: 'hbox',
				align: 'stretch',
				pack: 'end'
			},
			defaults: {
				margin: 0
			},
			items: [{
				xtype: 'filefield',
				name: 'file',
				flex: 1,
				allowBlank: false
			}, {
				xtype: 'tool',
				cls: 'np-file-upload-close',
				tooltip: this.uploadRemoveText,
				type: 'close',
				handler: function()
				{
					var cont, pcont;

					cont = this.up('container[cls~=np-file-upload-cont]');
					if(!cont || !cont.ownerCt)
						return;
					pcont = cont.ownerCt;
					pcont.remove(cont, true);
				},
				width: 20
			}]
		};
		return cfg;
	},
	getUploadForm: function()
	{
		var cmp;

		cmp = this.down('toolbar[dock=top]');
		if(!cmp)
			return null;
		cmp = cmp.getComponent('btn_upload');
		if(!cmp || !cmp.menu)
			return null;
		return cmp.menu.down('form');
	},
	getUploadParams: function()
	{
		var p = {};

		if(this.folder)
			p.ffid = this.folder.getId();
		return p;
	},
	uploadFileList: function(files)
	{
		var i, fd, param;

		if(typeof(FormData) === 'undefined')
			return false;
		if(this.folder && !this.folder.get('allow_write'))
			return false;
			// TODO: alert 'no permission'

		fd = new FormData();
		param = this.getUploadParams();
		Ext.Object.each(param, function(k, v)
		{
			fd.append(k, v);
		});
		for(i = 0; i < files.length; i++)
		{
			fd.append('file', files[i]);
		}
		this.mask(this.uploadWaitMsg);
		Ext.Ajax.request({
			url: this.uploadUrl,
			method: 'POST',
			rawData: fd,
			callback: function(opt, success, response)
			{
				this.unmask();
				this.updateStore();
			},
			scope: this
		});
		return true;
	},
	deleteRecords: function(recs, onyes)
	{
		var delnum, can_del = true;

		if(this.folder && !this.folder.get('allow_write'))
			return false;
		delnum = recs.length;
		Ext.Array.forEach(recs, function(r)
		{
			if(!r.get('allow_write'))
				can_del = false;
		});
		if(!can_del)
			return false;

		Ext.MessageBox.confirm(
			(delnum > 1 ? this.deleteManyTipText : this.deleteTipText),
			(delnum > 1 ? this.deleteManyMsgText : this.deleteMsgText),
			function(btn)
			{
				if(btn === 'yes')
				{
					this.store.remove(recs);
					if(typeof(onyes) === 'function')
						onyes(recs);
				}
				return true;
			},
			this
		);
		return true;
	}
});

