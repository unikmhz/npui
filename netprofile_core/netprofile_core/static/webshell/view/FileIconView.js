/**
 * @class NetProfile.view.FileIconView
 * @extends Ext.view.View
 */
Ext.define('NetProfile.view.FileIconView', {
	extend: 'Ext.view.View',
	alias: 'widget.fileiconview',
	requires: [
		'Ext.ux.view.DragSelector',
		'Ext.ux.view.LabelEditor'
	],

	emptyText: 'Folder is empty',

	itemSelector: 'div.np-file-wrap',
	overItemCls: 'x-file-item-over',
	multiSelect: true,
	trackOver: true,

	tpl: [
		'<tpl for=".">',
			'<div class="np-file-wrap" id="file_{fileid}">',
				'<div class="np-file-icon"><img src="/static/core/img/mime/{mime_img}.png" title="{fname}" /></div>',
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
		this.callParent(arguments);
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

