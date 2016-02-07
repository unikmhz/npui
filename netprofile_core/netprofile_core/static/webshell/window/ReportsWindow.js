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
		'Ext.form.*',
		'Ext.toolbar.Toolbar',
		'Ext.picker.Date',
		'NetProfile.form.field.DateTime'
	],

	config: {
		modal: true,
		shrinkWrap: 3,
		layout: 'fit',
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
	generateText: 'Show Report',

	aggregateNames: {
		'count'          : 'Number',
		'count_distinct' : 'Distinct values',
		'min'            : 'Minimum',
		'max'            : 'Maximum',
		'avg'            : 'Average',
		'sum'            : 'Sum'
	},
	groupByNames: {
		'year'   : 'by year',
		'month'  : 'by month',
		'week'   : 'by week',
		'day'    : 'by day',
		'hour'   : 'by hour',
		'minute' : 'by minute'
	},
	groupBySubstitutes: {
		'month'  : ['year', 'month'],
		'week'   : ['year', 'week'],
		'day'    : ['year', 'month', 'day'],
		'hour'   : ['year', 'month', 'day', 'hour'],
		'minute' : ['year', 'month', 'day', 'hour', 'minute']
	},
	groupByOrder: ['year', 'month', 'week', 'day', 'hour', 'minute'],

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
		me.dateRangeType = null;
		me.dateRangeField = null;
		me.valueCnt = 0;
		me.groupByCnt = 0;
		me.title = me.titleText;
		me.apiModule = me.grid.apiModule;
		me.apiClass = me.grid.apiClass;
		me.dockedItems = [{
			xtype: 'toolbar',
			dock: 'top',
			itemId: 'tbar',
			items: [{
				itemId: 'fld_date_from',
				xtype: 'datetimefield',
				disabled: true
			}, {
				itemId: 'fld_date_to',
				xtype: 'datetimefield',
				disabled: true
			}, {
				itemId: 'btn_prev',
				iconCls: 'ico-prev',
				disabled: true,
				handler: 'prevDateRange',
				scope: me
			}, {
				itemId: 'btn_next',
				iconCls: 'ico-next',
				disabled: true,
				handler: 'nextDateRange',
				scope: me
			}, '->', {
				itemId: 'btn_gen',
				iconCls: 'ico-report-plus',
				text: me.generateText,
				enableToggle: true,
				toggleHandler: function(btn, pressed)
				{
					var daterange, store;

					if(pressed)
					{
						daterange = me.getInitialDateRange();
						if(daterange)
							me.setDateRange(daterange[0], daterange[1]);
						else
							me.clearDateRange();

						me.removeAll(true);
						me.add({
							xtype: 'cartesian',
							border: 0,
							store: me.getGraphStore(),
							axes: [me.getGraphXAxis(), me.getGraphYAxis()],
							series: me.getGraphSeries()
						});
					}
					else
					{
						me.clearDateRange();
					}
				}
			}]
		}, {
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
		me.items = [];
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
							funcs = rec.get('func'),
							data = [];

						while(cmp = cmp.next())
						{
							cont.remove(cmp, true);
						}

						if(Ext.isArray(funcs))
						{
							cont.setTitle(rec.get('title') + ': ?');

							Ext.Array.forEach(rec.get('func'), function(func)
							{
								if(!(func in me.groupByNames))
									return;
								data.push({
									name: func,
									title: me.groupByNames[func]
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
											field_combo = cont.getComponent('grp' + fldidx + '_field'),
											field_value = field_combo.getValue(),
											field_rec = field_combo.findRecordByValue(field_value);

										cont.setTitle(field_rec.get('title') + ': ' + func_rec.get('title'));
										me.usedGroupBy[fldidx] = [func_rec.get('name'), field_rec.get('name')];
									}
								}
							});
						}
						else
						{
							cont.setTitle(rec.get('title'));
							me.usedGroupBy[fldidx] = rec.get('name');
						}
					}
				}
			}],
			listeners: {
				beforecollapse: function(fset)
				{
					delete me.usedGroupBy[fldidx];

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
	setDateRange: function(d1, d2)
	{
		var me = this,
			tbar = me.getDockedComponent('tbar'),
			df1 = tbar.getComponent('fld_date_from'),
			df2 = tbar.getComponent('fld_date_to'),
			dprev = tbar.getComponent('btn_prev'),
			dnext = tbar.getComponent('btn_next');

		df1.setValue(d1);
		df2.setValue(d2);

		df1.enable();
		df2.enable();

		dprev.enable();
		dnext.enable();
	},
	clearDateRange: function()
	{
		var me = this,
			tbar = me.getDockedComponent('tbar'),
			df1 = tbar.getComponent('fld_date_from'),
			df2 = tbar.getComponent('fld_date_to'),
			dprev = tbar.getComponent('btn_prev'),
			dnext = tbar.getComponent('btn_next');

		dprev.disable();
		dnext.disable();

		df1.disable();
		df2.disable();

		df1.setValue('');
		df2.setValue('');

		me.dateRangeType = null;
		me.dateRangeField = null;
	},
	prevDateRange: function()
	{
		var me = this,
			tbar = me.getDockedComponent('tbar'),
			df1 = tbar.getComponent('fld_date_from'),
			df2 = tbar.getComponent('fld_date_to'),
			d1 = df1.getValue(),
			d2 = df2.getValue(),
			diff;

		d2.setSeconds(59);
		d2.setMilliseconds(999);
		diff = Ext.Date.diff(d1, d2, Ext.Date.SECOND) + 1;
		d1 = Ext.Date.subtract(d1, Ext.Date.SECOND, diff);
		d2 = Ext.Date.subtract(d2, Ext.Date.SECOND, diff);
		df1.setValue(d1);
		df2.setValue(d2);
		// TODO: update store
	},
	nextDateRange: function()
	{
		var me = this,
			tbar = me.getDockedComponent('tbar'),
			df1 = tbar.getComponent('fld_date_from'),
			df2 = tbar.getComponent('fld_date_to'),
			d1 = df1.getValue(),
			d2 = df2.getValue();

		d2.setSeconds(59);
		d2.setMilliseconds(999);
		diff = Ext.Date.diff(d1, d2, Ext.Date.SECOND) + 1;
		d1 = Ext.Date.add(d1, Ext.Date.SECOND, diff);
		d2 = Ext.Date.add(d2, Ext.Date.SECOND, diff);
		df1.setValue(d1);
		df2.setValue(d2);
		// TODO: update store
	},
	getDateRange: function()
	{
		var me = this,
			tbar = me.getDockedComponent('tbar'),
			df1 = tbar.getComponent('fld_date_from'),
			df2 = tbar.getComponent('fld_date_to');

		if(df1.isDisabled() || df2.isDisabled())
			return null;
		return [df1.getValue(), df2.getValue()];
	},
	getInitialDateRange: function()
	{
		var me = this,
			now = new Date(),
			max_gby = -1,
			fld, d1, d2;

		Ext.Array.forEach(me.usedGroupBy, function(gby)
		{
			var idx;

			if(!Ext.isArray(gby))
				return;
			idx = Ext.Array.indexOf(me.groupByOrder, gby[0]);
			if(idx > max_gby)
			{
				fld = gby[1];
				max_gby = idx;
			}
		});

		if(max_gby <= 0)
			return null;

		me.dateRangeType = me.groupByOrder[max_gby - 1];
		me.dateRangeField = fld;
		switch(me.dateRangeType)
		{
			case 'year':
				d1 = Ext.Date.clearTime(now, true);
				d1.setMonth(0);
				d1.setDate(1);
				d2 = Ext.Date.clone(d1);
				d2.setHours(23);
				d2.setMinutes(59);
				d2.setSeconds(59);
				d2.setMilliseconds(999);
				return [d1, d2];
			case 'month':
				d1 = Ext.Date.getFirstDateOfMonth(now);
				d2 = Ext.Date.getLastDateOfMonth(now);
				d2.setHours(23);
				d2.setMinutes(59);
				d2.setSeconds(59);
				d2.setMilliseconds(999);
				return [d1, d2];
			case 'week':
				d1 = Ext.Date.clearTime(now, true);
				d1.setDate(d1.getDate() - d1.getDay() + Ext.picker.Date.prototype.startDay);
				d2 = Ext.Date.clone(d1);
				d2.setDate(d2.getDate() + 6);
				d2.setHours(23);
				d2.setMinutes(59);
				d2.setSeconds(59);
				d2.setMilliseconds(999);
				return [d1, d2];
			case 'day':
				d1 = Ext.Date.clearTime(now, true);
				d2 = Ext.Date.clone(now);
				d2.setHours(23);
				d2.setMinutes(59);
				d2.setSeconds(59);
				d2.setMilliseconds(999);
				return [d1, d2];
			case 'hour':
				d1 = Ext.Date.clone(now);
				d1.setMinutes(0);
				d1.setSeconds(0);
				d1.setMilliseconds(0);
				d2 = Ext.Date.clone(now);
				d2.setMinutes(59);
				d2.setSeconds(59);
				d2.setMilliseconds(999);
				return [d1, d2];
			case 'minute':
				d1 = Ext.Date.clone(now);
				d1.setSeconds(0);
				d1.setMilliseconds(0);
				d2 = Ext.Date.clone(now);
				d2.setSeconds(59);
				d2.setMilliseconds(999);
				return [d1, d2];
			default:
				return null;
		}
	},
	getGraphStore: function()
	{
		var me = this,
			report_api = NetProfile.api[me.apiClass].report,
			fields = [],
			store;

		Ext.Array.forEach(me.usedValues, function(aggr)
		{
			if(typeof(aggr) === 'undefined')
				return;

			var fld = {
				name: aggr[2],
				type: 'number'
			};
			fields.push(fld);
		});

		Ext.Array.forEach(me.usedGroupBy, function(gby)
		{
			var fld = {},
				model_fld;

			if(typeof(gby) === 'undefined')
				return;
			if(typeof(gby) === 'string')
			{
				model_fld = NetProfile.model[me.apiModule][me.apiClass].getField(gby);
				fld.name = gby;
				fld.type = model_fld.getType();
				fields.push(fld);
				return;
			}

			if(gby[0] in me.groupBySubstitutes)
			{
				Ext.Array.forEach(me.groupBySubstitutes[gby[0]], function(gbsubst)
				{
					fields.push({
						name: gby[1] + '_' + gbsubst,
						type: 'int'
					});
				});
			}
			else
			{
				fld.name = gby[1] + '_' + gby[0];
				fld.type = 'auto';
				fields.push(fld);
			}
		});

		store = Ext.create('Ext.data.Store', {
			fields: fields,
			autoLoad: true,
			proxy: {
				type: 'direct',
				directFn: report_api,
				reader: {
					type: 'json',
					messageProperty: 'message',
					rootProperty: 'records',
					successProperty: 'success',
					totalProperty: 'total'
				}
			},
			listeners: {
				beforeload: function(st, op)
				{
					var grid = me.grid,
						grid_store = grid.getStore(),
						grid_proxy = grid_store.getProxy(),
						op_params = op.getParams(),
						op_aggregates = [],
						op_groupby = [],
						grid_params, tmp_oper;

					tmp_oper = new Ext.data.operation.Read(grid_store.lastOptions);
					grid_params = grid_proxy.getParams(tmp_oper);
					if(grid_store.lastExtraParams)
						Ext.apply(grid_params, grid_store.lastExtraParams);

					op_params = Ext.copyTo(op_params || {}, grid_params, ['__filter', '__ffilter', '__xfilter', '__sstr']);

					Ext.Array.forEach(me.usedValues, function(aggr)
					{
						if(typeof(aggr) === 'undefined')
							return;
						op_aggregates.push(aggr);
					});
					Ext.Array.forEach(me.usedGroupBy, function(gby)
					{
						if(typeof(gby) === 'undefined')
							return;
						if(typeof(gby) === 'string')
						{
							op_groupby.push(gby);
							return;
						}

						if(gby[0] in me.groupBySubstitutes)
						{
							Ext.Array.forEach(me.groupBySubstitutes[gby[0]], function(gbsubst)
							{
								op_groupby.push([gbsubst, gby[1]]);
							});
						}
						else
						{
							op_groupby.push(gby);
						}
					});

					if(op_aggregates.length)
						op_params.__aggregates = op_aggregates;
					if(op_groupby.length)
						op_params.__groupby = op_groupby;

					op.setParams(op_params);

					return true;
				}
			}
		});

		return store;
	},
	getGraphXAxis: function()
	{
		var me = this,
			fields = [],
			cfg = {
				type: 'category',
				position: 'bottom'
			};

		Ext.Array.forEach(me.usedGroupBy, function(gby)
		{
			if(typeof(gby) === 'undefined')
				return;

			if(typeof(gby) === 'string')
			{
				fields.push(gby);
				return;
			}
			if(gby[0] in me.groupBySubstitutes)
			{
				Ext.Array.forEach(me.groupBySubstitutes[gby[0]], function(gbsubst)
				{
					fields.push(gby[1] + '_' + gbsubst);
				});
			}
			else
			{
				fields.push(gby[1] + '_' + gby[0]);
			}
		});
		if(fields.length)
			cfg.fields = fields;
		return cfg;
	},
	getGraphYAxis: function()
	{
		var cfg = {
			type: 'numeric',
			position: 'left'
		};

		return cfg;
	},
	getGraphSeries: function()
	{
		var me = this,
			y_fields = [],
			y_titles = [],
			cfg = {
				type: 'bar',
				stacked: false
			},
			top_gby;

		Ext.Array.forEach(me.usedValues, function(aggr)
		{
			y_fields.push(aggr[2]);
			y_titles.push(aggr[2]); // FIXME
		});

		if(y_fields.length)
			cfg.yField = y_fields;
		if(y_titles.length)
			cfg.title = y_titles;

		if(me.usedGroupBy.length)
		{
			top_gby = me.usedGroupBy[0];
			if(typeof(top_gby) === 'string')
				cfg.xField = top_gby;
		}

		return cfg;
	}
});

