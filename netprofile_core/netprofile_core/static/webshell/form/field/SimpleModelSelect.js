/**
 * @class NetProfile.form.field.SimpleModelSelect
 * @extends Ext.form.field.ComboBox
 */
Ext.define('NetProfile.form.field.SimpleModelSelect', {
	extend: 'Ext.form.field.ComboBox',
	alias: 'widget.simplemodelselect',
	requires: [
	],
	apiModule: null,
	apiClass: null,
	hiddenField: null,
	extraParams: null,

	editable: false,
	valueField: '__str__',
	displayField: '__str__',

	initComponent: function()
	{
		if(!this.store)
		{
			this.store = NetProfile.StoreManager.getStore(
				this.apiModule,
				this.apiClass,
				null, true,
				this.extraParams
			);
		}
		this.callParent(arguments);

		this.on('select', function(cbox, recs, opt)
		{
			if(!this.hiddenField)
				return;
			var form = this.up('form'),
				hf = form.down('field[name=' + this.hiddenField + ']');

			if(!hf)
				return;
			if(recs && recs.length)
				hf.setValue(recs[0].getId());
		}, this);
	}
});

