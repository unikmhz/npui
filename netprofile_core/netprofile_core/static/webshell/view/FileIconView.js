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

	getMIME: null,
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
				'<div class="np-file-icon"><img src="{staticURL}/static/core/img/mime/48/{mime_img}.png" title="{fname}" onerror=\'this.onerror = null; this.src="{staticURL}/static/core/img/mime/48/default.png"\' /></div>',
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
	},
	prepareData: function(data)
	{
		data.baseURL = NetProfile.baseURL;
		data.staticURL = NetProfile.staticURL;
		if(data.mime && this.getMIME)
			data.mime_img = this.getMIME(data.mime);

		return data;
	}
});

