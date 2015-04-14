/**
 * @class NetProfile.entities.grid.HistoryGrid
 * @extends Ext.grid.Panel
 */
Ext.define('NetProfile.entities.grid.HistoryGrid', {
	extend: 'Ext.grid.Panel',
	alias: 'widget.historygrid',
	requires: [
		'Ext.grid.*',
		'Ext.form.field.Number',
		'Ext.form.field.Date',
		'NetProfile.entities.data.EntityHistoryStore'
	],

	entityId: null,

	fromText: 'From',
	toText: 'To',
	numText: 'Max',
	timeText: 'Time',
	authorText: 'Author',
	titleText: 'Title',
	clearText: 'Clear',
	expandAllText: 'Expand All',
	collapseAllText: 'Collapse All',

	disableSelection: true,
	plugins: [{
		ptype: 'rowexpander',
		pluginId: 'rowxp',
		rowBodyTpl: new Ext.XTemplate(
			'<div class="change_details">',
			'<tpl for="parts">',
				'<div class="change_bit">',
					'<div class="change_icon"><img class="np-block-img" src="{icon:this.makeIcon}" /></div>',
					'<div class="change_text">{text}</div>',
				'</div>',
			'</tpl>',
			'</div>',
			{
				makeIcon: function(icondef)
				{
					var i = icondef.split(':');
					return NetProfile.staticURL + '/static/' + i[0] + '/img/history/' + i[1] + '.png';
				}
			}
		)
	}],
	viewConfig: {
		stripeRows: true,
		plugins: []
	},
	border: 0,

	initComponent: function()
	{
		this.tabConfig = { cls: 'record-tab-hdl' };
		this.columns = [{
			text: this.timeText,
			tooltip: this.timeText,
			dataIndex: 'time',
			xtype: 'datecolumn',
			sortable: true,
			resizable: true,
			filterable: true,
			format: 'd.m.Y H:i:s', // FIXME!
			flex: 1
		}, {
			text: this.authorText,
			tooltip: this.authorText,
			dataIndex: 'author',
			flex: 1
		}, {
			text: this.titleText,
			tooltip: this.titleText,
			dataIndex: 'title',
			flex: 4
		}];
		if(!this.plugins)
			this.plugins = [];
		this.dockedItems = [{
			xtype: 'toolbar',
			dock: 'top',
			itemId: 'toolTop',
			items: [{
				xtype: 'datefield',
				itemId: 'dateFrom',
				name: 'date_from',
				value: new Date(),
				emptyText: this.fromText,
				width: 100,
				listeners: {
					change: function(fld, newval, oldval)
					{
						this.getStore().reload();
					},
					scope: this
				}
			}, {
				xtype: 'datefield',
				itemId: 'dateTo',
				name: 'date_to',
				value: new Date(),
				emptyText: this.toText,
				width: 100,
				listeners: {
					change: function(fld, newval, oldval)
					{
						this.getStore().reload();
					},
					scope: this
				}
			}, {
				xtype: 'numberfield',
				itemId: 'maxNum',
				name: 'max_num',
				value: 20,
				minValue: 0,
				maxValue: 500,
				emptyText: this.numText,
				width: 55,
				listeners: {
					change: function(fld, newval, oldval)
					{
						this.getStore().reload();
					},
					scope: this
				}
			}, {
				iconCls: 'ico-clear',
				text: this.clearText,
				handler: function(btn, ev)
				{
					var me = this,
						tb = me.getDockedComponent('toolTop'),
						fld_from = tb.getComponent('dateFrom'),
						fld_to = tb.getComponent('dateTo'),
						fld_num = tb.getComponent('maxNum'),
						store = me.getStore();

					if(fld_from)
					{
						fld_from.suspendEvents();
						fld_from.setValue(new Date());
						fld_from.resumeEvents();
					}
					if(fld_to)
					{
						fld_to.suspendEvents();
						fld_to.setValue(new Date());
						fld_to.resumeEvents();
					}
					if(fld_num)
					{
						fld_num.suspendEvents();
						fld_num.setValue(20);
						fld_num.resumeEvents();
					}
					store.reload();
				},
				scope: this
			}, '->', {
				iconCls: 'ico-expand',
				text: this.expandAllText,
				handler: function(btn, ev)
				{
					this.setAllExpanders(true);
				},
				scope: this
			}, {
				iconCls: 'ico-collapse',
				text: this.collapseAllText,
				handler: function(btn, ev)
				{
					this.setAllExpanders(false);
				},
				scope: this
			}]
		}];

		if(!this.store)
		{
			this.store = Ext.create('NetProfile.entities.data.EntityHistoryStore', {
				proxy: {
					type: 'direct',
					api: {
						read: NetProfile.api.Entity.get_history
					},
					simpleSortMode: true,
					filterParam: '__filter',
					sortParam: 'sort',
					directionParam: 'dir',
					startParam: undefined,
					limitParam: undefined,
					pageParam: undefined,
					groupParam: '__group',
					reader: {
						type: 'json',
						rootProperty: 'history',
						successProperty: 'success',
						totalProperty: 'total'
					}
				}
			});
		}

		this.callParent();

		this.on('afterrender', this.onGridRender);
		this.mon(this.store, 'beforeload', this.onStoreLoad, this);
	},

	onGridRender: function(grid)
	{
		var rec, store;

		if(!grid.entityId)
		{
			rec = this.up('panel[cls~=record-tab]');
			if(rec && rec.record)
				grid.entityId = rec.record.getId();
		}
		store = grid.getStore();
		store.load();
	},
	onStoreLoad: function(store, op)
	{
		var me = this,
			prx = store.proxy,
			tb = me.getDockedComponent('toolTop'),
			fld_from = tb.getComponent('dateFrom'),
			fld_to = tb.getComponent('dateTo'),
			fld_num = tb.getComponent('maxNum'),
			xp = { eid: me.entityId };

		if(fld_from)
			xp.begin = fld_from.getValue();
		if(fld_to)
			xp.end = fld_to.getValue();
		if(fld_num)
			xp.maxnum = fld_num.getValue();
		prx.extraParams = xp;
	},
	setAllExpanders: function(value)
	{
		var me = this,
			store = me.getStore(),
			plug = me.getPlugin('rowxp'),
			records = store.getRange(),
			len = records.length,
			i, rec;

		for(i = 0; i < len; i++)
		{
			rec = records[i];
			if(plug.recordsExpanded[rec.internalId] !== value)
				plug.toggleRow(i, rec);
		}
	}
});

