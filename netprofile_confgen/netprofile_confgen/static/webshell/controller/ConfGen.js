/**
 * @class NetProfile.confgen.controller.ConfGen
 * @extends Ext.app.Controller
 */
Ext.define('NetProfile.confgen.controller.ConfGen', {
	extend: 'Ext.app.Controller',

	init: function()
	{
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
					console.log('MSG', msg);

					if(store)
					{
						rec = Ext.create('NetProfile.model.ConsoleMessage');
						rec.set('ts', new Date());
						rec.set('from', NetProfile.currentUser);
						rec.set('bodytype', 'task_request');
						rec.set('data', 'GENTASK');
						store.add(rec);
					}
					NetProfile.rtSocket.send(Ext.JSON.encode(msg));
					NetProfile.showConsole();
				}
			}
		});
	}
});

