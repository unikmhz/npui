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
		this.valueField = Extensible.calendar.data.CalendarMappings.CalendarId.name;
		this.displayField = Extensible.calendar.data.CalendarMappings.Title.name;

		this.listConfig = Ext.apply(this.listConfig || {}, {
			getInnerTpl: this.getListItemTpl
		});

		if(!this.showAllCalendars)
		{
			var old_store = this.store,
				new_store = this.calendarStore = Ext.create('Extensible.calendar.data.MemoryCalendarStore');

			Ext.each(old_store.getRange(), function(rec)
			{
				var new_data = Ext.clone(rec.copy().data),
					new_rec = new Extensible.calendar.data.EventModel(new_data, new_data.id);
				console.log('NEW_DATA', new_data);
				new_store.add(new_rec);
			});
			this.store = new_store;
		}
		this.store.on('update', this.refreshColorCls, this);

		return Ext.form.field.ComboBox.prototype.initComponent.apply(this, arguments);
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
						create:  Ext.emptyFn,
						read:    NetProfile.api.Calendar.evt_read,
						update:  NetProfile.api.Calendar.evt_update,
						destroy: Ext.emptyFn
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
	}
});

