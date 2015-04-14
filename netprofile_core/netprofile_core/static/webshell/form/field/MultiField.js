/**
 * @class NetProfile.form.field.MultiField
 * @extends Ext.form.FieldContainer
 */
Ext.define('NetProfile.form.field.MultiField', {
	extend: 'Ext.form.FieldContainer',
	mixins: {
		field: 'Ext.form.field.Field'
	},
	requires: [
		'NetProfile.form.field.MultiFieldItem'
	],
	alias: 'widget.multifield',

	templateCfg: {
	},

	readOnly: false,
	minSize: null,
	maxSize: null,

	layout: 'vbox',

	initComponent: function()
	{
		var me = this,
			i, cfg;

		me.items = [];
		if(!Ext.isArray(me.value))
			me.value = [ me.value ];
		for(i in me.value)
		{
			cfg = Ext.apply({
				value: me.value[i],
				flex: 1,
				listeners: {
					change: function(fld, newval)
					{
						this.fireEvent('change', me, me.getValue());
					},
					validitychange: function(fld, isvalid)
					{
						this.fireEvent('validitychange', me, me.isValid());
					},
					scope: me
				}
			}, me.templateCfg || {});
			cfg = {
				xtype: 'multifielditem',
				readOnly: me.readOnly,
				items: [ cfg ],
				showAdd: false,
				showRemove: true,
				listeners: {
					removeitem: function(it, ev)
					{
						var me = this,
							curlen = me.items.length;

						if(!me.readOnly && ((me.minSize === null) || (me.minSize < me.items.length)))
						{
							me.remove(it, true);
							if(me.maxSize === curlen)
								me.addFooter();
						}
					},
					scope: me
				}
			};
			me.items.push(cfg);
		}
		if(!me.readOnly && ((me.maxSize === null) || (me.maxSize > me.items.length)))
			me.items.push({
				xtype: 'multifielditem',
				readOnly: false,
				showUp: false,
				showDown: false,
				showAdd: true,
				showRemove: false,
				listeners: {
					additem: function(it, ev)
					{
						var me = this,
							curlen = me.items.length;

						if(!me.readOnly && ((me.maxSize === null) || (me.maxSize > curlen)))
						{
							me.addItem('', curlen);
							if((curlen + 1) === me.maxSize)
								me.remove(it, true);
						}
					},
					scope: me
				}
			});
		me.callParent(arguments);
	},
	addItem: function(val, idx)
	{
		var me = this,
			cfg;

		cfg = Ext.apply({
			value: val,
			flex: 1,
			listeners: {
				change: function(fld, newval)
				{
					this.fireEvent('change', me, me.getValue());
				},
				scope: me
			}
		}, me.templateCfg || {});
		cfg = {
			xtype: 'multifielditem',
			items: [cfg],
			listeners: {
				removeitem: function(it, ev)
				{
					var me = this,
						curlen = me.items.length;

					if(!me.readOnly && ((me.minSize === null) || (me.minSize < me.items.length)))
					{
						me.remove(it, true);
						if(me.maxSize === curlen)
							me.addFooter();
					}
				},
				scope: me
			}
		};
		if(typeof(idx) === 'number')
			return me.insert(idx, cfg);
		return me.add(cfg);
	},
	addFooter: function()
	{
		return this.add({
			xtype: 'multifielditem',
			readOnly: false,
			showUp: false,
			showDown: false,
			showAdd: true,
			showRemove: false,
			listeners: {
				additem: function(it, ev)
				{
					var me = this,
						curlen = me.items.length;

					if(!me.readOnly && ((me.maxSize === null) || (me.maxSize > curlen)))
					{
						me.addItem('', curlen - 1);
						if((curlen + 1) === me.maxSize)
							me.remove(it, true);
					}
				},
				scope: this
			}
		});
	},
	getValue: function()
	{
		var val = [], v;

		this.items.each(function(it)
		{
			if(it instanceof NetProfile.form.field.MultiFieldItem)
			{
				v = it.getValue();
				if((v !== null) && (v !== undefined))
					val.push(v);
			}
		});
		return val;
	},
	setValue: function(val)
	{
		var me = this;

		if(!Ext.isArray(val))
			val = [ val ];
		me.removeAll(true);
		Ext.Array.forEach(val, function(v, idx)
		{
			me.addItem(v);
		});
		if(!me.readOnly && ((me.maxSize === null) || (me.maxSize > me.items.length)))
			me.addFooter();
	},
	isValid: function()
	{
		var valid = true;

		this.items.each(function(it)
		{
			if(it instanceof NetProfile.form.field.MultiFieldItem)
			{
				if(!it.isValid())
					valid = false;
			}
		});
		return valid;
	}
});

