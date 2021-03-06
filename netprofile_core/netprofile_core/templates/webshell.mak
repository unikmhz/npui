## -*- coding: utf-8 -*-
##
## NetProfile: JavaScript template for administrative UI
## Copyright © 2012-2017 Alex Unigovsky
##
## This file is part of NetProfile.
## NetProfile is free software: you can redistribute it and/or
## modify it under the terms of the GNU Affero General Public
## License as published by the Free Software Foundation, either
## version 3 of the License, or (at your option) any later
## version.
##
## NetProfile is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General
## Public License along with NetProfile. If not, see
## <http://www.gnu.org/licenses/>.
##
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
	'Ext.Component',
	'Ext.container.Container',
	'Ext.button.Button',
	'Ext.util.Cookies',
	'Ext.util.DelayedTask',
	'Ext.util.LocalStorage',
	'Ext.Ajax',
% for i_ajs in res_ajs:
	${i_ajs | jsone},
% endfor
	'NetProfile.data.BaseModel',
	'NetProfile.data.SockJS',
	'NetProfile.grid.CapabilityGrid',
	'NetProfile.form.field.MultiField',
	'NetProfile.window.CenterWindow',
	'NetProfile.panel.Wizard',
	'NetProfile.panel.Calendar'
], function()
{
	Ext.BLANK_IMAGE_URL = ${req.static_url('netprofile_core:static/img/blank.gif') | jsone};
% if req.debug_enabled:
	NetProfile.debugEnabled = true;
% else:
	NetProfile.debugEnabled = false;
% endif
	NetProfile.currentLocale = ${cur_loc | jsone};
	NetProfile.currentUser = ${req.user.login | jsone};
	NetProfile.currentUserId = ${req.user.id | n,jsone};
% if req.np_session:
	NetProfile.currentSession = ${str(req.np_session) | jsone};
	NetProfile.currentSessionTimeout = ${req.user.sess_timeout | n,jsone};
% endif
	NetProfile.userSettings = ${req.user.client_settings(req) | n,jsone};
	NetProfile.userCapabilities = ${req.user.flat_privileges | n,jsone};
	NetProfile.userACLs = ${req.user.client_acls(req) | n,jsone};
	NetProfile.rootFolder = ${req.user.get_root_folder() | n,jsone};
	NetProfile.baseURL = ${req.host_url | jsone};
	NetProfile.staticURL = ${req.host_url | jsone};
	NetProfile.state = null;
% if rt_url:
	NetProfile.rtURL = '${rt_url}';
% elif rt_host:
	NetProfile.rtURL = '//${rt_host}:${rt_port}';
% else:
	NetProfile.rtURL = null;
% endif
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
		'X-CSRFToken': ${req.get_csrf() | jsone}
	});
	NetProfile.msg = function()
	{
		function getMsg(cls, delay, title, args)
		{
			return Ext.toast({
				html: Ext.String.format.apply(Ext.String, args),
				title: title,
				minWidth: 200,
				maxWidth: 450,
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
	NetProfile.onSessionTimeout = function()
	{
% if req.debug_enabled:
		Ext.log.info('Session timeout, reloading window');
% endif
		window.location.reload();
	};
	NetProfile.sessionTimeoutTask = new Ext.util.DelayedTask(NetProfile.onSessionTimeout, NetProfile);

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
	NetProfile.logOut = function(save_state)
	{
		var sp = Ext.state.Manager.getProvider();
		if(sp && sp.state)
		{
			if(save_state)
			{
				NetProfile.api.DataCache.save_ls(sp.state, function(data, res)
				{
					Ext.Object.each(sp.state, function(k)
					{
						sp.clear(k);
					});
					sp.clear('loaded');
					window.location.href = '/logout';
				});
			}
			else
			{
				Ext.Object.each(sp.state, function(k)
				{
					sp.clear(k);
				});
				sp.clear('loaded');
				window.location.href = '/logout';
			}
		}
		else
			window.location.href = '/logout';
	};
	NetProfile.changePassword = function()
	{
		var win;

		win = Ext.create('NetProfile.window.CenterWindow', {
			iconCls: 'ico-lock',
			items: [{
				xtype: 'npwizard',
				shrinkWrap: true,
				showNavigation: false,
				wizardCls: 'User',
				createApi: 'get_chpass_wizard',
				submitApi: 'change_password',
				validateApi: 'ChangePassword',
				afterSubmit: function(data)
				{
					NetProfile.logOut(false);
				}
			}],
		});
		win.show();
	};

	NetProfile.showConsole = function()
	{
		var pbar = Ext.getCmp('npws_propbar'),
			store = NetProfile.StoreManager.getConsoleStore('system', 'log'),
			str_id = 'cons:system:log',
			tab;

		tab = pbar.addConsoleTab(str_id, {
			xtype: 'grid',
			title: ${_('System Console') | jsone},
			iconCls: 'ico-console',
			store: store,
			viewConfig: {
				preserveScrollOnRefresh: true
			},
			columns: [{
				text: ${_('Date') | jsone},
				dataIndex: 'ts',
				width: 120,
				xtype: 'datecolumn',
				format: Ext.util.Format.dateFormat + ' H:i:s'
			}, {
				text: ${_('Message') | jsone},
				dataIndex: 'data',
				flex: 1,
				sortable: false,
				filterable: false,
				menuDisabled: true,
				allowMarkup: true,
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

			if(node)
				view.focusNode(node);
		});
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
	Ext.define('Ext.overrides.mod.ExtraFormatters', {
		override: 'Ext.util.Format',
		encodeURI: encodeURI
	});

	Ext.define('Ext.overrides.xss.Component', {
		override: 'Ext.Component',
		config: {
			allowMarkup: false
		},
		privates: {
			doRenderContent: function(out, renderData)
			{
				var me = renderData.$comp,
					html = me.html;

				if(html && !me.getAllowMarkup())
					me.html = Ext.String.htmlEncode(html);

				me.callParent([out, renderData]);
			}
		},
		update: function(htmlOrData, loadScripts, callback)
		{
			if(htmlOrData && Ext.isString(htmlOrData) && !this.getAllowMarkup())
				htmlOrData = Ext.String.htmlEncode(htmlOrData);
			this.callParent([htmlOrData, loadScripts, callback]);
		}
	});
	Ext.define('Ext.overrides.xss.Button', {
		override: 'Ext.button.Button',
		applyText: function(text, oldText)
		{
			if(text && !this.getAllowMarkup())
				text = Ext.String.htmlEncode(text);
			return this.callParent([text, oldText]);
		}
	});
	Ext.define('Ext.overrides.xss.Display', {
		override: 'Ext.form.field.Display',
		htmlEncode: true,
		updateAllowMarkup: function(allow)
		{
			this.htmlEncode = !allow;
		}
	});
	Ext.define('Ext.overrides.xss.Column', {
		override: 'Ext.grid.column.Column',
		allowMarkup: false,
		setupRenderer: function(type)
		{
			var me = this;

			me.callParent([type]);

			if(!type && !me.allowMarkup)
			{
				var oldRenderer = me.renderer;

				me.renderer = function(value)
				{
					if(oldRenderer)
						value = oldRenderer.apply(this, arguments);
					if(value)
						value = Ext.String.htmlEncode(value);

					return value;
				};
			}
		}
	});
	Ext.define('Ext.overrides.xss.TreeColumn', {
		override: 'Ext.tree.Column',
		setupRenderer: function(type)
		{
			var me = this,
				origAllowMarkup = me.allowMarkup;

			me.allowMarkup = true;
			me.callParent([type]);
			me.allowMarkup = origAllowMarkup;
		},
		initComponent: function()
		{
			var me = this;

			me.callParent();
			me.setupXssProtectorRenderer();
		},
		setupXssProtectorRenderer: function()
		{
			var me = this;

			if(!me.allowMarkup)
			{
				var oldRenderer = me.innerRenderer;

				me.innerRenderer = function(value)
				{
					if(oldRenderer)
						value = oldRenderer.apply(this, arguments);
					if(value)
						value = Ext.String.htmlEncode(value);
					return value;
				};
			}
		}
	});
	Ext.define('Ext.overrides.xss.Title', {
		override: 'Ext.panel.Title',
		applyText: function(text, oldText)
		{
			text = this.callParent([text, oldText]);
			if(!this.getAllowMarkup())
				text = Ext.String.htmlEncode(text);
			return text;
		}
	});
	Ext.define('Ext.overrides.xss.MessageBox', {
		override: 'Ext.window.MessageBox',
		initComponent: function(cfg)
		{
			this.callParent([cfg]);
			this.updateAllowMarkup(this.allowMarkup);
		},
		updateAllowMarkup: function(allow)
		{
			if(this.msg)
				this.msg.allowMarkup = allow;
		},
		reconfigure: function(cfg)
		{
			this.updateAllowMarkup(cfg.allowMarkup);
			this.callParent([cfg]);
		}
	});
	Ext.define('Ext.overrides.xss.BoundList', {
		override: 'Ext.view.BoundList',
		initComponent: function()
		{
			var me = this;

			me.origInnerTpl = me.getInnerTpl;
			me.getInnerTpl = function(displayField)
			{
				var tpl = me.origInnerTpl(displayField);

				if(tpl)
					tpl = tpl.replace(/\{(.*?)\}/g, '{$1:htmlEncode}');
				return tpl;
			};
			me.callParent();
		}
	});
	Ext.define('Ext.overrides.xss.Check', {
		override: 'Ext.grid.column.Check',
		allowMarkup: true
	});
	Ext.define('Ext.overrides.xss.ToolbarText', {
		override: 'Ext.toolbar.TextItem',
		allowMarkup: true
	});
	Ext.define('Ext.overrides.xss.ToolTip', {
		override: 'Ext.tip.ToolTip',
		allowMarkup: true
	});
	Ext.define('Ext.overrides.xss.QuickTip', {
		override: 'Ext.tip.QuickTip',
		update: function(htmlOrData, loadScripts, callback)
		{
			if(this.activeTarget && (el = Ext.fly(this.activeTarget.el)))
			{
				if(el && el.component && el.component.errorEl)
				{
					var origAllowMarkup = this.getAllowMarkup();

					this.setAllowMarkup(el.component.errorEl.allowMarkup);
					this.callParent([htmlOrData, loadScripts, callback]);
					this.setAllowMarkup(origAllowMarkup);
					return;
				}
			}
			this.callParent([htmlOrData, loadScripts, callback]);
		}
	});
	Ext.define('Ext.overrides.xss.RowExpander', {
		override: 'Ext.grid.plugin.RowExpander',
		getHeaderConfig: function()
		{
			var cfg = this.callParent(arguments);
			cfg.allowMarkup = true;
			return cfg;
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
	Ext.define('Ext.overrides.bugfix.Editor', {
		override: 'Ext.Editor',
		initComponent: function()
		{
			var me = this,
				field = me.field = Ext.ComponentManager.create(me.field || {}, 'textfield');

			if(field.ownerCt)
				field = me.field = field.cloneConfig();

			field.msgTarget = field.msgTarget || 'qtip';
			me.mon(field, {
				scope: me,
				specialkey: me.onSpecialKey
			});

			if(field.grow)
				me.mon(field, 'autosize', me.onFieldAutosize,  me, {delay: 1});
			me.floating = {
				constrain: me.constrain
			};
			me.items = field;

			me.callSuper(arguments);
		}
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
		fields: ${mod.get_reader_cfg(req) | n,jsone},
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
		pageSize: NetProfile.userSettings['core.ui.datagrid_perpage'],
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
		extraActions: ${mod.get_extra_actions(req) | n,jsone},
		detailPane: ${mod.get_detail_pane(req) | n,jsone},
% if mod.row_class_field:
		rowClassField: ${mod.row_class_field | n,jsone},
% endif
% if mod.create_wizard:
		canCreate: <%np:jscap code="${mod.cap_create}" />,
% else:
		canCreate: false,
% endif
		canEdit: <%np:jscap code="${mod.cap_edit}" />,
		canDelete: <%np:jscap code="${mod.cap_delete}" />,
		canShowReports: true,
		reportAggregates: ${mod.get_aggregates(req) | n,jsone},
		reportGroupBy: ${mod.get_groupby_groups(req) | n,jsone},
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
		// TODO: defaultToken: 'dashboard',

		models: [],
		views: [
			'ChangePassword',
			'Viewport'
		],
		stores: [],
		controllers: [
			'NetProfile.controller.DataStores',
			'NetProfile.controller.Users',
			'NetProfile.controller.FileAttachments',
% for cont in res_ctl:
			${cont | jsone},
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
			Ext.direct.Manager.on('sesstimeout', function(ev)
			{
				NetProfile.onSessionTimeout();
			});
			if(NetProfile.currentSessionTimeout)
				NetProfile.sessionTimeoutTask.delay((NetProfile.currentSessionTimeout + 3) * 1000);
			direct_provider = Ext.direct.Manager.getProvider('netprofile-provider');
			direct_provider.on('exception', function(p, e)
			{
				if(e && e.message)
				{
% if req.debug_enabled:
					Ext.log.error(e.message);
% endif
					NetProfile.msg.err(${_('Error') | jsone}, '{0}', e.message);
				}
			});
			direct_provider.on('data', function(p, e)
			{
				if(e.sto)
				{
					NetProfile.currentSessionTimeout = e.sto;
					NetProfile.sessionTimeoutTask.delay((NetProfile.currentSessionTimeout + 3) * 1000);
				}
				if(e.result && !e.result.success)
				{
					if(e.result.message)
					{
% if req.debug_enabled:
						Ext.log.warn(e.result.message);
						if(e.result.stacktrace)
							Ext.log.info(e.result.stacktrace);
% endif
						NetProfile.msg.warn(${_('Warning') | jsone}, '{0}', e.result.message);
					}
				}
			});

% if pw_age == 'force':
			app.setMainView('ChangePassword');
			NetProfile.rtURL = null;
% endif

			// Init SockJS connection to realtime server
			if(NetProfile.rtURL)
				NetProfile.rtSocket = Ext.create('NetProfile.data.SockJS', {
					url: NetProfile.rtURL + '/sock'
				});
		},
		showStartupMessages: function()
		{
% if pw_age == 'warn':
			Ext.toast({
				title: ${_('Please change your password') | jsone},
				minWidth: 200,
				maxWidth: 450,
				align: 'br',
				autoCloseDelay: 5000,
				iconCls: 'ico-lock',
				layout: {
					type: 'vbox',
					align: 'stretch'
				},
				items: [{
					xtype: 'component',
					html: Ext.String.format(
						${_('Your current password will expire in approximately {0}. Please change it as soon as possible.') | jsone},
						${req.localizer.pluralize('${num} day', '${num} days', pw_days, domain='netprofile_core', mapping={ 'num' : pw_days }) | jsone}
					)
				}, {
					xtype: 'container',
					padding: '6 0 0 0',
					layout: {
						type: 'hbox',
						pack: 'end'
					},
					items: [{
						xtype: 'button',
						iconCls: 'ico-lock',
						text: ${_('Change now') | jsone},
						handler: function()
						{
							NetProfile.changePassword();
						}
					}]
				}]
			});
% endif
		},
		launch: function(profile)
		{
			var me = this,
				spl = Ext.get('splash');

			if(spl)
				spl.fadeOut({
					opacity: 0,
					delay: 300,
					duration: 400,
					easing: 'easeIn',
					remove: true,
					useDisplay: true,
					callback: 'showStartupMessages',
					scope: me
				});
			else
				me.showStartupMessages();
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

