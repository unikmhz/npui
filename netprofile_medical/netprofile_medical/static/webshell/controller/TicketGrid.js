/**
 * @class NetProfile.medical.controller.TicketGrid
 * @extends Ext.app.Controller
 */
Ext.define('NetProfile.medical.controller.TicketGrid', {
	extend: 'Ext.app.Controller',
	requires: [
		'Ext.menu.Menu'
	],

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
						text: 'Add Test',
						tooltip: { text: 'Add medical test', title: 'Add Test' },
						iconCls: 'ico-add',
						handler: function()
						{
							grid.spawnWizard('medtest');
						}
					});
				}
			}
		});
	}
});

