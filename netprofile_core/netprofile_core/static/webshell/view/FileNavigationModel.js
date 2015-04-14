Ext.define('NetProfile.view.FileNavigationModel', {
	extend: 'Ext.view.NavigationModel',
	alias: 'view.navigation.file',

	onKeyUp: function(ev)
	{
		var me = this,
			view = me.view,
			useColumns = view.useColumns,
			perGroup = view.itemsInGroup(),
			curIdx = me.recordIndex,
			newIdx;

		if(useColumns)
		{
			newIdx = curIdx - 1;
			if(newIdx < 0)
				newIdx = 0;
		}
		else
		{
			newIdx = curIdx - perGroup;
			if(newIdx < 0)
				newIdx = curIdx;
		}
		me.setPosition(newIdx, ev);
	},
	onKeyDown: function(ev)
	{
		var me = this,
			view = me.view,
			useColumns = view.useColumns,
			perGroup = view.itemsInGroup(),
			lastIdx = view.all.getCount() - 1,
			curIdx = me.recordIndex,
			newIdx;

		if(useColumns)
		{
			newIdx = curIdx + 1;
			if(newIdx > lastIdx)
				newIdx = lastIdx;
		}
		else
		{
			newIdx = curIdx + perGroup;
			if(newIdx > lastIdx)
				newIdx = curIdx;
		}
		me.setPosition(newIdx, ev);
	},
	onKeyLeft: function(ev)
	{
		var me = this,
			view = me.view,
			useColumns = view.useColumns,
			perGroup = view.itemsInGroup(),
			curIdx = me.recordIndex,
			newIdx;

		if(useColumns)
		{
			newIdx = curIdx - perGroup;
			if(newIdx < 0)
				newIdx = curIdx;
		}
		else
		{
			newIdx = curIdx - 1;
			if(newIdx < 0)
				newIdx = 0;
		}
		me.setPosition(newIdx, ev);
	},
	onKeyRight: function(ev)
	{
		var me = this,
			view = me.view,
			useColumns = view.useColumns,
			perGroup = view.itemsInGroup(),
			lastIdx = view.all.getCount() - 1,
			curIdx = me.recordIndex,
			newIdx;

		if(useColumns)
		{
			newIdx = curIdx + perGroup;
			if(newIdx > lastIdx)
				newIdx = curIdx;
		}
		else
		{
			newIdx = curIdx + 1;
			if(newIdx > lastIdx)
				newIdx = lastIdx;
		}
		me.setPosition(newIdx, ev);
	},
	onKeyEnter: function(ev)
	{
		ev.stopEvent();
		ev.view.fireEvent('itemdblclick', ev.view, ev.record, ev.item, ev.recordIndex, ev);
	}
});

