/**
 * @class NetProfile.tickets.controller.TicketGrid
 * @extends Ext.app.Controller
 */
Ext.define('NetProfile.tickets.controller.TicketGrid', {
	extend: 'Ext.app.Controller',
	requires: [
		'Ext.menu.Menu'
	],

	fromTemplateText: 'From Template',
	fromTemplateTipText: 'Add ticket from template',
	scheduleText: 'Schedule',

	init: function()
	{
		this.control({
			'grid_tickets_Ticket' : {
				beforerender: function(grid)
				{
					var tb;

					tb = grid.getDockedItems('toolbar[dock=top]');
					if(!tb || !tb.length)
						return;
					tb = tb[0];
					tb.add({
						text: this.fromTemplateText,
						tooltip: { text: this.fromTemplateTipText, title: this.fromTemplateText },
						iconCls: 'ico-add',
						handler: function()
						{
							grid.spawnWizard('tpl');
						}
					});
				}
			},
			'npwizard button#btn_sched' : {
				click: {
				scope: this, fn: function(btn, ev)
				{
					var wiz = btn.up('npwizard'),
						date_field = wiz.down('datetimefield[name=assigned_time]'),
						cfg = { dateField: date_field },
						win, sched, values;

					values = wiz.getValues();
					if(values['assigned_uid'])
						cfg.userId = parseInt(values['assigned_uid']);
					if(values['assigned_gid'])
						cfg.groupId = parseInt(values['assigned_gid']);
					if(values['ticketid'])
						cfg.ticketId = parseInt(values['ticketid']);
					if(values['tstid'])
						cfg.ticketStateId = parseInt(values['tstid']);
					if(values['tschedid'])
						cfg.schedulerId = parseInt(values['tschedid']);
					if(values['ttplid'])
						cfg.templateId = parseInt(values['ttplid']);
					win = Ext.create('Ext.ux.window.CenterWindow', {
						title: this.scheduleText,
						modal: true
					});
					sched = Ext.create('NetProfile.tickets.view.Scheduler', cfg);
					win.add(sched);
					win.show();

					return true;
				}}
			}
		});
	}
});

