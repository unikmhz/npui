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
			url += ('?' + Ext.Object.toQueryString(config.params));

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
	},
	loadFileById: function(file_id)
	{
		var store = NetProfile.StoreManager.getStore(
			'core', 'File',
			null, true, true
		);

		if(!store)
			return false;
		store.load({
			params: { __ffilter: { fileid: { eq: file_id } } },
			callback: function(recs, op, success)
			{
				if(!success || !recs || (recs.length <= 0))
					return;
				this.load({
					url: Ext.String.format(
						'{0}/core/file/dl/{1}/{2}',
						NetProfile.baseURL,
						recs[0].getId(), recs[0].get('fname')
					)
				});
			},
			scope: this
		});
		return true;
	}
});

