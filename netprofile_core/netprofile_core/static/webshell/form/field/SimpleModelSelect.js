/**
 * @class NetProfile.form.field.SimpleModelSelect
 * @extends Ext.form.field.ComboBox
 */
Ext.define('NetProfile.form.field.SimpleModelSelect', {
	extend: 'Ext.form.field.ComboBox',
	alias: 'widget.simplemodelselect',
	requires: [
	],

	config: {
		apiModule: null,
		apiClass: null,
		hiddenField: null,
		extraParams: null,

		editable: false,
		valueField: '__str__',
		displayField: '__str__',

		showLink: false,
		triggers: {
			clear: {
				cls: Ext.baseCSSPrefix + 'form-clear-trigger',
				weight: -1,
				hidden: true,
				handler: 'onTriggerClear'
			}
		}
	},

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
		if(this.allowBlank && !this.readOnly)
			this.getTrigger('clear').show();
		this.callParent(arguments);

		this.on('select', function(cbox, recs, opt)
		{
			if(!this.hiddenField)
				return;
			var form = this.up('form'),
				hf = form.down('field[name=' + this.hiddenField + ']');

			if(!hf)
				return;
			if(recs)
			{
				if(recs.length)
					recs = recs[0];
				hf.setValue(recs.getId());
			}
		}, this);
	},
	onTriggerClear: function()
	{
		if(this.hiddenField)
		{
			var form = this.up('form'),
				hf = form.down('field[name=' + this.hiddenField + ']');

			if(hf)
				hf.setValue(null);
		}
		this.setValue('');
	}
});

