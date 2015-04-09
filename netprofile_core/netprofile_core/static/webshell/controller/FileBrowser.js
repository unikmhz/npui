Ext.define('NetProfile.controller.FileBrowser', {
	extend: 'Ext.util.Observable',
	requires: [
		'NetProfile.store.core.FileFolder',
		'NetProfile.panel.FileBrowser'
	],
	statics: {
		folderStore: null
	},

	process: function(xid)
	{
		var fb, mainbar, loadparam, st;

		st = this.statics();
		if(!st.folderStore)
			st.folderStore = Ext.create('NetProfile.store.core.FileFolder', {
				autoDestroy: false,
				autoLoad: false,
				buffered: false,
				pageSize: -1
			});

		if(!xid)
			throw 'Missing folder ID';
		if(xid === 'root')
			xid = null;
		else
		{
			xid = parseInt(xid);
			if(xid <= 0)
				throw 'Invalid folder ID';
		}

		mainbar = Ext.getCmp('npws_mainbar');
		if(!mainbar)
			throw 'Unable to locate interface';
		fb = mainbar.mainWidget;
		if(!fb || !(fb instanceof NetProfile.panel.FileBrowser))
		{
			fb = Ext.create('NetProfile.panel.FileBrowser', {
				region: 'center'
			});
			mainbar.replaceWith(fb);
		}

		if(xid === null)
		{
			fb.setFolder(xid);
			return true;
		}
		st.folderStore.load({
			params: {
				__ffilter: [{
					property: 'ffid',
					operator: 'eq',
					value:    xid
				}]
			},
			callback: function(recs, op, success)
			{
				if(success && (recs.length === 1))
					fb.setFolder(recs[0]);
			},
			scope: this,
			synchronous: false
		});
		return true;
	}
});

