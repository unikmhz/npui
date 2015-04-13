/**
 * @class NetProfile.tickets.panel.Scheduler
 * @extends Ext.panel.Panel
 */
Ext.define('NetProfile.tickets.panel.Scheduler', {
	extend: 'Ext.panel.Panel',
	alias: 'widget.scheduler',
	requires: [
		'Ext.form.field.Number',
		// + combo
		'Ext.picker.Date',
		'Ext.menu.Menu'
	],

	layout: {
		type: 'hbox',
		align: 'stretch'
	},
	border: 0,

	userId: null,
	groupId: null,
	ticketId: null,
	ticketStateId: null,
	schedulerId: null,
	templateId: null,

	dateField: null,

	getParams: function()
	{
		var p = {},
			numfld = this.down('#numdates'),
			xtsfld = this.down('#xtschedid');
		if(this.userId)
			p.uid = this.userId;
		if(this.groupId)
			p.gid = this.groupId;
		if(this.ticketId)
			p.ticketid = this.ticketId;
		if(this.ticketStateId)
			p.tstid = this.ticketStateId;
		if(this.schedulerId)
			p.tschedid = this.schedulerId;
		if(this.templateId)
			p.ttplid = this.templateId;
		if(numfld)
			p.numdates = numfld.getValue();
		if(xtsfld)
			p.xtschedid = xtsfld.getValue();
		return p;
	},
	onLoadDates: function(data, res)
	{
		if(!data || !data.success)
			return;
		var menu = this.getComponent('sched_list'),
			i, dt, item;
		Ext.destroy(menu.removeAll());
		for(i in data.dates)
		{
			dt = Ext.Date.parse(data.dates[i], 'c', true);
			if(dt)
			{
				item = menu.add({
					// FIXME: customizable formats
					text: Ext.Date.format(dt, 'Y.m.d H:i:s')
				});
				item.value = dt;
			}
		}
	},
	initComponent: function()
	{
		var sched_store = NetProfile.StoreManager.getStore(
			'tickets',
			'TicketScheduler',
			null, true
		);
		this.items = [{
			xtype: 'datepicker',
			minDate: new Date(),
			handler: function(picker, date)
			{
				var param = this.getParams();
				param['date'] = date;
				NetProfile.api.Ticket.schedule_date(param, this.onLoadDates, this);
			},
			scope: this
		}, {
			tbar: [{
				xtype: 'combo',
				itemId: 'xtschedid',
				name: 'xtschedid',
				store: sched_store,
				displayField: 'name',
				valueField: 'tschedid'
			}, '->', {
				xtype: 'numberfield',
				itemId: 'numdates',
				name: 'numdates',
				value: 5,
				minValue: 1,
				maxValue: 20,
				width: 40
			}],
			flex: 1,
			border: 0,
//			plain: true,
			xtype: 'menu',
			floating: false,
			overflowY: 'auto',
			itemId: 'sched_list',
			listeners: {
				click: function(menu, item, ev)
				{
					if(item && item.value && this.dateField)
					{
						this.dateField.setValue(item.value);
						this.up('window').close();
					}
				},
				scope: this
			},
			items: []
		}];

		this.callParent();
	}
});

