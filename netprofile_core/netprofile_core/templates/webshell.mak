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
	'Ext.tip.*',
	'Ext.state.*',
	'Ext.util.Cookies',
	'Ext.Ajax',
% for i_ajs in res_ajs:
	'${i_ajs}',
% endfor
	'NetProfile.model.Basic'
], function()
{
//	NetProfile.api.Descriptor.enableBuffer = 100;
	NetProfile.currentLocale = '${cur_loc}';
	NetProfile.userSettings = ${req.user.client_settings(req) | n,jsone};
	NetProfile.baseURL = '${req.host_url}';
	Ext.direct.Manager.addProvider(NetProfile.api.Descriptor);
	Ext.Ajax.defaultHeaders = Ext.apply(Ext.Ajax.defaultHeaders || {}, {'X-CSRFToken': '${req.session.get_csrf_token().decode('utf-8')}'});

	Ext.define('NetProfile.data.IPAddress', {
		MAX_IPV4: 0xffffffff,
		value: null,
		getValue: function()
		{
			return this.value;
		}
	});

	Ext.define('NetProfile.data.IPv4Address', {
		extend: 'NetProfile.data.IPAddress',
		constructor: function(val)
		{
			if((val !== undefined) && (val !== null))
				this.setValue(val);
		},
		setValue: function(val)
		{
			if(Ext.isNumeric(val))
				val = parseInt(val);
			else
				val = this.parseTextual(val);
			this.value = val;
			return this;
		},
		setOctets: function(oct)
		{
			oct = this.parseOctets(oct);
			this.value = oct;
			return this;
		},
		parseOctets: function(oct)
		{
			var ip, i, ioct;

			if(oct.length !== 4)
				throw 'Invalid IPv4 octets';
			ip = 0;
			for(i = 0; i < oct.length; i++)
			{
				ioct = parseInt(oct[i]);
				if(isNaN(ioct) || (ioct < 0) || (ioct > 255) ||
						((oct[i].length > 1) && (oct[i].slice(0, 1) == '0')))
					throw 'Invalid octet ' + (i + 1) + ' in IPv4 address';
				ip = (ip | ioct) >>> 0;
				if(i < 3)
					ip = (ip << 8) >>> 0;
			}
			return ip;
		},
		parseTextual: function(val)
		{
			if(!val.match(/^[0-9.]*$/))
				throw 'Invalid IPv4 address: ' + val;
			return this.parseOctets(val.split('.'));
		},
		toOctets: function()
		{
			var oct, v, i;

			oct = [0, 0, 0, 0];
			v = this.value;

			for(i = 3; i >= 0; i--)
			{
				oct[i] = String((v & 0xff));
				v = v >>> 8;
			}
			return oct;
		},
		toString: function()
		{
			return this.toOctets().join('.');
		}
	});

	Ext.define('NetProfile.data.IPv6Address', {
		extend: 'NetProfile.data.IPAddress',
	});

	Ext.data.Types.IPV4 = {
		type: 'ipv4',
		convert: function(value, record)
		{
			if(value === null)
				return null;
			if(Ext.isObject(value))
			{
				if(Ext.getClassName(value) === 'NetProfile.data.IPv4Address')
					return value;
				throw "Supplied with an unknown object type";
			}
			return new NetProfile.data.IPv4Address(value);
		},
		serialize: function(value, record)
		{
			if(value === null)
				return null;
			if(Ext.isObject(value) && (Ext.getClassName(value) === 'NetProfile.data.IPv4Address'))
				return value.value;
			return value;
		},
		sortType: function(t)
		{
			return t.value;
		}
	};
	Ext.data.Types.IPV6 = {
		type: 'ipv6',
		convert: function(value, record)
		{
			if(value === null)
				return null;
			return new NetProfile.data.IPv6Address(value);
		},
		sortType: function(t)
		{
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
		data: ${langs | n,jsone},
		storeId: 'npstore_lang'
	});

	Ext.define('NetProfile.model.Menu', {
		extend: 'Ext.data.Model',
		fields: [
			{ name: 'name', type: 'string' },
			{ name: 'title', type: 'string' },
			{ name: 'order', type: 'int' },
			{ name: 'direct', type: 'string' },
			{ name: 'url', type: 'string' }
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
	Ext.define('NetProfile.store.menu.${menu.name}', {
		extend: 'Ext.data.TreeStore',
		requires: 'NetProfile.model.MenuItem',
		model: 'NetProfile.model.MenuItem',
% if menu.direct:
		proxy: {
			type: 'direct',
			directFn: NetProfile.api.MenuTree.${menu.direct},
			reader: {
				type: 'json',
				root: 'records'
			}
		},
		root: {
			expanded: true
		},
		autoLoad: false,
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
			create:  NetProfile.api.${model}.create,
			read:    NetProfile.api.${model}.read,
			update:  NetProfile.api.${model}.update,
			destroy: NetProfile.api.${model}.delete
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
		extend: 'Ext.data.Store',
		requires: 'NetProfile.model.${module}.${model}',
		model: 'NetProfile.model.${module}.${model}',
		sorters: ${mod.default_sort | n, jsone},
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
});

Ext.application({
	name: 'NetProfile',
	appFolder: 'static/core/webshell',
	autoCreateViewport: false,

	models: [],
	stores: [],
	controllers: ['DataStores'],

	launch: function()
	{
		var state_prov = null;

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

		var npp = Ext.direct.Manager.getProvider('netprofile-provider');
		npp.on('exception', function(p, e)
		{
			console.error(e.message);
		});
		npp.on('data', function(p, e)
		{
			if(!e.result.success)
				console.log(e.result.message);
		});

		Ext.create('NetProfile.view.Viewport', {});
	}
});

