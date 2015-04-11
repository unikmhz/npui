Ext.define('NetProfile.data.MenuTreeStore', {
	extend: 'Ext.data.TreeStore',
	alias: 'store.menutree',

	findNodeByPath: function(path, callback)
	{
		var me = this,
			pathlen = path.length,
			node = null,
			head, nextnode, i;

		for(i = 0; i < pathlen; i++)
		{
			head = path[i];
			nextnode = me.getNodeById(head);
			if(!nextnode)
				break;
			node = nextnode;
		}
		if(!node)
			return false;
		else if(nextnode === node)
			return callback(node, me);
		else
			node.expand(false, function()
			{
				me.findNodeByPath(path, callback);
			});

		return true;
	}
});

