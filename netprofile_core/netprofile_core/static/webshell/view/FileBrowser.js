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
		'NetProfile.store.core.File',
		'NetProfile.view.FileIconView'
	],

	border: 0,
	autoScroll: true,
	layout: 'fit',

	store: null,
	view: null,
	folder: null,
	viewType: 'icon',
	sortType: 'fname',
	sortDir: 'ASC',

	viewText: 'View',
	viewAsIconsText: 'As Icons',
	viewAsListText: 'As List',
	viewAsGridText: 'As Grid',

	sortText: 'Sort',
	sortByNameText: 'By Filename',
	sortByCTimeText: 'By Creation Time',
	sortByMTimeText: 'By Modification Time',
	sortBySizeText: 'By Size',

	sortAscText: 'Sort Ascending',
	sortDescText: 'Sort Descending',

	initComponent: function()
	{
		if(!this.store)
			this.store = Ext.create('NetProfile.store.core.File', {
				autoDestroy: true,
				autoLoad: false,
				buffered: false,
				pageSize: -1
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
		}, '-'];
		this.callParent(arguments);

		this.on('beforerender', this.onBeforeRender);
	},
    getState: function()
	{
		var state = this.callParent();

		state = this.addPropertyToState(state, 'viewType');
		state = this.addPropertyToState(state, 'sortType');
		state = this.addPropertyToState(state, 'sortDir');
		return state;
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
		this.renderView();
	},
	setFolder: function(frec)
	{
		this.folder = frec;
		this.updateStore();
	},
	updateStore: function()
	{
		var qparam;

		if(this.folder === null)
			qparam = { __ffilter: { ffid: { eq: null } } };
		else
			qparam = { __ffilter: { ffid: { eq: this.folder.getId() } } };
		// TODO: insert search/sort criteria here
		qparam.__sort = [{ direction: this.sortDir, property: this.sortType }];
		this.store.load({
			params: qparam,
			callback: function(recs, op, success)
			{
			},
			scope: this,
			synchronous: false
		});
	},
	renderView: function()
	{
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
	onSelectionChange: function(ids)
	{
		this.selectedRecords = ids;
	},
	onFileOpen: function(rec, ev)
	{
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
	}
});

