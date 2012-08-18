<%!

from netprofile.tpl.filters import jsone

%>

Ext.Loader.setConfig({enabled: true});

Ext.Loader.setPath({
	'Ext.ux'               : 'static/core/webshell/ux',
	'NetProfile'           : 'static/core/webshell'
});

Ext.require([
	'Ext.data.*',
	'Ext.direct.*',
	'Ext.tip.*',
	'Ext.state.*',
	'Ext.util.Cookies',
	'Ext.util.History',
	'Ext.Ajax'
], function()
{
	Ext.direct.Manager.addProvider(NetProfile.api.Descriptor);
	Ext.Ajax.defaultHeaders = Ext.apply(Ext.Ajax.defaultHeaders || {}, {'X-CSRFToken': '${req.session.get_csrf_token().decode('utf-8')}'});
	Ext.History.init();

	Ext.data.Types.IPV4 = {
		type: 'ipv4',
		convert: function(value, record) {
			if(value === null)
				return null;
			return value;
		},
		sortType: function(t)
		{
		}
	};
	Ext.data.Types.IPV6 = {
		type: 'ipv6',
		convert: function(value, record) {
			if(value === null)
				return null;
			return value;
		},
		sortType: function(t)
		{
		}
	};

	Ext.apply(Ext.data.validations, {
		rangeMessage: 'is out of range',
		range: function(config, value) {
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

	Ext.define('NetProfile.model.Menu', {
		extend: 'Ext.data.Model',
		fields: [
			{ name: 'name', type: 'string' },
			{ name: 'title', type: 'string' },
			{ name: 'order', type: 'int' }
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
			{ name: 'xview', type: 'string' }
		]
	});
	Ext.define('NetProfile.store.Menu', {
		extend: 'Ext.data.Store',
		requires: 'NetProfile.model.Menu',
		model: 'NetProfile.model.Menu',
		data: ${modules.get_menu_data() | n,jsone},
		storeId: 'npstore_menu'
	});
% for menu in modules.get_menu_data():
	Ext.define('NetProfile.store.menu.${menu.name}', {
		extend: 'Ext.data.TreeStore',
		requires: 'NetProfile.model.MenuItem',
		model: 'NetProfile.model.MenuItem',
		root: {
			expanded: true,
			children: ${modules.get_menu_tree(menu.name) | n,jsone}
		},
		storeId: 'npstore_menu_${menu.name}'
	});
% endfor
% for module in modules:
% for model in modules[module]:
<% mod = modules[module][model] %>
	Ext.define('NetProfile.model.${module}.${model}', {
		extend: 'Ext.data.Model',
		fields: ${mod.get_reader_cfg() | n,jsone},
		associations: ${mod.get_related_cfg() | n,jsone},
		idProperty: '${mod.pk}',
		clientIdProperty: '_clid',
		proxy: {
			type: 'direct',
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
		}
	});

	Ext.define('NetProfile.store.${module}.${model}', {
		extend: 'Ext.data.Store',
		requires: 'NetProfile.model.${module}.${model}',
		model: 'NetProfile.model.${module}.${model}',
		sorters: [], // FIXME
		pageSize: 20,
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
		columns: ${mod.get_column_cfg() | n,jsone},
		apiModule: '${module}',
		apiClass: '${model}',
		stateId: 'npgrid_${module}_${model}',
		stateful: true,
		simpleSearch: ${'true' if mod.easy_search else 'false'},
		detailPane: ${mod.get_detail_pane() | n,jsone}
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
	controllers: [],

	launch: function() {
		var state_prov = null;

		try {
			state_prov = new Ext.state.LocalStorageProvider({
				prefix: 'nps_'
			});
		}
		catch(e) {
			state_prov = new Ext.state.CookieProvider({
				prefix: 'nps_'
			});
		}

		Ext.state.Manager.setProvider(state_prov);

		var npp = Ext.direct.Manager.getProvider('netprofile-provider');
		npp.on('exception',function(p,e){
			console.log(e.message);
		});
		npp.on('data',function(p,e){
			if(!e.result.success)
				console.log(e.result.message);
		});

		Ext.create('NetProfile.view.Viewport', {
		});
	}
});

