/**
 * @class NetProfile.panel.Calendar
 * @extends Extensible.calendar.CalendarPanel
 */

Extensible.calendar.data.CalendarMappings = {
    CalendarId: {
        name:    'CalendarId',
        mapping: 'id',
        type:    'string'
    },
    Title: {
        name:    'Title',
        mapping: 'title',
        type:    'string'
    },
    Description: {
        name:    'Description',
        mapping: 'desc',
        type:    'string'
    },
    Owner: {
        name:    'Owner',
        mapping: 'owner',
        type:    'string'
    },
    ColorId: {
        name:    'ColorId',
        mapping: 'color',
        type:    'int'
    },
    IsHidden: {
        name:    'IsHidden',
        mapping: 'hidden',
        type:    'boolean'
    },
	AllowCreation: {
		name:         'AllowCreation',
		mapping:      'cancreate',
		type:         'boolean',
        defaultValue: true
	}
};
Extensible.calendar.data.CalendarModel.reconfigure();

Extensible.calendar.data.EventMappings = {
    EventId: {
        name:    'EventId',
        mapping: 'id',
        type:    'string'
    },
    CalendarId: {
        name:    'CalendarId',
        mapping: 'cid',
        type:    'string'
    },
    Title: {
        name:    'Title',
        mapping: 'title',
        type:    'string'
    },
    StartDate: {
        name:       'StartDate',
        mapping:    'start',
        type:       'date',
        dateFormat: 'c'
    },
    EndDate: {
        name:       'EndDate',
        mapping:    'end',
        type:       'date',
        dateFormat: 'c'
    },
    Location: {
        name:    'Location',
        mapping: 'loc',
        type:    'string'
    },
    Notes: {
        name:    'Notes',
        mapping: 'notes',
        type:    'string'
    },
    Url: {
        name:    'Url',
        mapping: 'url',
        type:    'string'
    },
    IsAllDay: {
        name:    'IsAllDay',
        mapping: 'ad',
        type:    'boolean'
    },
    Reminder: {
        name:    'Reminder',
        mapping: 'rem',
        type:    'string'
    },
    RRule: {
        name:    'RRule',
        mapping: 'rrule',
        type:    'string',
        allowNull: true
    },
    Duration: {
        name:         'Duration',
        mapping:      'duration',
        defaultValue: -1,
        allowNull:      true,
        type:         'int'
    },
    OriginalEventId: {
        name:    'OriginalEventId',
        mapping: 'origid',
        type:    'string',
        allowNull: true
    },
    RSeriesStartDate: {
        name:       'RSeriesStartDate',
        mapping:    'rsstart',
        type:       'date',
        dateFormat: 'c',
        allowNull:    true
    },
    RInstanceStartDate: {
        name:       'RInstanceStartDate',
        mapping:    'ristart',
        type:       'date',
        dateFormat: 'c',
        allowNull:    true
    },
    REditMode: {
        name:    'REditMode',
        mapping: 'redit',
        type:    'string',
        allowNull: true
    },
	APIModule: {
		name:    'APIModule',
		mapping: 'apim',
		type:    'string',
		allowNull: true
	},
	APIClass: {
		name:    'APIClass',
		mapping: 'apic',
		type:    'string',
		allowNull: true
	},
	APIId: {
		name:    'APIId',
		mapping: 'apiid',
		type:    'int',
		allowNull: true
	},
	CanEditText: {
		name:    'CanEditText',
		mapping: 'caned',
		type:    'boolean'
	}
};
Extensible.calendar.data.EventModel.reconfigure();

Ext.define('NetProfile.override.Extensible.calendar.form.field.CalendarCombo', {
	override: 'Extensible.calendar.form.field.CalendarCombo',
	showAllCalendars: false,
	initComponent: function()
	{
		if(this.showAllCalendars)
			this.store.clearFilter();
		else
		{
			this.store.filter({ filterFn: function(rec)
			{
				return rec.get('AllowCreation');
			}});
		}

		return this.callParent(arguments);
	}
});

