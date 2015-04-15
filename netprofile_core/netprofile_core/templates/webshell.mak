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
	'Ext.menu.*',
	'Ext.state.*',
	'Ext.util.Cookies',
	'Ext.util.LocalStorage',
	'Ext.Ajax',
% for i_ajs in res_ajs:
	'${i_ajs}',
% endfor
	'NetProfile.data.BaseModel',
	'NetProfile.grid.CapabilityGrid',
	'NetProfile.form.field.MultiField',
	'NetProfile.panel.Calendar'
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
	NetProfile.state = null;
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
	Ext.Ajax.setDefaultHeaders({
		'X-CSRFToken': '${req.get_csrf()}'
	});
	NetProfile.msg = function()
	{
		function getMsg(cls, delay, title, args)
		{
			return Ext.toast({
				html: Ext.String.format.apply(Ext.String, args),
				title: title,
				minWidth: 200,
				align: 'br',
				autoCloseDelay: delay,
				iconCls: cls
			});
		}

		return {
			notify: function(title, fmt)
			{
				return getMsg('ico-info', 3000, title, Ext.Array.slice(arguments, 1));
			},
			warn: function(title, fmt)
			{
				return getMsg('ico-warning', 4500, title, Ext.Array.slice(arguments, 1));
			},
			err: function(title, fmt)
			{
				return getMsg('ico-error', 6000, title, Ext.Array.slice(arguments, 1));
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

	Ext.define('Ext.overrides.mod.AcceptFormData', {
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
	Ext.define('Ext.overrides.mod.FieldAsyncErrors', {
		override: 'Ext.form.field.Field',
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
	Ext.define('Ext.overrides.mod.BaseAsyncErrors', {
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
	Ext.define('Ext.overrides.mod.ROTrigger', {
		override: 'Ext.form.trigger.Trigger',
		disableOnReadOnly: true,
		onClick: function()
		{
			var me = this,
				args = arguments,
				e = me.clickRepeater ? args[1] : args[0],
				handler = me.handler,
				field = me.field;

			if(handler && (!field.readOnly || !me.disableOnReadOnly) && me.isFieldEnabled())
				Ext.callback(me.handler, me.scope, [field, me, e], 0, field);
		}
	});
	Ext.define('Ext.overrides.bugfix.EXTJS16183.menu', {
		override: 'Ext.menu.Menu',
		compatibility: '5.1.0.107',
		onFocusLeave: function(e)
		{
			var me = this;

			me.callSuper([e]);
			me.mixins.focusablecontainer.onFocusLeave.call(me, e);
			if(me.floating)
				me.hide();
		},
		beforeShow: function()
		{
			var me = this,
				activeEl, viewHeight;

			// Constrain the height to the containing element's viewable area
			if(me.floating)
			{
				if(!me.parentMenu && !me.allowOtherMenus)
					Ext.menu.Manager.hideAll();
				// Only register a focusAnchor to return to on hide if the active element is not the document
				// If there's no focusAnchor, we return to the ownerCmp, or first focusable ancestor.
				activeEl = Ext.Element.getActiveElement();
				me.focusAnchor = activeEl === document.body ? null : activeEl;

				me.savedMaxHeight = me.maxHeight;
				viewHeight = me.container.getViewSize().height;
				me.maxHeight = Math.min(me.maxHeight || viewHeight, viewHeight);
			}

			me.callSuper(arguments);

			// Add a touch start listener to check for taps outside the menu.
			// iOS in particular does not trigger blur on document tap, so
			// we have to check for taps outside this menu.
			if(Ext.supports.Touch)
			{
				me.tapListener = Ext.getBody().on({
					touchstart: me.onBodyTap,
					scope: me,
					destroyable: true
				});
			}
		},
		afterShow: function()
		{
			var me = this;

			me.callSuper(arguments);
			Ext.menu.Manager.onShow(me);

			// Restore configured maxHeight
			if(me.floating && me.autoFocus)
			{
				me.maxHeight = me.savedMaxHeight;
				me.focus();
			}
		},
		onHide: function(animateTarget, cb, scope)
		{
			var me = this,
				focusTarget;

			// If we contain focus just before element hide, move it elsewhere before hiding
			if(me.el.contains(Ext.Element.getActiveElement()))
			{
				// focusAnchor was the active element before this menu was shown.
				focusTarget = me.focusAnchor || me.ownerCmp || me.up(':focusable');

				// Component hide processing will focus the "previousFocus" element.
				if(focusTarget)
					me.previousFocus = focusTarget;
			}
			this.callSuper([animateTarget, cb, scope]);
			Ext.menu.Manager.onHide(me);
		}
	});
	Ext.define('Ext.overrides.bugfix.EXTJS16183.menuMgr', {
		override: 'Ext.menu.Manager',
		compatibility: '5.1.0.107',
		visible: [],
		onShow: function(menu)
		{
			if(menu.floating)
				Ext.Array.include(this.visible, menu);
		},
		onHide: function(menu)
		{
			if(menu.floating)
				Ext.Array.remove(this.visible, menu);
		},
		hideAll: function()
		{
			var allMenus = this.visible,
				len = allMenus.length,
				i,
				result = false;

			for(i = 0; i < len; i++)
			{
				allMenus[i].hide();
				result = true;
			}
			return result;
		},
		checkActiveMenus: function(e)
		{
			var allMenus = this.visible,
				len = allMenus.length,
				i, menu;

			for(i = 0; i < len; ++i)
			{
				menu = allMenus[i];
				if(!menu.containsFocus && !menu.owns(e))
					menu.hide();
			}
		}
	});
	Ext.onReady(function()
	{
		Ext.getDoc().on('mousedown', Ext.menu.Manager.checkActiveMenus, Ext.menu.Manager);
	});
	Ext.define('Ext.overrides.bugfix.EXTJS15525', {
		override: 'Ext.util.Collection',
		compatibility: '5.1.0.107',
		updateKey: function (item, oldKey) {
			var me = this,
				map = me.map,
				indices = me.indices,
				source = me.getSource(),
				newKey;

			if (source && !source.updating) {
				// If we are being told of the key change and the source has the same idea
				// on keying the item, push the change down instead.
				source.updateKey(item, oldKey);
			}
			// If there *is* an existing item by the oldKey and the key yielded by the new item is different from the oldKey...
			else if (map[oldKey] && (newKey = me.getKey(item)) !== oldKey) {
				if (oldKey in map || map[newKey] !== item) {
					if (oldKey in map) {
						//<debug>
						if (map[oldKey] !== item) {
							Ext.Error.raise('Incorrect oldKey "' + oldKey +
											'" for item with newKey "' + newKey + '"');
						}
						//</debug>

						delete map[oldKey];
					}

					// We need to mark ourselves as updating so that observing collections
					// don't reflect the updateKey back to us (see above check) but this is
					// not really a normal update cycle so we don't call begin/endUpdate.
					me.updating++;

					me.generation++;
					map[newKey] = item;
					if (indices) {
						indices[newKey] = indices[oldKey];
						delete indices[oldKey];
					}

					me.notify('updatekey', [{
						item: item,
						newKey: newKey,
						oldKey: oldKey
					}]);

					me.updating--;
				}
			}
		}
	});
	Ext.define('Ext.overrides.bugfix.EXTJS16166', {
		override: 'Ext.view.View',
		compatibility: '5.1.0.107',
		handleEvent: function(e) {
			var me = this,
				isKeyEvent = me.keyEventRe.test(e.type),
				nm = me.getNavigationModel();

			e.view = me;

			if (isKeyEvent) {
				e.item = nm.getItem();
				e.record = nm.getRecord();
			}

			// If the key event was fired programatically, it will not have triggered the focus
			// so the NavigationModel will not have this information.
			if (!e.item) {
				e.item = e.getTarget(me.itemSelector);
			}
			if (e.item && !e.record) {
				e.record = me.getRecord(e.item);
			}

			if (me.processUIEvent(e) !== false) {
				me.processSpecialEvent(e);
			}

			// We need to prevent default action on navigation keys
			// that can cause View element scroll unless the event is from an input field.
			// We MUST prevent browser's default action on SPACE which is to focus the event's target element.
			// Focusing causes the browser to attempt to scroll the element into view.

			if (isKeyEvent && !Ext.fly(e.target).isInputField()) {
				if (e.getKey() === e.SPACE || e.isNavKeyPress(true)) {
					e.preventDefault();
				}
			}
		}
	});
	Ext.define('Ext.overrides.bugfix.EXTJS16347', {
		override: 'Ext.data.AbstractStore',
		compatibility: '5.1.0.107',
		applyState: function(state)
		{
			var me = this,
				sorters = me.getSorters(),
				filters = me.getFilters(),
				stateSorters = state.sorters,
				stateFilters = state.filters,
				stateGrouper = state.grouper;

			me.blockLoad();
			if(stateSorters)
			{
				sorters.replaceAll(stateSorters);
			}
			if(stateFilters)
			{
				// We found persisted filters so let's save stateful filters from this point forward.
				me.saveStatefulFilters = true;
				filters.replaceAll(stateFilters);
			}
			if(stateGrouper)
			{
				this.setGrouper(stateGrouper);
			}
			me.unblockLoad();
		}
	});
	Ext.define('Ext.overrides.bugfix.EXTJS16347.filters', {
		override: 'Ext.grid.filters.Filters',
		compatibility: '5.1.0.107',
		initColumns: function()
		{
			var grid = this.grid,
				store = grid.getStore(),
				columns = grid.columnManager.getColumns(),
				len = columns.length,
				i, column,
				filter, filterCollection, block;

			// We start with filters defined on any columns.
			for(i = 0; i < len; i++)
			{
				column = columns[i];
				filter = column.filter;

				if(filter && !filter.isGridFilter)
					this.createColumnFilter(column);
			}
		}
	});
	Ext.define('Ext.overrides.bugfix.EXTJS16023', {
		override: 'Ext.form.field.ComboBox',
		compatibility: '5.1.0.107',
		checkChangeEvents: Ext.isIE ? ['change', 'propertychange', 'keyup'] : ['change', 'input', 'textInput', 'keyup', 'dragdrop']
	});

	Ext.define('NetProfile.data.field.IPv4', {
		extend: 'Ext.data.field.Field',
		alias: 'data.field.ipv4',
		isIPField: true,
		convert: function(value)
		{
			if((value === null) || (value === undefined) || (value === ''))
				return null;
			if(Ext.isObject(value))
			{
				if(value instanceof ipaddr.IPv4)
					return value;
				throw 'Supplied with an unknown object type';
			}
			return ipaddr.IPv4.parse(value);
		},
		serialize: function(value)
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
		},
		getType: function()
		{
			return 'ipv4';
		}
	});
	Ext.define('NetProfile.data.field.IPv6', {
		extend: 'Ext.data.field.Field',
		alias: 'data.field.ipv6',
		isIPField: true,
		convert: function(value)
		{
			if((value === null) || (value === undefined) || (value === ''))
				return null;
			if(Ext.isObject(value))
			{
				if(value instanceof ipaddr.IPv6)
					return value;
				throw 'Supplied with an unknown object type';
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
		serialize: function(value)
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
		},
		getType: function()
		{
			return 'ipv6';
		}
	});

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
		extend: 'Ext.data.Model',
		fields: [
			{ name: 'id',   type: 'auto' },
			{ name: 'ts',   type: 'date', dateFormat: 'c' },
			{ name: 'from', type: 'string' },
			{ name: 'bodytype', type: 'string', defaultValue: 'text' },
			{ name: 'data', type: 'auto' }
		],
		idProperty: 'id'
	});

	Ext.define('NetProfile.view.ExportMenu', {
		extend: 'Ext.menu.Menu',
		alias: 'widget.exportmenu',
		plain: true,
		layout: 'fit',
		minWidth: 200,
		showSeparator: false,
		defaults: {
			plain: true
		},
		items: [{
			xtype: 'panel',
			layout: {
				type: 'accordion',
				align: 'stretch'
			},
			items: ${modules.get_export_menu(req) | n,jsone}
		}]
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
		extend: 'Ext.data.TreeModel',
		fields: [
			{ name: 'id', type: 'string' },
			{ name: 'text', type: 'string' },
			{ name: 'leaf', type: 'boolean' },
			{ name: 'iconCls', type: 'string', persist: false },
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
		extend: 'Ext.data.TreeModel',
		fields: [
			{ name: 'id', type: 'string' },
			{ name: 'text', type: 'string' },
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
		extend: 'NetProfile.data.MenuTreeStore',
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
				rootProperty: 'records',
				messageProperty: 'message',
				successProperty: 'success',
				totalProperty: 'total'
			},
			writer: {
				type: 'json',
				rootProperty: 'records',
				writeAllFields: true,
				allowSingle: false
			}
		},
% if menu.custom_root:
		root: ${menu.custom_root | n,jsone},
% else:
		root: {
			expanded: true
		},
% endif
		autoLoad: false,
		autoSync: false,
% else:
% if menu.custom_root:
		root: ${menu.custom_root | n,jsone},
% else:
		root: {
			expanded: true,
			id: 'top',
			children: ${modules.get_menu_tree(req, menu.name) | n,jsone}
		},
% endif
% endif
		storeId: 'npstore_menu_${menu.name}'
	});\
</%np:limit>\
% endfor

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
			rootProperty: 'records',
			successProperty: 'success',
			totalProperty: 'total'
		},
		writer: {
			type: 'json',
			rootProperty: 'records',
			writeAllFields: false,
			clientIdProperty: '_clid',
			allowSingle: false
		}
	});
	Ext.define('NetProfile.model.${module}.${model}', {
		extend: 'NetProfile.data.BaseModel',
		fields: ${mod.get_reader_cfg() | n,jsone},
		idProperty: '${mod.pk}',
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
		remoteSort: true,
		storeId: 'npstore_${module}_${model}',
		autoLoad: false,
		autoSync: true
	});
	Ext.define('NetProfile.view.grid.${module}.${model}', {
		extend: 'NetProfile.grid.ModelGrid',
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
		canDelete: <%np:jscap code="${mod.cap_delete}" />,
		canExport: ${'false' if (mod.export_view is None) else 'true'}
	});
% endfor
% endfor

	// Choose supported state storage
	if(Ext.util.LocalStorage.supported)
		NetProfile.state = new Ext.state.LocalStorageProvider({
			prefix: 'np' + NetProfile.currentUserId + '_'
		});
	else
		NetProfile.state = new Ext.state.CookieProvider({
			prefix: 'np' + NetProfile.currentUserId + '_'
		});
	var state_loaded = NetProfile.state.get('loaded');

	Ext.onReady(function()
	{
		Ext.tip.QuickTipManager.init();
		Ext.apply(Ext.tip.QuickTipManager.getQuickTip(), {
			anchorToTarget: false,
			anchor: 'right',
			anchorOffset: 12,
			trackMouse: true,
			constraintInsets: '-8 -8 -8 -8',
			showDelay: 650,
			hideDelay: 0
		});
	});

	Ext.define('NetProfile.main.Application', {
		extend: 'Ext.app.Application',
		name: 'NetProfile',
		appFolder: 'static/core/webshell',
		mainView: 'Viewport',

		models: [],
		views: ['Viewport'],
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

		init: function(app)
		{
			var rt_sock = null,
				direct_provider;

			// Init state storage
			Ext.state.Manager.setProvider(NetProfile.state);

			// Init ExtDirect remoting provider
			direct_provider = Ext.direct.Manager.getProvider('netprofile-provider');
			direct_provider.on('exception', function(p, e)
			{
				if(e && e.message)
				{
% if req.debug_enabled:
					Ext.log.error(e.message);
% endif
					NetProfile.msg.err('${_('Error')}', '{0}', e.message);
				}
			});
			direct_provider.on('data', function(p, e)
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

			// Init SockJS connection to realtime server
			// TODO: move this to a separate component
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
		},
		launch: function(profile)
		{
			var spl = Ext.get('splash');

			if(spl)
				spl.fadeOut({
					opacity: 0,
					delay: 300,
					duration: 400,
					easing: 'easeIn',
					remove: true,
					useDisplay: true
				});
			return true;
		}
	});

	if(state_loaded !== 'OK')
		NetProfile.api.DataCache.load_ls(function(data, res)
		{
			if(data && data.state && data.success)
				Ext.Object.each(data.state, function(k, v)
				{
					NetProfile.state.set(k, v);
				});
			NetProfile.state.set('loaded', 'OK');
			Ext.application('NetProfile.main.Application');
		});
	else
		Ext.application('NetProfile.main.Application');

});

