/**
 * @class NetProfile.view.FileIconView
 * @extends Ext.view.View
 */
Ext.define('NetProfile.view.FileIconView', {
	extend: 'Ext.view.View',
	alias: 'widget.fileiconview',
	requires: [
		'NetProfile.view.FileNavigationModel',
		'NetProfile.plugin.LabelEditor',
		'NetProfile.plugin.Draggable',
		'NetProfile.plugin.DragSelector'
	],

	useColumns: false,
	browser: null,
	getMIME: null,
	getFileSize: null,
	iconSize: 48,
	cls: 'np-file-iview',
	emptyText: 'Folder is empty',
	sizeText: 'Size: {0}',
	mimeTypeText: 'MIME type: {0}',

	itemSelector: 'div.np-file-wrap',
	overItemCls: 'x-file-item-over',
	deferInitialRefresh: true,
	multiSelect: true,
	trackOver: true,
	scrollable: 'vertical',
	navigationModel: {
		type: 'file'
	},

	iconTpl: [
		'<tpl for=".">',
			'<div class="np-file-wrap" data-qtitle="{fname}" data-qtip="{qtip}" id="file_{fileid}">',
				'<div class="np-file-icon"><img src="{staticURL}/static/core/img/mime/{iconSz}/{mime_img}.png" onerror=\'this.onerror = null; this.src="{staticURL}/static/core/img/mime/{iconSz}/default.png"\' /></div>',
				'<span class="x-editable">{fname}</span>',
			'</div>',
		'</tpl>',
		'<div class="x-clear"></div>'
	],
	columnTpl: [
		'<tpl for=".">',
			'<div class="np-file-wrap" data-qtitle="{fname}" data-qtip="{qtip}" id="file_{fileid}" style="left: {[ Math.floor((xindex - 1) / values.maxItems) * 202 ]}px; top: {[ ((xindex - 1) % values.maxItems) * 21 ]}px;">',
				'<div class="np-file-icon"><img src="{staticURL}/static/core/img/mime/{iconSz}/{mime_img}.png" onerror=\'this.onerror = null; this.src="{staticURL}/static/core/img/mime/{iconSz}/default.png"\' /></div>',
				'<span class="x-editable">{fname}</span>',
			'</div>',
		'</tpl>'
	],

	initComponent: function()
	{
		var me = this;

		if(me.useColumns)
			me.tpl = me.columnTpl;
		else
			me.tpl = me.iconTpl;
		me.plugins = [{
			ptype: 'draggable',
			ddConfig: {
				ddGroup: 'ddFile'
			},
			ghostCls: 'np-file-iview',
			ghostTpl: [
				'<tpl for=".">',
					'<div>{fname}</div>',
				'</tpl>'
			]
		}, {
			ptype: 'dragselector'
		}, {
			ptype: 'labeleditor',
			pluginId: 'editor',
			dataIndex: 'fname',
			recordFilter: Ext.bind(function(rec)
			{
				if(this.folder && !this.folder.get('allow_write'))
					return false;
				if(!rec.get('allow_write'))
					return false;
				return true;
			}, me)
		}];
		me.emptyText = '<div class="x-view-empty">' + me.emptyText + '</div>';
		me.callParent(arguments);
		if(me.useColumns)
			me.on('resize', me.onResize, me);
		me.on({
			scope: me,
			afterrender: me.onAfterRender
		});
	},
	itemsInGroup: function()
	{
		var me = this,
			reg = me.getViewRegion(),
			sbar = Ext.getScrollbarSize(),
			len;

		if(me.useColumns)
		{
			len = reg.bottom - reg.top - sbar.height - 2;
			return Math.floor(len / 21);
		}
		len = reg.right - reg.left - sbar.width;
		return Math.floor(len / 103);
	},
	onAfterRender: function(me)
	{
		if(me.useColumns)
		{
			var el = me.getEl();

			el.dom.addEventListener(
				'mousewheel',
				me.onScroll,
				false
			);
			el.dom.addEventListener(
				'DOMMouseScroll',
				me.onScroll,
				false
			);
		}
	},
	onScroll: function(ev)
	{
		var delta = Math.max(-1, Math.min(1, (ev.wheelDelta || -ev.detail))),
			tgt = (ev.currentTarget) ? ev.currentTarget : ev.srcElement;

		if(delta == 1)
		{
			if(tgt.doScroll)
				tgt.doScroll('left');
			else
				tgt.scrollLeft -= 30;
		}
		else
		{
			if(tgt.doScroll)
				tgt.doScroll('right');
			else
				tgt.scrollLeft += 30;
		}
		ev.preventDefault();
	},
	onResize: function(w, h, oldw, oldh)
	{
		if(!oldw || !oldh)
			return;
		this.refresh();
	},
	prepareData: function(data)
	{
		var me = this,
			qtip_cont = [];

		data.maxItems = me.itemsInGroup();
		data.iconSz = me.iconSize;
		data.baseURL = NetProfile.baseURL;
		data.staticURL = NetProfile.staticURL;
		data.fname = Ext.String.htmlEncode(data.fname);

		qtip_cont.push(Ext.String.htmlEncode(data.descr ? data.descr : data.fname));
		if(data.size && me.getFileSize)
			qtip_cont.push(Ext.String.format(me.sizeText, me.getFileSize(data.size)));
		if(data.mime)
			qtip_cont.push(Ext.String.format(me.mimeTypeText, Ext.String.htmlEncode(data.mime.split(';')[0])));
		if(qtip_cont.length)
			data.qtip = qtip_cont.join('<br />');
		if(data.mime && me.getMIME)
			data.mime_img = me.getMIME(data.mime);

		return data;
	}
});

