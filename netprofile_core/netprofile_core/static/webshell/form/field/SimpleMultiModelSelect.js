/**
 * @class NetProfile.form.field.SimpleMultiModelSelect
 * @extends Ext.form.field.Tag
 */

Ext.define('NetProfile.form.field.SimpleMultiModelSelect', {
    values: [],
    extend: 'Ext.form.field.Tag',
    alias: 'widget.simplemultimodelselect',
    requires: [
    ],

    config: {
            apiModule: null,
            apiClass: null,
            hiddenField: null,
            extraParams: null,

            editable: false,
            multiField: true,
            valueField: '__str__',
            displayField: '__str__',
            selectOnFocus: false,

            showLink: false,
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
                            var uids = [];
                            for (var i = 0; i < recs.length; i++) {
                                    uids.push(recs[i].getId());
                            }
                            hf.setValue(uids);
                    }
            }, this);
    },
    getValue: function()
	{
		return this.values;
	},
	setValue: function(val)
	{
		var me = this;

		if(!Ext.isArray(val))
			val = [ val ];
		me.values = [];
		Ext.Array.forEach(val, function(v)
		{
			me.values.push(v.getId());
		});
	},
});
