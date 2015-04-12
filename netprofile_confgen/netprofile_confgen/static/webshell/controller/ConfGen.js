/**
 * @class NetProfile.confgen.controller.ConfGen
 * @extends Ext.app.Controller
 */
Ext.define('NetProfile.confgen.controller.ConfGen', {
	extend: 'Ext.app.Controller',

	serverMgmtText: 'Server Management',
	reconfigureAllText: 'Reconfigure All Servers',
	confGenAllText: 'Sent configuration generation command for all servers.',
	confGenServerText: 'Sent configuration generation command for server: {0} (ID:{1}).',

	init: function()
	{
		var me = this;

		if(NetProfile.cap('SRV_CONFGEN'))
		this.control({
			'grid_confgen_Server' : {
				action_srvgen: function(grid, item, ev, record)
				{
					var store = NetProfile.StoreManager.getConsoleStore('system', 'log'),
						rec;
					if(!NetProfile.rtSocket)
						return false; // FIXME: Print some error to console?
					var msg = {
						'type'   : 'task',
						'tname'  : 'netprofile_confgen.tasks.task_generate',
						'kwargs' : { 'srv_ids' : [record.getId()] }
					};

					if(store)
					{
						rec = Ext.create('NetProfile.model.ConsoleMessage');
						rec.set('ts', new Date());
						rec.set('from', NetProfile.currentUser);
						rec.set('bodytype', 'task_request');
						rec.set('data', Ext.String.format(me.confGenServerText,
							record.get('__str__'),
							record.getId()
						));
						store.add(rec);
					}
					NetProfile.rtSocket.send(Ext.JSON.encode(msg));
					NetProfile.showConsole();
				}
			},
			'maintoolbar' : {
				beforerender: function(tb, opts)
				{
					var menu, item;

					menu = tb.getComponent('sub_tools');
					item = Ext.create('Ext.menu.Item', {
						showSeparator: false,
						iconCls: 'ico-mod-server',
						text: me.serverMgmtText,
						menu: {
							xtype: 'menu',
							items: [{
								text: me.reconfigureAllText,
								iconCls: 'ico-redo',
								handler: function(el, ev)
								{
									var store = NetProfile.StoreManager.getConsoleStore('system', 'log'),
										rec;
									if(!NetProfile.rtSocket)
										return false; // FIXME: Print some error to console?
									var msg = {
										'type'   : 'task',
										'tname'  : 'netprofile_confgen.tasks.task_generate'
									};

									if(store)
									{
										rec = Ext.create('NetProfile.model.ConsoleMessage');
										rec.set('ts', new Date());
										rec.set('from', NetProfile.currentUser);
										rec.set('bodytype', 'task_request');
										rec.set('data', me.confGenAllText);
										store.add(rec);
									}
									NetProfile.rtSocket.send(Ext.JSON.encode(msg));
									NetProfile.showConsole();
								}
							}]
						}
					});
					menu.menu.add(item);
				}
			}
		});
	}
});