Ext.define('NetProfile.panel.Calendar', {
	extend: 'Extensible.calendar.CalendarPanel',
	alias: 'widget.calendar',
	requires: [
		'Extensible.calendar.data.EventStore',
		'Extensible.calendar.data.MemoryCalendarStore'
	],
	border: 0,
	initComponent: function()
	{
		var me = this,
			tbar, cmp;

		if(!me.calendarStore)
			me.calendarStore = Ext.create('Extensible.calendar.data.MemoryCalendarStore', {
				proxy: {
					type: 'direct',
					api: {
						create:  Ext.emptyFn,
						read:    NetProfile.api.Calendar.cal_read,
						update:  Ext.emptyFn,
						destroy: Ext.emptyFn
					},
					reader: {
						type: 'json',
						rootProperty: 'calendars',
						messageProperty: 'message',
						successProperty: 'success',
						totalProperty: 'total'
					}
				}
			});
		if(!me.store)
			me.store = Ext.create('Extensible.calendar.data.EventStore', {
				autoLoad: true,
				proxy: {
					type: 'direct',
					api: {
						create:  NetProfile.api.Calendar.evt_create,
						read:    NetProfile.api.Calendar.evt_read,
						update:  NetProfile.api.Calendar.evt_update,
						destroy: NetProfile.api.Calendar.evt_delete
					},
					reader: {
						type: 'json',
						rootProperty: 'evts',
						messageProperty: 'message',
						successProperty: 'success',
						totalProperty: 'total'
					}
				}
			});
		me.callParent();

		tbar = me.getDockedItems('toolbar[dock="top"]');
		if(tbar && tbar.length)
		{
			tbar = tbar[0];
			tbar.insert(0, {
				xtype: 'extensible.calendarcombo',
				itemId: 'cals',
				multiSelect: true,
				fieldLabel: null,
				showAllCalendars: true,
				store: Ext.create('Extensible.calendar.data.MemoryCalendarStore', {
					proxy: {
						type: 'direct',
						api: {
							create:  Ext.emptyFn,
							read:    NetProfile.api.Calendar.cal_read,
							update:  Ext.emptyFn,
							destroy: Ext.emptyFn
						},
						reader: {
							type: 'json',
							rootProperty: 'calendars',
							messageProperty: 'message',
							successProperty: 'success',
							totalProperty: 'total'
						}
					}
				})
			});
		}

		me.mon(me.store, 'beforeload', me.onBeforeLoad, me);
		me.on({
			eventclick: function(cal, rec, el)
			{
				if(rec instanceof Extensible.calendar.data.EventModel)
				{
					var mod = rec.get('APIModule'),
						cls = rec.get('APIClass'),
						id = rec.get('APIId'),
						ff, store;

					if(mod && cls && id)
					{
						store = NetProfile.StoreManager.getStore(
							mod, cls,
							null, true
						);
						if(!store)
							return false;
						ff = { __ffilter: [{
							property: store.model.prototype.idProperty,
							operator: 'eq',
							value:    parseInt(id)
						}] };
						store.load({
							params: ff,
							callback: function(recs, op, success)
							{
								var dp, pb, poly, apim, apic;

								poly = recs[0].get('__poly');
								if(poly)
								{
									apim = poly[0];
									apic = poly[1];
								}
								else
								{
									apim = mod;
									apic = cls;
								}

								pb = Ext.getCmp('npws_propbar');
								dp = NetProfile.view.grid[apim][apic].prototype.detailPane;
								if(success && pb && dp)
								{
									pb.addRecordTab(apim, apic, dp, recs[0]);
									pb.show();
								}
							},
							scope: this,
							synchronous: false
						});
						return false;
					}
				}
				return true;
			},
			viewchange: function(cal, view, info)
			{
				var jump_id = cal.id + '-tb-jump-dt',
					jump = Ext.getCmp(jump_id);

				if(cal.showNavJump && jump && info.activeDate)
					jump.setValue(info.activeDate);
			},
			scope: me
		});
	},
	onBeforeLoad: function(store, oper)
	{
		var me = this,
			tbar = me.getDockedItems('toolbar[dock="top"]'),
			cals = null,
			params;

		if(tbar && tbar.length)
		{
			tbar = tbar[0];
			cals = tbar.getComponent('cals');
			if(cals)
				cals = cals.getValue();
		}
		if(cals && cals.length)
		{
			params = oper.getParams() || {};
			params.cals = cals;
			oper.setParams(params);
		}
	}
});

/**
 * @class Ext.ux.form.field.CalendarColor
 * @extends Ext.form.FieldContainer
 */
Ext.define('Ext.ux.form.field.CalendarColor', {
	extend: 'Ext.form.FieldContainer',
	mixins: {
		field: 'Ext.form.field.Field'
	},
	requires: [
		'Ext.picker.Color'
	],
	alias: 'widget.calendarcolor',

	readOnly: false,
	value: null,

	colorMap: [
		'FA7166',
		'CF2424',
		'A01A1A',
		'7E3838',
		'CA7609',
		'F88015',
		'EDA12A',
		'D5B816',
		'E281CA',
		'BF53A4',
		'9D3283',
		'7A0F60',
		'542382',
		'7742A9',
		'8763CA',
		'B586E2',
		'7399F9',
		'4E79E6',
		'2951B9',
		'133897',
		'1A5173',
		'1A699C',
		'3694B7',
		'64B9D9',
		'A8C67B',
		'83AD47',
		'2E8F0C',
		'176413',
		'0F4C30',
		'386651',
		'3EA987',
		'7BC3B5'
	],

	initComponent: function()
	{
		var me = this;

		if(me.readOnly)
			me.items = []; // TODO: implement read-only view
		else
			me.items = [{
				xtype: 'colorpicker',
				itemId: 'picker',
				colors: me.colorMap,
				value: me.indexToColor(me.value),
				listeners: {
					select: function(fld, newval)
					{
						this.fireEvent('change', me, me.getValue());
					},
					scope: me
				}
			}];
		me.callParent(arguments);
	},
	indexToColor: function(idx)
	{
		if(typeof(idx) !== 'number')
			return null;
		if(idx <= 0)
			return null;
		if(idx > this.colorMap.length)
			return null;
		return this.colorMap[idx - 1];
	},
	colorToIndex: function(col)
	{
		if(typeof(col) !== 'string')
			return null;
		var idx = this.colorMap.indexOf(col.toUpperCase());
		if(idx === -1)
			return null;
		return (idx + 1);
	},
	getValue: function()
	{
		return this.colorToIndex(this.getComponent('picker').getValue());
	},
	setValue: function(val)
	{
		return this.getComponent('picker').select(this.indexToColor(val));
	},
	isValid: function()
	{
		return true;
	}
});

