Ext.define('Ext.ux.window.CenterWindow', {
	extend: 'Ext.window.Window',
	alias: 'widget.centerwindow',
	requires: [
	],
	layout: 'fit',
	minWidth: 500,
	constrain: true,
	constrainHeader: true,
	maximizable: true,
	listeners: {
		afterlayout: function(win)
		{
			var pos, sz, bodysz;

			if(!win.maximized)
			{
				pos = win.getPosition();
				sz = win.getSize();
				bodysz = Ext.getBody().getSize();
				if(pos[1] < 0)
					win.setPosition(pos[0], 10);
				if((sz.height + 20) > bodysz.height)
					win.setSize(sz.width + 16, bodysz.height - 20);
				win.center();
			}
		}
	}
});

