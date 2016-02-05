/**
 * @class NetProfile.window.ReportsWindow
 * @extends Ext.window.Window
 */
Ext.define('NetProfile.window.ReportsWindow', {
	extend: 'Ext.window.Window',
	alias: 'widget.reportswindow',
	requires: [
		'Ext.data.Store',
		'Ext.chart.*',
		'Ext.form.*'
	],

	config: {
		modal: true,
		shrinkWrap: 3,
		minHeight: 500,
		minWidth: 700,
		iconCls: 'ico-chart'
	},

	titleText: 'Report viewer',
	valuesText: 'Values',
	groupByText: 'Group By',
	addText: 'Add',
	removeText: 'Remove',
	newValueText: 'New Value',
	newGroupByText: 'New Group',

	aggregateNames: {
		'count'          : 'Number',
		'count_distinct' : 'Distinct values',
		'min'            : 'Minimum',
		'max'            : 'Maximum',
		'avg'            : 'Average',
		'sum'            : 'Sum'
	},

	apiModule: null,
	apiClass: null,
	grid: null,
	store: null,

	initComponent: function()
	{
		var me = this;

		if(!me.store)
			me.store = me.grid.getStore();

		me.aggregateStore = Ext.create('Ext.data.Store', {
			fields: ['name', 'title', 'func'],
			autoLoad: true,
			proxy: {
				type: 'memory'
			},
			data:   me.grid.reportAggregates
		});
		me.groupByStore = Ext.create('Ext.data.Store', {
			fields: ['name', 'title', 'func'],
			autoLoad: true,
			proxy: {
				type: 'memory'
			},
			data:   me.grid.reportGroupBy
		});

		me.usedValues = [];
		me.usedGroupBy = [];
		me.valueCnt = 0;
		me.groupByCnt = 0;
		me.title = me.titleText;
		me.apiModule = me.grid.apiModule;
		me.apiClass = me.grid.apiClass;
		me.dockedItems = [{
			xtype: 'panel',
			dock: 'left',
			hidden: false,
			width: 230,
			resizable: {
				handles: 'e',
				pinned: false
			},
			layout: {
				type: 'accordion',
				multi: false
			},
			itemId: 'leftbar',
			items: [{
				xtype: 'form',
				itemId: 'values',
				scrollable: 'vertical',
				bodyPadding: 4,
				layout: {
					type: 'anchor',
					reserveScrollbar: true
				},
				defaults: {
					anchor: '100%'
				},
				buttons: [{
					text: me.addText,
					iconCls: 'ico-add',
					handler: 'addValueField',
					scope: me
				}],
				title: me.valuesText
			}, {
				xtype: 'panel',
				itemId: 'groupby',
				bodyPadding: 4,
				buttons: [{
					text: me.addText,
					iconCls: 'ico-add',
					handler: 'addGroupByField',
					scope: me
				}],
				title: me.groupByText
			}]
		}];
		me.items = [{
			xtype: 'cartesian',
			layout: 'fit'
		}];

		me.callParent();
	},
	addValueField: function()
	{
		var me = this,
			lbar = me.getDockedComponent('leftbar'),
			pval = lbar.getComponent('values');

		pval.add(me.getValueField());
	},
	addGroupByField: function()
	{
		var me = this,
			lbar = me.getDockedComponent('leftbar'),
			pgrp = lbar.getComponent('groupby');

		pgrp.add(me.getGroupByField());
	},
	getValueField: function()
	{
		var me = this,
			cfg, fldidx;

		fldidx = me.valueCnt;
		me.valueCnt ++;
		cfg = {
			xtype: 'fieldset',
			layout: {
				type: 'anchor',
				reserveScrollbar: false
			},
			defaults: {
				anchor: '100%'
			},
			collapsible: true,
			checkboxToggle: true,
			checkboxName: 'val' + fldidx + '_enabled',
			title: me.newValueText,
			items: [{
				xtype: 'combobox',
				store: me.aggregateStore,
				itemId: 'val' + fldidx + '_field',
				queryMode: 'local',
				forceSelection: true,
				displayField: 'title',
				valueField: 'name',
				listeners: {
					select: function(combo, rec)
					{
						var cmp = combo,
							cont = combo.ownerCt,
							data = [];

						while(cmp = cmp.next())
						{
							cont.remove(cmp, true);
						}

						cont.setTitle(rec.get('title') + ': ?');

						Ext.Array.forEach(rec.get('func'), function(func)
						{
							if(!(func in me.aggregateNames))
								return;
							data.push({
								name: func,
								title: me.aggregateNames[func]
							});
						});
						cont.add({
							xtype: 'combobox',
							store: Ext.create('Ext.data.Store', {
								fields: ['name', 'title'],
								autoLoad: true,
								proxy: {
									type: 'memory'
								},
								data: data
							}),
							queryMode: 'local',
							forceSelection: true,
							displayField: 'title',
							valueField: 'name',
							listeners: {
								select: function(func_combo, func_rec)
								{
									var cont = func_combo.ownerCt,
										field_combo = cont.getComponent('val' + fldidx + '_field'),
										field_value = field_combo.getValue(),
										field_rec = field_combo.findRecordByValue(field_value);

									cont.setTitle(field_rec.get('title') + ': ' + func_rec.get('title'));

									me.usedValues[fldidx] = [func_rec.get('name'), field_rec.get('name'), 'val'+ fldidx];
								}
							}
						});
					}
				}
			}],
			listeners: {
				beforecollapse: function(fset)
				{
					delete me.usedValues[fldidx];

					// XXX: Borks sometimes. Racy?
					if(fset && fset.ownerCt)
					{
						var cont = fset.ownerCt;
						cont.remove(fset, true);
					}
					return false;
				}
			}
		};
		return cfg;
	},
	getGroupByField: function()
	{
		var me = this,
			cfg, fldidx;

		fldidx = me.groupByCnt;
		me.groupByCnt ++;
		cfg = {
			xtype: 'fieldset',
			layout: {
				type: 'anchor',
				reserveScrollbar: false
			},
			defaults: {
				anchor: '100%'
			},
			collapsible: true,
			checkboxToggle: true,
			checkboxName: 'grp' + fldidx + '_enabled',
			title: me.newGroupByText,
			items: [{
				xtype: 'combobox',
				store: me.groupByStore,
				itemId: 'grp' + fldidx + '_field',
				queryMode: 'local',
				forceSelection: true,
				displayField: 'title',
				valueField: 'name',
				listeners: {
					select: function(combo, rec)
					{
						var cmp = combo,
							cont = combo.ownerCt,
							data = [];

						while(cmp = cmp.next())
						{
							cont.remove(cmp, true);
						}
					}
				}
			}],
			listeners: {
				beforecollapse: function(fset)
				{
					delete me.userGroupBy[fldidx];

					// XXX: Borks sometimes. Racy?
					if(fset && fset.ownerCt)
					{
						var cont = fset.ownerCt;
						cont.remove(fset, true);
					}
					return false;
				}
			}
		};
		return cfg;
	}
});

