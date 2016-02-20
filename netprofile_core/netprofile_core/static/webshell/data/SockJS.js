/**
 * @class NetProfile.data.SockJS
 */
Ext.define('NetProfile.data.SockJS', {
	mixins: ['Ext.mixin.Observable'],
	requires: [
		'Ext.JSON'
	],

	constructor: function(config)
	{
		var me = this,
			sock;

		me.mixins.observable.constructor.call(me, config);

		sock = SockJS(me.url);
		sock.onopen = function()
		{
			if(NetProfile.debugEnabled)
				Ext.log.info('SockJS connected');

			var msg = {
				type:    'auth',
				user:    NetProfile.currentUser,
				uid:     NetProfile.currentUserId,
				session: NetProfile.currentSession
			};
			sock.send(Ext.JSON.encode(msg));
		};
		sock.onmessage = function(ev)
		{
			ev.data = Ext.JSON.decode(ev.data);
			if(NetProfile.debugEnabled)
				Ext.log.info({ dump: ev }, 'SockJS event received');
			if(typeof(ev.data.type) !== 'string')
				return;

			switch(ev.data.type)
			{
				case 'user_enters':
				case 'user_leaves':
					var uid = ev.data.uid,
						obj = Ext.getCmp('npmenu_tree_users').getStore().getNodeById('user-' + uid);
					if(!obj)
						return;
					if(ev.data.type === 'user_enters')
						obj.set('iconCls', 'ico-status-online');
					else
						obj.set('iconCls', 'ico-status-offline');
					break;
				case 'user_list':
					var u, uid, obj;
					NetProfile.rtSocketReady = true;
					NetProfile.rtActiveUIDs = ev.data.users;
					for(u in ev.data.users)
					{
						uid = ev.data.users[u];
						obj = Ext.getCmp('npmenu_tree_users').getStore().getNodeById('user-' + uid);
						if(!obj)
							continue;
						obj.set('iconCls', 'ico-status-online');
					}
					break;
				case 'direct':
					var store = NetProfile.StoreManager.getConsoleStore(ev.data.msgtype, ev.data.fromid),
						rec;
					if(store)
					{
						rec = Ext.create('NetProfile.model.ConsoleMessage');
						rec.set('ts', new Date(ev.data.ts));
						if(ev.data.fromstr)
							rec.set('from', ev.data.fromstr);
						if(ev.data.bodytype)
							rec.set('bodytype', ev.data.bodytype);
						if(ev.data.msg)
							rec.set('data', ev.data.msg);
						store.add(rec);
					}
					break;
				case 'task_result':
					if(me.fireEvent('taskresult', me, sock, ev) === true)
						break;

					var store = NetProfile.StoreManager.getConsoleStore('system', 'log'),
						rec;
					if(store)
					{
						rec = Ext.create('NetProfile.model.ConsoleMessage');
						rec.set('ts', new Date(ev.data.ts));
						rec.set('bodytype', 'task_result');
						rec.set('data', ev.data.value);
						store.add(rec);
					}
					NetProfile.showConsole();
					break;
				case 'task_error':
					var store = NetProfile.StoreManager.getConsoleStore('system', 'log'),
						rec;
					if(store)
					{
						rec = Ext.create('NetProfile.model.ConsoleMessage');
						rec.set('ts', new Date(ev.data.ts));
						rec.set('bodytype', 'task_error');
						rec.set('data', [ev.data.errno, ev.data.value]);
						store.add(rec);
					}
					NetProfile.showConsole();
					break;
			}
		};
		me.sock = sock;
	},
	send: function(data)
	{
		return this.sock.send(data);
	}
});

