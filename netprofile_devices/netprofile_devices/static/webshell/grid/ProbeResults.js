/**
 * @class NetProfile.devices.grid.ProbeResults
 * @extends Ext.grid.Panel
 */
Ext.define('NetProfile.devices.grid.ProbeResults', {
	extend: 'Ext.grid.Panel',
	alias: 'widget.proberesults',
	requires: [
		'Ext.String',
		'Ext.grid.*',
		'NetProfile.devices.data.ProbeResultsStore'
	],

	config: {
		border: 0
	},

	okText: 'OK',
	partialText: 'Packet Loss',
	noneText: 'Unreachable',
	firewallText: 'Firewall',

	hostText: 'Host',
	addressText: 'Address',
	stateText: 'State',
	detailsText: 'Details',

	initComponent: function()
	{
		var me = this;

		me.columns = [{
			dataIndex: 'host',
			name: 'host',
			header: me.hostText,
			flex: 2,
			sortable: true
		}, {
			dataIndex: 'addr',
			name: 'addr',
			header: me.addressText,
			flex: 2,
			sortable: true
		}, {
			name: 'state',
			header: me.stateText,
			renderer: 'renderState',
			scope: me,
			flex: 2
		}, {
			name: 'details',
			header: me.detailsText,
			flex: 3
		}];

		me.callParent();
	},
	renderState: function(value, meta, rec, rowidx, colidx, store, view)
	{
		var me = this,
			detected = rec.get('detected'),
			sent = rec.get('sent'),
			returned = rec.get('returned'),
			state_text, state_icon;

		if(!detected)
		{
			state_text = me.noneText;
			state_icon = 'error';
		}
		else if(returned === sent)
		{
			state_text = me.okText;
			state_icon = 'ok';
		}
		else if(returned === 0)
		{
			state_text = me.firewallText;
			state_icon = 'info';
		}
		else
		{
			state_text = me.partialText;
			state_icon = 'warning';
		}

		return Ext.String.format(
			'<img class="np-cap-icon" src="{0}/static/devices/img/probe_{1}.png" alt="{2}" title="{2}" />{2}',
			NetProfile.staticURL, state_icon, state_text
		);
	}
});

