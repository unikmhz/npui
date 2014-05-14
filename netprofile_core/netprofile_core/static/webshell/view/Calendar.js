/**
 * @class NetProfile.view.Calendar
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
        useNull: true
    },
    Duration: {
        name:         'Duration',
        mapping:      'duration',
        defaultValue: -1,
        useNull:      true,
        type:         'int'
    },
    OriginalEventId: {
        name:    'OriginalEventId',
        mapping: 'origid',
        type:    'string',
        useNull: true
    },
    RSeriesStartDate: {
        name:       'RSeriesStartDate',
        mapping:    'rsstart',
        type:       'date',
        dateFormat: 'c',
        useNull:    true
    },
    RInstanceStartDate: {
        name:       'RInstanceStartDate',
        mapping:    'ristart',
        type:       'date',
        dateFormat: 'c',
        useNull:    true
    },
    REditMode: {
        name:    'REditMode',
        mapping: 'redit',
        type:    'string',
        useNull: true
    },
	APIModule: {
		name:    'APIModule',
		mapping: 'apim',
		type:    'string',
		useNull: true
	},
	APIClass: {
		name:    'APIClass',
		mapping: 'apic',
		type:    'string',
		useNull: true
	},
	APIId: {
		name:    'APIId',
		mapping: 'apiid',
		type:    'int',
		useNull: true
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

Ext.define('NetProfile.override.Extensible.calendar.view.AbstractCalendar', {
	override: 'Extensible.calendar.view.AbstractCalendar',
	showEventEditor: function(rec, animateTarget)
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
					null, true, true
				);
				if(!store)
					return;
				ff = { __ffilter: {} };
				ff.__ffilter[store.model.prototype.idProperty] = { eq: parseInt(id) };
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
				return;
			}
		}
		this.callParent(arguments);
	}
});

Ext.define('NetProfile.view.Calendar', {
	extend: 'Extensible.calendar.CalendarPanel',
	alias: 'widget.calendar',
	requires: [
		'Extensible.calendar.data.EventStore',
		'Extensible.calendar.data.MemoryCalendarStore'
	],
	border: 0,
	initComponent: function()
	{
		var tbar;

		if(!this.calendarStore)
			this.calendarStore = Ext.create('Extensible.calendar.data.MemoryCalendarStore', {
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
						root: 'calendars',
						messageProperty: 'message',
						successProperty: 'success',
						totalProperty: 'total'
					}
				}
			});
		if(!this.eventStore)
			this.eventStore = Ext.create('Extensible.calendar.data.EventStore', {
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
						root: 'evts',
						messageProperty: 'message',
						successProperty: 'success',
						totalProperty: 'total'
					}
				}
			});
		this.callParent();

		tbar = this.getDockedItems('toolbar[dock="top"]');
		if(tbar && tbar.length)
		{
			tbar = tbar[0];
			tbar.insert(0, {
				xtype: 'extensible.calendarcombo',
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
							root: 'calendars',
							messageProperty: 'message',
							successProperty: 'success',
							totalProperty: 'total'
						}
					}
				}),
				getListItemTpl: function(displayField) {
					return '<div class="x-combo-list-item x-cal-{' + Extensible.calendar.data.CalendarMappings.ColorId.name +
						'}"><div class="x-combo-check" style="float: left; width: 20px; margin: 1px 0;">&nbsp;</div><div class="ext-cal-picker-icon">&#160;</div>{' + displayField + '}</div>';
				}
			});
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
		'Extensible.calendar.util.ColorPicker'
	],
	alias: 'widget.calendarcolor',

	readOnly: false,
	value: null,

//	layout: 'fit',

	initComponent: function()
	{
		var me = this;

		if(me.readOnly)
			me.items = []; // TODO: implement read-only view
		else
			me.items = [{
				xtype: 'extensible.calendarcolorpicker',
				itemId: 'picker',
				value: me.value,
//				style: {
//					height: 'auto'
//				},
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
	getValue: function()
	{
		return this.getComponent('picker').getValue();
	},
	setValue: function(val)
	{
		return this.getComponent('picker').select(val);
	},
	isValid: function()
	{
		return true;
	}
});

