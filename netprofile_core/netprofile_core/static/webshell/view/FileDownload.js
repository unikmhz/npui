/**
 * @class NetProfile.view.FileDownload
 * @extends Ext.Component
 */
Ext.define('NetProfile.view.FileDownload', {
	extend: 'Ext.Component',
	alias: 'widget.filedownload',
	autoEl: {
		tag: 'iframe',
		cls: 'x-hidden-display',
		name: 'npws_filedl_frame',
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
			el.on('load', this._onIFrameLoad, this);
			this.funcInstalled = true;
		}
		el.dom.src = url;
		return true;
	},
	loadExport: function(moddef, model, fmt, par)
	{
		var uri = NetProfile.baseURL + '/core/file/export/' + moddef + '/' + model,
			csrf = null,
			form, headers;

		if(!par)
			par = {};
		headers = Ext.Ajax.getDefaultHeaders();
		form = Ext.create('Ext.form.Panel', {
			hidden: true,
			stateful: false,
			standardSubmit: true
		});
		par = {
			'format' : fmt,
			'params' : Ext.JSON.encode(par)
		};
		if('X-CSRFToken' in headers)
			par['csrf'] = headers['X-CSRFToken'];
		form.getForm().submit({
			url: uri,
			method: 'POST',
			target: 'npws_filedl_frame',
			params: par
		});
		form.destroy();
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
			params: { __ffilter: [{
				property: 'fileid',
				operator: 'eq',
				value:    file_id
			}]},
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

