/**
 * @class NetProfile.view.FileDownload
 * @extends Ext.Component
 */
Ext.define('NetProfile.view.FileDownload', {
	extend: 'Ext.Component',
	alias: 'widget.filedownload',
	autoEl: {
		tag: 'iframe',
		cls: 'x-hidden',
		src: Ext.SSL_SECURE_URL
	},
	id: 'npws_filedl',
	hidden: true,
	stateful: false,

	_onIFrameLoad: function(ev, tgt, opts)
	{
	},
	initComponent: function()
	{
		this.funcInstalled = false;
		this.callParent(arguments);
	},
	load: function(params)
	{
		var el, url;

		url = params.url;
		if(params.params)
			url += ('?' + Ext.urlEncode(config.params));

		el = this.getEl();
		if(!el)
			return false;
		if(!this.funcInstalled)
		{
			el.on('load', this._onIFrameLoad);
			this.funcInstalled = true;
		}
		el.dom.src = url;
		return true;
	}
});

