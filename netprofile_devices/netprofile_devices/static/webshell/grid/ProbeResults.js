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

	hostUnreachableText: 'Host unreachable',
	behindFirewallText: 'Host is behind a firewall',
	hostDetailsTpl: '{0}/{1} min.:{2} avg.:{3} max.:{4}',

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
			flex: 2,
			allowMarkup: true
		}, {
			name: 'details',
			header: me.detailsText,
			renderer: 'renderDetails',
			scope: me,
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
	},
	renderDetails: function(value, meta, rec, rowidx, colidx, store, view)
	{
		var me = this,
			detected = rec.get('detected'),
			sent = parseInt(rec.get('sent')),
			returned = parseInt(rec.get('returned')),
			min = rec.get('min'),
			max = rec.get('max'),
			avg = rec.get('avg');

		if(!detected)
			return me.hostUnreachableText;
		if((returned === 0) && (returned !== sent))
			return me.behindFirewallText;

		return Ext.String.format(
			me.hostDetailsTpl,
			returned, sent,
			Ext.util.Format.number(min, '0.00#'),
			Ext.util.Format.number(avg, '0.00#'),
			Ext.util.Format.number(max, '0.00#')
		);
	}
});

