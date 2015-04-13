/**
 * @class NetProfile.view.FileDownload
 * @extends Ext.Component
 */
Ext.define('NetProfile.view.FileDownload', {
	extend: 'Ext.Component',
	requires: [
		'Ext.form.Panel'
	],
	alias: 'widget.filedownload',
	autoEl: {
		tag: 'iframe',
		cls: Ext.baseCSSPrefix + 'hidden-display',
		name: 'npws_filedl_frame',
		src: Ext.SSL_SECURE_URL
	},
	id: 'npws_filedl',
	hidden: true,
	stateful: false,

	initComponent: function()
	{
		this.form = null;
		this.callParent(arguments);
	},
	getForm: function()
	{
		var me = this;

		if(!me.form)
			me.form = Ext.create('Ext.form.Panel', {
				hidden: true,
				stateful: false,
				standardSubmit: true
			});
		return me.form;
	},
	load: function(params)
	{
		var el = this.getEl(),
			url = params.url;

		if(!el)
			return false;
		if(params.params)
			url += ('?' + Ext.Object.toQueryString(config.params));
		el.dom.contentWindow.location.href = url;
		return true;
	},
	loadExport: function(moddef, model, fmt, par)
	{
		var me = this,
			uri = NetProfile.baseURL + '/core/file/export/' + moddef + '/' + model,
			form = me.getForm(),
			csrf = null,
			headers = Ext.Ajax.getDefaultHeaders();

		if(!par)
			par = {};
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
			clientValidation: false,
			params: par
		});
	},
	loadFileById: function(file_id)
	{
		var me = this,
			store = NetProfile.StoreManager.getStore(
				'core', 'File',
				null, true
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
			scope: me
		});
		return true;
	}
});

