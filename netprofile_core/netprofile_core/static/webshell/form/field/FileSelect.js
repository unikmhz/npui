/**
 * @class NetProfile.form.field.FileSelect
 * @extends Ext.form.field.Text
 */
Ext.define('NetProfile.form.field.FileSelect', {
	extend: 'Ext.form.field.Text',
	alias: 'widget.fileselect',
	requires: [
		'NetProfile.window.FileSelectWindow'
	],

	chooseText: 'Choose a file',

	config: {
		hiddenField: null,
		extraParams: null,
		editable: false,
		triggers: {
			clear: {
				cls: Ext.baseCSSPrefix + 'form-clear-trigger',
				weight: 1,
				hidden: true,
				handler: 'onTriggerClear'
			},
			select: {
				cls: Ext.baseCSSPrefix + 'form-folder-trigger',
				weight: 2,
				hidden: false,
				handler: 'onTriggerSelect'
			}
		}
	},

	initComponent: function()
	{
		if(this.allowBlank && !this.readOnly)
			this.getTrigger('clear').show();
		this.callParent(arguments);
	},
	initEvents: function()
	{
		var me = this;

		me.callParent(arguments);
		if(!me.editable)
			me.mon(me.inputEl, 'click', me.onTriggerSelect, me);
	},
	onTriggerClear: function()
	{
		var form = this.up('form'),
			hf = form.down('field[name=' + this.hiddenField + ']');
		if(hf)
			hf.setValue('');
		else
			form.getRecord().set(this.hiddenField, '');

		this.setValue('');
	},
	onTriggerSelect: function()
	{
		var me = this,
			picker = Ext.create('NetProfile.window.FileSelectWindow', {
				title: me.chooseText,
				onFileOpen: function(rec, ev)
				{
					if(!rec.get('allow_read'))
						return false;

					var form = me.up('form'),
						hf, xrec;

					if(form)
					{
						xrec = form.getRecord();
						if(me.hiddenField)
							hf = form.down('field[name=' + me.hiddenField + ']');
					}
					if(hf)
						hf.setValue(rec.getId());
					else if(xrec)
						xrec.set(me.hiddenField, rec.getId());

					me.setValue(rec.get('__str__'));
					this.up('window').close();
				}
			});

		picker.down('filebrowser').setFolder(null); // FIXME: select proper root folder
		picker.show();
	}
});

