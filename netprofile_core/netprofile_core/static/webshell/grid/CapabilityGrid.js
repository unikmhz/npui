/**
 * @class NetProfile.grid.CapabilityGrid
 * @extends Ext.grid.Panel
 */
Ext.define('NetProfile.grid.CapabilityGrid', {
	extend: 'Ext.grid.Panel',
	alias: 'widget.capgrid',
	requires: [
		'Ext.grid.*',
		'Ext.data.*',
		'Ext.util.*',
		'Ext.state.*',
		'Ext.form.*',
		'Ext.menu.*',
		'Ext.toolbar.Paging',
		'Ext.toolbar.TextItem',
		'NetProfile.data.PrivCapStore',
		'NetProfile.window.CenterWindow'
	],

	ownerId: null,
	code: null,
	apiGet: null,
	apiSet: null,
	canSet: false,
	showACL: true,
	border: 0,
	invalidateScrollerOnRefresh: false,

	textCatagory: 'Category',
	textName: 'Name',
	textValue: 'Value',
	textAllowed: 'Allowed',
	textDenied: 'Denied',
	textNotDefined: 'Not Defined',
	textTipACL: 'Edit ACLs',

	groupHeaderTpl: '{columnName}: {name} ({rows.length} total)',

	dockedItems: [],
	plugins: [],
	features: [],
	viewConfig: {
		stripeRows: true,
		plugins: []
	},

	initComponent: function()
	{
		var me = this;

		me.columns = [];
		if(me.showACL)
		{
			me.columns.push({
				header: me.textCategory,
				dataIndex: 'prefix',
				name: 'prefix',
				flex: 1
			}, {
				header: me.textName,
				dataIndex: 'suffix',
				name: 'name',
				flex: 4,
				groupable: false
			});
		}
		else
		{
			me.columns.push({
				header: me.textName,
				dataIndex: 'name',
				name: 'name',
				flex: 1,
				groupable: false
			});
		}
		me.columns.push({
			header: me.textValue,
			dataIndex: 'value',
			name: 'value',
			sortable: false,
			groupable: false,
			width: 120,
		    renderer: function(value, meta, record, rowidx, colidx, store)
			{
				if(value === true)
					return Ext.String.format(
						'<img class="np-cap-icon" src="{0}/static/core/img/priv_allowed.png" alt="{1}" title="{1}" />{1}',
						NetProfile.staticURL, me.textAllowed
					);
				if(value === false)
					return Ext.String.format(
						'<img class="np-cap-icon" src="{0}/static/core/img/priv_denied.png" alt="{1}" title="{1}" />{1}',
						NetProfile.staticURL, me.textDenied
					);
				if(value === null)
					return Ext.String.format(
						'<img class="np-cap-icon" src="{0}/static/core/img/priv_undef.png" alt="{1}" title="{1}" />{1}',
						NetProfile.staticURL, me.textNotDefined
					);
		        return value;
		    },
			editor: {
				xtype: 'combobox',
				format: 'string',
				editable: false,
				valueField: 'xid',
				displayField: 'value',
				forceSelection: false,
				allowBlank: true,
				queryMode: 'local',
				emptyText: me.textNotDefined,
				store: {
					xtype: 'simplestore',
					fields: [{
						name: 'xid',
						type: 'boolean',
						allowNull: true,
						allowBlank: true
					}, {
						name: 'value',
						type: 'string'
					}],
					data: [{
						xid: null,
						value: me.textNotDefined
					}, {
						xid: true,
						value: me.textAllowed
					}, {
						xid: false,
						value: me.textDenied
					}]
				}
			}
		});
		if(me.showACL)
			me.columns.push({
				xtype: 'actioncolumn',
				width: 20,
				groupable: false,
				items: [{
					iconCls: 'ico-mod-acl',
					tooltip: me.textTipACL,
					handler: function(grid, rowi, coli, item, e, rec)
					{
						var acl_win, grid_cfg;

						acl_win = Ext.create('NetProfile.window.CenterWindow', {
							title: me.textTipACL + ': ' + rec.get('name'),
							modal: true
						});
						grid_cfg = {
							xtype: 'capgrid',
							stateId: null,
							stateful: false,
							showACL: false,
							ownerId: me.ownerId,
							code: rec.get('code')
						};
						if(me.apiGet)
							grid_cfg.apiGet = me.apiGet.replace('Privilege', 'ACL');
						if(me.apiSet)
							grid_cfg.apiSet = me.apiSet.replace('Privilege', 'ACL');
						acl_win.add(Ext.create('NetProfile.grid.CapabilityGrid', grid_cfg));
						acl_win.show();
					}
				}],
				sortable: false,
				resizable: false,
				menuDisabled: true,
				renderer: function(val, meta, rec, row, col, store, view)
				{
					if(!rec.get('hasacls'))
						meta.style = 'display: none;';
				}
			});

		me.plugins.push({
			ptype: 'cellediting',
			pluginId: 'editcell',
			triggerEvent: 'cellclick'
		});
		if(me.showACL)
			me.features = [{
				ftype: 'grouping',
				groupHeaderTpl: me.groupHeaderTpl,
				hideGroupedHeader: true,
				startCollapsed: true,
				id: 'privGroup'
			}];

		if(!me.store)
		{
			me.store = Ext.create('NetProfile.data.PrivCapStore', {
				proxy: {
					type: 'direct',
					api: {
						create: Ext.emptyFn,
						read: me.apiGet,
						update: me.apiSet,
						destroy: Ext.emptyFn
					},
					reader: {
						type: 'json',
						idProperty: 'privid',
						messageProperty: 'message',
						rootProperty: 'records',
						successProperty: 'success',
						totalProperty: 'total'
					},
					writer: {
						type: 'json',
						rootProperty: 'records',
						writeAllFields: true,
						allowSingle: false
					},
					extraParams: { owner: me.ownerId, code: me.code }
				},
				listeners: {
					beforeload: {
						fn: function(st, op)
						{
							if(!me.ownerId)
							{
								var rec = me.up('panel[cls~=record-tab]');

								if(rec && rec.record)
								{
									me.ownerId = rec.record.getId();
									st.proxy.extraParams = { owner: me.ownerId };
								}
							}
						},
						single: true
					}
				}
			});
		}

		me.callParent();
	}
});

