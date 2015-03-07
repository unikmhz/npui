## -*- coding: utf-8 -*-
<%!

from netprofile.tpl.filters import jsone

%>\
<%namespace name="np" file="netprofile_core:templates/np.mak" />\
Ext.Loader.setConfig({enabled: true});

Ext.Loader.setPath({
	'NetProfile'           : 'static/core/webshell',
% for module in modules:
	'NetProfile.${module}' : 'static/${module}/webshell',
% endfor
	'Ext.ux'               : 'static/core/webshell/ux'
});

Ext.require([
	'Ext.data.*',
	'Ext.direct.*',
	'Ext.form.field.Field',
	'Ext.tip.*',
	'Ext.state.*',
	'Ext.util.Cookies',
	'Ext.Ajax',
% for i_ajs in res_ajs:
	'${i_ajs}',
% endfor
	'NetProfile.model.Basic',
	'NetProfile.view.CapabilityGrid',
	'Ext.ux.form.MultiField',
	'NetProfile.view.Calendar'
], function()
{
	NetProfile.currentLocale = '${cur_loc}';
	NetProfile.currentUser = '${req.user.login}';
	NetProfile.currentUserId = ${req.user.id};
	NetProfile.currentSession = '${str(req.np_session)}';
	NetProfile.userSettings = ${req.user.client_settings(req) | n,jsone};
	NetProfile.userCapabilities = ${req.user.flat_privileges | n,jsone};
	NetProfile.userACLs = ${req.user.client_acls(req) | n,jsone};
	NetProfile.rootFolder = ${req.user.get_root_folder() | n,jsone};
	NetProfile.baseURL = '${req.host_url}';
	NetProfile.staticURL = '${req.host_url}';
	NetProfile.rtURL = '//${rt_host}:${rt_port}';
	NetProfile.rtSocket = null;
	NetProfile.rtSocketReady = false;
	NetProfile.rtActiveUIDs = null;
	NetProfile.rtMessageRenderers = {
		file: function(val, meta, rec)
		{
			var fname = Ext.String.htmlEncode(val.fname),
				surl = NetProfile.staticURL;

			return '<a class="np-file-wrap" href="#" onclick="Ext.getCmp(\'npws_filedl\').loadFileById(' + Ext.String.htmlEncode(val.id) + '); return false;"><img class="np-file-icon" src="' + surl + '/static/core/img/mime/16/' + Ext.String.htmlEncode(val.mime) + '.png" title="' + fname + '" onerror=\'this.onerror = null; this.src="' + surl + '/static/core/img/mime/16/default.png"\' /><span title="' + fname + '">' + fname + '</span></a>';
		},
		task_result: function(val, meta, rec)
		{
			if(Ext.isArray(val))
				val = Ext.Array.map(val, Ext.String.htmlEncode).join('<br />');
			else
				val = Ext.String.htmlEncode(val);
			return Ext.String.format('<img class="np-console-icon" src="{0}/static/core/img/info.png" /><span class="np-console-message">{1}</span>',
				NetProfile.staticURL,
				val
			);
		},
		task_error: function(val, meta, rec)
		{
			return Ext.String.format('<img class="np-console-icon" src="{0}/static/core/img/cancel.png" /><span class="np-console-message"><strong>Error {1}</strong>: {2}</span>',
				NetProfile.staticURL,
				Ext.String.htmlEncode(val[0]),
				Ext.String.htmlEncode(val[1])
			);
		}
	};
	Ext.direct.Manager.addProvider(NetProfile.api.Descriptor);
	Ext.Ajax.defaultHeaders = Ext.apply(Ext.Ajax.defaultHeaders || {}, {
		'X-CSRFToken': '${req.get_csrf()}'
	});
	NetProfile.msg = function()
	{
		var msgCt;

		function createBox(t, s, cls)
		{
			return '<div class="msg ' + cls + '"><h3>' + t + '</h3><p>' + s + '</p></div>';
		}

		function getMsg(cls, title, args)
		{
			if(!msgCt)
				msgCt = Ext.DomHelper.insertFirst(document.body, { id: 'msg-div' }, true);
			var s = Ext.String.format.apply(String, args);
			var m = Ext.DomHelper.append(msgCt, createBox(title, s, cls), true);
			m.hide();
			m.slideIn('t').ghost('t', { delay: 1250, remove: true });
		}

		return {
			notify: function(title, fmt)
			{
				return getMsg('', title, Array.prototype.slice.call(arguments, 1));
			},
			warn: function(title, fmt)
			{
				return getMsg('warning', title, Array.prototype.slice.call(arguments, 1));
			},
			err: function(title, fmt)
			{
				return getMsg('error', title, Array.prototype.slice.call(arguments, 1));
			},
			init: function()
			{
				if(!msgCt)
					msgCt = Ext.DomHelper.insertFirst(document.body, { id: 'msg-div' }, true);
			}
		};
	}();

	NetProfile.cap = function(capname)
	{
		if(capname in NetProfile.userCapabilities)
			return NetProfile.userCapabilities[capname];
		return false;
	};
	NetProfile.acl = function(capname, resid)
	{
		if(!(capname in NetProfile.userACLs))
			return NetProfile.cap(capname);
		if(!(resid in NetProfile.userACLs[capname]))
			return NetProfile.cap(capname);
		return NetProfile.userACLs[capname][resid];
	};

	NetProfile.showConsole = function()
	{
		var pbar = Ext.getCmp('npws_propbar'),
			store = NetProfile.StoreManager.getConsoleStore('system', 'log'),
			str_id = 'cons:system:log',
			tab;

		tab = pbar.addConsoleTab(str_id, {
			xtype: 'grid',
			title: '${_('System Console')}',
			iconCls: 'ico-console',
			store: store,
			viewConfig: {
				preserveScrollOnRefresh: true
			},
			columns: [{
				text: 'Date',
				dataIndex: 'ts',
				width: 120,
				xtype: 'datecolumn',
				format: Ext.util.Format.dateFormat + ' H:i:s'
			}, {
				text: 'Message',
				dataIndex: 'data',
				flex: 1,
				sortable: false,
				filterable: false,
				menuDisabled: true,
				editor: null,
				renderer: function(val, meta, rec)
				{
					var ret = '',
						from = rec.get('from'),
						btype = rec.get('bodytype'),
						cssPrefix = Ext.baseCSSPrefix,
						cls = [cssPrefix + 'cons-data'];

					if(from)
						ret += '<strong>' + Ext.String.htmlEncode(from) + ':</strong> ';
					if(btype in NetProfile.rtMessageRenderers)
						ret += NetProfile.rtMessageRenderers[btype](val, meta, rec);
					else
						ret += Ext.String.htmlEncode(val);
					return '<div class="' + cls.join(' ') + '">' + ret + '</div>';
				}
			}]
		}, function(val)
		{
			// FIXME: implement system console commands?
		});
		tab.mon(store, 'add', function(st, recs, idx)
		{
			var view = tab.getView(),
				node = view.getNode(recs[0]);

			node.scrollIntoView();
		});
		tab.down('toolbar')
		pbar.show();
	};

	Ext.define('Ext.data.ConnectionNPOver', {
		override: 'Ext.data.Connection',
		setOptions: function(opt, scope)
		{
			res = this.callParent(arguments);
			if(opt.rawData && (typeof(FormData) !== 'undefined') && (opt.rawData instanceof FormData))
				res.data = opt.rawData;
			return res;
		},
		setupHeaders: function(xhr, opt, data, params)
		{
			if(opt.rawData && (typeof(FormData) !== 'undefined') && (opt.rawData instanceof FormData))
				return {};
			res = this.callParent(arguments);
			return res;
		}
	});
	Ext.define('Ext.form.field.BaseErrors', {
		override: 'Ext.form.field.Base',
		getErrors: function(value)
		{
			var errs, i;

			errs = this.callParent(arguments);
			if(this.asyncErrors && this.asyncErrors.length)
				for(i in this.asyncErrors)
				{
					Ext.Array.push(errs, this.asyncErrors[i]);
				}
			return errs;
		}
	});

	Ext.data.Types.IPV4 = {
		type: 'ipv4',
		convert: function(value, record)
		{
			if((value === null) || (value === undefined) || (value === ''))
				return null;
			if(Ext.isObject(value))
			{
				if(value instanceof ipaddr.IPv4)
					return value;
				throw "Supplied with an unknown object type";
			}
			return ipaddr.IPv4.parse(value);
		},
		serialize: function(value, record)
		{
			if((value === null) || (value === undefined) || (value === ''))
				return null;
			if(Ext.isObject(value) && (value instanceof ipaddr.IPv4))
				return value.toInteger();
			return value;
		},
		sortType: function(t)
		{
			return t.toInteger();
		}
	};
	Ext.data.Types.IPV6 = {
		type: 'ipv6',
		convert: function(value, record)
		{
			if((value === null) || (value === undefined) || (value === ''))
				return null;
			if(Ext.isObject(value))
			{
				if(value instanceof ipaddr.IPv6)
					return value;
				throw "Supplied with an unknown object type";
			}
			if(Ext.isArray(value) && (value.length == 16))
			{
				var newval = [], i;

				for(i = 0; i < value.length; i += 2)
				{
					newval.push((value[i] << 8) + value[i + 1]);
				}
				return new ipaddr.IPv6(newval);
			}
			return ipaddr.IPv6.parse(value);
		},
		serialize: function(value, record)
		{
			if((value === null) || (value === undefined) || (value === ''))
				return null;
			if(Ext.isObject(value) && (value instanceof ipaddr.IPv6))
				return value.toByteArray();
			return value;
		},
		sortType: function(t)
		{
			return t.toByteArray();
		}
	};

	Ext.apply(Ext.data.validations, {
		rangeMessage: 'is out of range',
		range: function(config, value)
		{
			if(value === undefined || value === null)
				return false;

			if(typeof(value) !== 'number')
				return false;

			var min = config.min,
				max = config.max;

			if((typeof(min) === 'number') && (value < min))
				return false;
			if((typeof(max) === 'number') && (value > max))
				return false;

			return true;
		}
	});

	Ext.define('NetProfile.model.Language', {
		extend: 'Ext.data.Model',
		fields: [
			{ name: 'code', type: 'string' },
			{ name: 'name', type: 'string' }
		]
	});
	Ext.define('NetProfile.store.Language', {
		extend: 'Ext.data.ArrayStore',
		requires: 'NetProfile.model.Language',
		model: 'NetProfile.model.Language',
		data: ${[ (str(l), '%s [%s]' % (l.english_name, l.display_name)) for l in req.locales.values() ] | n,jsone},
		storeId: 'npstore_lang'
	});

	Ext.define('NetProfile.model.ConsoleMessage', {
		extend: 'NetProfile.model.Basic',
		fields: [
			{ name: 'id',   type: 'auto' },
			{ name: 'ts',   type: 'date', dateFormat: 'c' },
			{ name: 'from', type: 'string' },
			{ name: 'bodytype', type: 'string', defaultValue: 'text' },
			{ name: 'data', type: 'auto' }
		],
		idProperty: 'id'
	});

	Ext.define('NetProfile.model.Menu', {
		extend: 'Ext.data.Model',
		fields: [
			{ name: 'name', type: 'string' },
			{ name: 'title', type: 'string' },
			{ name: 'order', type: 'int' },
			{ name: 'direct', type: 'string' },
			{ name: 'url', type: 'string' },
			{ name: 'options', type: 'auto' }
		]
	});
	Ext.define('NetProfile.model.MenuItem', {
		extend: 'Ext.data.Model',
		fields: [
			{ name: 'id', type: 'string' },
			{ name: 'text', type: 'string' },
			{ name: 'order', type: 'int' },
			{ name: 'leaf', type: 'boolean' },
			{ name: 'iconCls', type: 'string' },
			{ name: 'xview', type: 'string' },
			{ name: 'xhandler', type: 'string' }
		]
	});
	Ext.define('NetProfile.store.Menu', {
		extend: 'Ext.data.Store',
		requires: 'NetProfile.model.Menu',
		model: 'NetProfile.model.Menu',
		data: ${modules.get_menu_data(req) | n,jsone},
		storeId: 'npstore_menu'
	});
% for menu in modules.get_menu_data(req):
<%np:limit cap="${menu.perm}">\
% if len(menu.extra_fields) > 0:
	Ext.define('NetProfile.model.customMenu.${menu.name}', {
		extend: 'Ext.data.Model',
		fields: [
			{ name: 'id', type: 'string' },
			{ name: 'text', type: 'string' },
			{ name: 'order', type: 'int' },
			{ name: 'leaf', type: 'boolean' },
			{ name: 'iconCls', type: 'string' },
% for xf in menu.extra_fields:
			${xf | n,jsone},
% endfor
			{ name: 'xview', type: 'string' },
			{ name: 'xhandler', type: 'string' }
		]
	});
% endif
	Ext.define('NetProfile.store.menu.${menu.name}', {
		extend: 'Ext.data.TreeStore',
		requires: 'NetProfile.model.MenuItem',
% if len(menu.extra_fields) > 0:
		model: 'NetProfile.model.customMenu.${menu.name}',
% else:
		model: 'NetProfile.model.MenuItem',
% endif
% if menu.direct:
		defaultRootProperty: 'records',
		proxy: {
			type: 'direct',
			api: {
				create:  NetProfile.api.MenuTree.${menu.direct}_create || Ext.emptyFn,
				read:    NetProfile.api.MenuTree.${menu.direct}_read || Ext.emptyFn,
				update:  NetProfile.api.MenuTree.${menu.direct}_update || Ext.emptyFn,
				destroy: NetProfile.api.MenuTree.${menu.direct}_delete || Ext.emptyFn
			},
			reader: {
				type: 'json',
				root: 'records',
				messageProperty: 'message',
				successProperty: 'success',
				totalProperty: 'total'
			},
			writer: {
				type: 'json',
				root: 'records',
				writeAllFields: true,
				allowSingle: false
			}
		},
		root: {
			expanded: true
		},
		autoLoad: false,
		autoSync: false,
% else:
		root: {
			expanded: true,
			id: 'top',
			children: ${modules.get_menu_tree(req, menu.name) | n,jsone}
		},
% endif
		storeId: 'npstore_menu_${menu.name}'
	});\
</%np:limit>\
% endfor

	Ext.require('NetProfile.view.Viewport');
% for module in modules:
% for model in modules[module]:
<% mod = modules[module][model] %>
	Ext.define('NetProfile.proxy.${module}.${model}', {
		extend: 'Ext.data.proxy.Direct',
		alias: 'proxy.${module}_${model}',
		api: {
			create:  NetProfile.api.${model}['create'],
			read:    NetProfile.api.${model}['read'],
			update:  NetProfile.api.${model}['update'],
			destroy: NetProfile.api.${model}['delete']
		},
		simpleSortMode: false,
		filterParam: '__filter',
		sortParam: '__sort',
		startParam: '__start',
		limitParam: '__limit',
		pageParam: '__page',
		groupParam: '__group',
		reader: {
			type: 'json',
			idProperty: '${mod.pk}',
			messageProperty: 'message',
			root: 'records',
			successProperty: 'success',
			totalProperty: 'total'
		},
		writer: {
			type: 'json',
			root: 'records',
			writeAllFields: false,
			allowSingle: false
		}
	});
	Ext.define('NetProfile.model.${module}.${model}', {
		extend: 'NetProfile.model.Basic',
		fields: ${mod.get_reader_cfg() | n,jsone},
		associations: ${mod.get_related_cfg() | n,jsone},
		idProperty: '${mod.pk}',
		clientIdProperty: '_clid',
		proxy: {
			type: '${module}_${model}'
		}
	});
	Ext.define('NetProfile.store.${module}.${model}', {
		alias: 'store.${module}_${model}',
		extend: 'Ext.data.Store',
		requires: 'NetProfile.model.${module}.${model}',
		model: 'NetProfile.model.${module}.${model}',
		sorters: ${mod.default_sort | n,jsone},
		pageSize: NetProfile.userSettings.datagrid_perpage,
		remoteFilter: true,
		remoteGroup: true,
		remoteSort: true,
		storeId: 'npstore_${module}_${model}',
		autoLoad: true,
		autoSync: true
	});
	Ext.define('NetProfile.view.grid.${module}.${model}', {
		extend: 'NetProfile.view.ModelGrid',
		alias: 'widget.grid_${module}_${model}',
		columns: ${mod.get_column_cfg(req) | n,jsone},
		apiModule: '${module}',
		apiClass: '${model}',
		stateId: 'npgrid_${module}_${model}',
		stateful: true,
		simpleSearch: ${'true' if mod.easy_search else 'false'},
		extraSearch: ${mod.get_extra_search_cfg(req) | n,jsone},
		extraActions: ${mod.extra_actions | n,jsone},
		detailPane: ${mod.get_detail_pane(req) | n,jsone},
% if mod.create_wizard:
		canCreate: <%np:jscap code="${mod.cap_create}" />,
% else:
		canCreate: false,
% endif
		canEdit: <%np:jscap code="${mod.cap_edit}" />,
		canDelete: <%np:jscap code="${mod.cap_delete}" />
	});
% endfor
% endfor


Ext.application({
	name: 'NetProfile',
	appFolder: 'static/core/webshell',
	autoCreateViewport: false,

	models: [],
	stores: [],
	controllers: [
		'NetProfile.controller.DataStores',
		'NetProfile.controller.Users',
		'NetProfile.controller.FileAttachments',
% for cont in res_ctl:
		'${cont}',
% endfor
		'NetProfile.controller.FileFolders'
	],

	launch: function()
	{
		var state_prov = null,
			state_loaded = false,
			rt_sock = null;

		Ext.onReady(NetProfile.msg.init, NetProfile.msg);
		if('localStorage' in window && window['localStorage'] !== null)
		{
			state_prov = new Ext.state.LocalStorageProvider({
				prefix: 'nps_'
			});
		}
		else
		{
			state_prov = new Ext.state.CookieProvider({
				prefix: 'nps_'
			});
		}

		Ext.state.Manager.setProvider(state_prov);
		state_loaded = state_prov.get('loaded');

		var npp = Ext.direct.Manager.getProvider('netprofile-provider');
		npp.on('exception', function(p, e)
		{
			if(e && e.message)
			{
% if req.debug_enabled:
				Ext.log.error(e.message);
% endif
				NetProfile.msg.err('${_('Error')}', '{0}', e.message);
			}
		});
		npp.on('data', function(p, e)
		{
			if(e.result && !e.result.success)
			{
				if(e.result.message)
				{
% if req.debug_enabled:
					Ext.log.warn(e.result.message);
					if(e.result.stacktrace)
						Ext.log.info(e.result.stacktrace);
% endif
					NetProfile.msg.warn('${_('Warning')}', '{0}', e.result.message);
				}
			}
		});

		if(NetProfile.rtURL)
		{
			rt_sock = SockJS(NetProfile.rtURL + '/sock');
			rt_sock.onopen = function()
			{
% if req.debug_enabled:
				Ext.log.info('SockJS connected');
% endif
				var msg = {
					type:    'auth',
					user:    NetProfile.currentUser,
					uid:     NetProfile.currentUserId,
					session: NetProfile.currentSession
				};
				rt_sock.send(Ext.JSON.encode(msg));
			};
			rt_sock.onmessage = function(ev)
			{
				ev.data = Ext.JSON.decode(ev.data);
% if req.debug_enabled:
				Ext.log.info({ dump: ev }, 'SockJS event received');
% endif
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
			NetProfile.rtSocket = rt_sock;
		}

		if(state_loaded !== 'OK')
		{
			NetProfile.api.DataCache.load_ls(function(data, res)
			{
				if(data && data.state && data.success)
				{
					Ext.Object.each(data.state, function(k, v)
					{
						state_prov.set(k, v);
					});
				}
				state_prov.set('loaded', 'OK');
				Ext.create('NetProfile.view.Viewport', {});
			});
		}
		else
			Ext.create('NetProfile.view.Viewport', {});
	}
});

});

