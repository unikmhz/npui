/**
 * @class NetProfile.view.FileIconView
 * @extends Ext.view.View
 */
Ext.define('NetProfile.view.FileIconView', {
	extend: 'Ext.view.View',
	alias: 'widget.fileiconview',
	requires: [
		'Ext.util.KeyNav',
		'Ext.ux.view.DragSelector',
		'Ext.ux.view.LabelEditor',
		'Ext.ux.view.Draggable'
	],
	mixins: {
		draggable: 'Ext.ux.view.Draggable'
	},

	cls: 'np-file-iview',
	emptyText: 'Folder is empty',

	itemSelector: 'div.np-file-wrap',
	overItemCls: 'x-file-item-over',
	multiSelect: true,
	trackOver: true,
	autoScroll: true,

	tpl: [
		'<tpl for=".">',
			'<div class="np-file-wrap" id="file_{fileid}">',
				'<div class="np-file-icon"><img src="/static/core/img/mime/48/{mime_img}.png" title="{fname}" onerror=\'this.onerror = null; this.src="/static/core/img/mime/48/default.png"\' /></div>',
				'<span class="x-editable" title="{fname}">{fname}</span>',
			'</div>',
		'</tpl>',
		'<div class="x-clear"></div>'
	],

	initComponent: function()
	{
		this.plugins = [
			Ext.create('Ext.ux.view.DragSelector', {}),
			Ext.create('Ext.ux.view.LabelEditor', { dataIndex: 'fname' })
		];
		this.emptyText = '<div class="x-view-empty">' + this.emptyText + '</div>';
		this.mixins.draggable.init(this, {
			ddConfig: {
				ddGroup: 'ddFile'
			},
			ghostTpl: [
				'<tpl for=".">',
					'<div>{fname}</div>',
				'</tpl>'
			]
		});
		this.nav = null;
		this.callParent(arguments);

		this.on({
			afterrender: this.onAfterRender
		});
	},
	onDragTest: function(ev)
	{
		if(!ev.dataTransfer || !ev.dataTransfer.types)
			return true;
		var bad_upload = true,
			drag_types = [
				'application/x-moz-file',
//				'text/x-moz-url',
//				'text/plain',
				'Files'
			];
		Ext.Array.forEach(drag_types, function(dt)
		{
			if(ev.dataTransfer.types.contains)
			{
				if(ev.dataTransfer.types.contains(dt))
					bad_upload = false;
			}
			else
			{
				if(Ext.Array.contains(ev.dataTransfer.types, dt))
					bad_upload = false;
			}
		});
		return bad_upload;
	},
	onDrop: function(e)
	{
		var ev = e.browserEvent;
		if(ev.dataTransfer && ev.dataTransfer.files)
		{
			e.stopEvent();
			this.fireEvent('filesdropped', this, ev.dataTransfer.files, e);
			return false;
		}
		return true;
	},
	onAfterRender: function(view)
	{
		var el = this.getEl();

		el.on({
			drop: this.onDrop,
			scope: this
		});
		el.dom.ondragenter = Ext.Function.bind(this.onDragTest, this);
		el.dom.ondragover = Ext.Function.bind(this.onDragTest, this);
	},
	prepareData: function(data)
	{
		var mime = data.mime;

		if(mime)
		{
			mime = mime.split(';')[0];
			mime = mime.split(' ')[0];
			mime = mime.replace('/', '_').replace('-', '_');
			data.mime_img = mime;
		}
		else
			data.mime_img = 'default';
		return data;
	}
});

