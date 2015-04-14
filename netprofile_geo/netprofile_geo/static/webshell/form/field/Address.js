/**
 * @class NetProfile.geo.form.field.Address
 * @extends Ext.form.FieldContainer
 */
Ext.define('NetProfile.geo.form.field.Address', {
	extend: 'Ext.form.FieldContainer',
	mixins: {
		field: 'Ext.form.field.Field'
	},
	alias: 'widget.address',
	requires: [
		'Ext.form.field.ComboBox',
		'Ext.form.field.Hidden'
	],

	displayLabels: true,

	displayCity: true,
	displayDistrict: true,
	displayStreet: true,
	displayHouse: true,
	displayPlace: false,

	fixedCity: false,
	fixedDistrict: false,
	fixedStreet: false,
	fixedHouse: false,
	fixedPlace: false,

	selectedCity: null,
	selectedDistrict: null,
	selectedStreet: null,
	selectedHouse: null,
	selectedPlace: null,

	labelCity: 'City',
	labelDistrict: 'District',
	labelStreet: 'Street',
	labelHouse: 'House',
	labelPlace: 'Place',

	comboCfg: {
	},

	_keys: {
		City: 'cityid',
		District: 'districtid',
		Street: 'streetid',
		House: 'houseid',
		Place: 'placeid'
	},
	_deps: [ 'City', 'District', 'Street', 'House', 'Place' ],

	initComponent: function()
	{
		var me = this,
			cfg;

		me.stores = {};
		me.items = [];
		me._orig = {};

		if(me.value && Ext.isObject(me.value))
		{
			Ext.Array.forEach(me._deps, function(stype)
			{
				cfg = me._keys[stype];
				if(cfg in me.value)
					me['selected' + stype] = parseInt(me.value[cfg]);
			});
			me.storeOriginal();
			delete me.value;
		}
		Ext.Array.forEach(me._deps, function(stype)
		{
			cfg = null;
			if(me['display' + stype])
			{
				me.stores[stype] = me._getSelectStore(stype);
				cfg = {
					xtype: 'combobox',
					itemId: stype,
					name: me._keys[stype],
					displayField: '__str__',
					width: 300,
					labelAlign: 'right',
					valueField: me._keys[stype],
					store: me.stores[stype],
					autoSelect: false,
					tpl: new Ext.XTemplate('<tpl for="."><li style="min-height: 22px;" class="x-boundlist-item" role="option">{__str__}</li></tpl>'),
					value: me['selected' + stype],
					autoLoadOnValue: true,
					listeners: {
						beforeselect: function(cb, record, idx)
						{
							this.storeOriginal();
						},
						select: function(cb, record)
						{
							var sub, name;

							if(record)
							{
								name = record.get('__str__');
								if(name)
									this['selected' + stype] = record.getId();
								else
									this['selected' + stype] = null;
								sub = this._getNextType(stype);
								if(sub && this.stores[sub] && this.stores[sub].getCount())
									this.stores[sub].reload();
								else
									this.compareOriginal();
							}
						},
						scope: me
					}
				};
				if(me.displayLabels)
					cfg['fieldLabel'] = me['label' + stype];
			}
			else if(me['fixed' + stype])
			{
				cfg = {
					xtype: 'hidden',
					itemId: stype,
					name: me._keys[stype],
					value: me['selected' + stype]
				};
			}
			if(cfg)
				me.items.push(cfg);
		});

		me.callParent();
	},
	getSubValue: function(stype)
	{
		return this['selected' + stype];
	},
	setSubValue: function(stype, value)
	{
		var cb;

		value = parseInt(value);
		if(value <= 0)
			return;
		this['selected' + stype] = value;
		cb = this.getComponent(stype);
		if(cb)
		{
			cb.setValue(value);
			if(this.stores[stype] && !this.stores[stype].getCount())
				this.stores[stype].reload();
		}
	},
	clearSubValue: function(stype)
	{
		var me = this,
			oldval = me['selected' + stype],
			sub = me._getNextType(stype),
			cb;

		me['selected' + stype] = null;
		cb = me.getComponent(stype);
		if(cb)
		{
			cb.setValue(null);
			if((oldval !== null) && sub && me.stores[sub] && me.stores[sub].getCount())
				me.stores[sub].reload();
		}
	},
	_getSubValuesBefore: function(stype)
	{
		var ret = {},
			pos, cur, val;

		pos = Ext.Array.indexOf(this._deps, stype);
		if(pos == -1)
			return {};
		for(cur = 0; cur < pos; cur++)
		{
			val = this.getSubValue(this._deps[cur]);
			if(val)
				ret[this._keys[this._deps[cur]]] = val;
		}
		return ret;
	},
	_getFiltersBefore: function(stype)
	{
		var ret = [];

		Ext.Object.each(this._getSubValuesBefore(stype), function(k, v)
		{
			ret.push({
				property: k,
				operator: 'eq',
				value:    v
			});
		});
		return ret;
	},
	_getNextType: function(stype)
	{
		var pos;

		pos = Ext.Array.indexOf(this._deps, stype);
		if((pos < 0) || (pos >= (this._deps.length - 1)))
			return null;
		return this._deps[pos + 1];
	},
	_getNextTypes: function(stype)
	{
		var pos;

		pos = Ext.Array.indexOf(this._deps, stype);
		if((pos < 0) || (pos >= (this._deps.length - 1)))
			return {};
		return Ext.Array.slice(this._deps, pos + 1);
	},
	_getSelectStore: function(stype)
	{
		return Ext.create('NetProfile.store.geo.' + stype, {
			buffered: false,
			autoLoad: false,
			pageSize: -1,
			listeners: {
				beforeload: function(st, oper)
				{
					var params = oper.getParams() || {};

					params.__ffilter = this._getFiltersBefore(stype);
					params.__empty = true;
					oper.setParams(params);
				},
				load: function(st, recs, succ)
				{
					var recid = null,
						cb, cbval;

					if(!succ)
						return;
					cb = this.getComponent(stype);
					if(cb)
						cbval = cb.getValue();
					else
						cbval = this['selected' + stype];
					cbval = parseInt(cbval);
					if(cbval)
					{
						Ext.Array.forEach(recs, function(rec)
						{
							if(rec.getId() === cbval)
								recid = rec.getId();
						});
					}
					if((recid === null) || (recid !== cbval))
					{
						this['selected' + stype] = null;
						if(cb)
							cb.clearValue();
						recid = this._getNextType(stype);
						if(recid && this.stores[recid] && this.stores[recid].getCount())
							this.stores[recid].reload();
						else
							this.compareOriginal();
					}
				},
				scope: this
			}
		});
	},
	getName: function()
	{
		return this.name;
	},
	setRawValue: function(raw)
	{
		var me = this,
			key;

		if(!Ext.isObject(raw))
			raw = {};
		Ext.Array.forEach(me._deps, function(stype)
		{
			key = me._keys[stype];
			if(key in raw)
				me.setSubValue(stype, raw[key]);
			else
				me.clearSubValue(stype);
		});
	},
	setValue: function(val)
	{
		this.storeOriginal();
		this.setRawValue(val);
		this.compareOriginal();
	},
	getFlatValue: function()
	{
		var me = this,
			ret = {},
			val = null,
			notnull = false;

		Ext.Array.forEach(me._deps, function(stype)
		{
			val = me.getSubValue(stype);
			if(val !== null)
			{
				notnull = true;
				ret[me._keys[stype]] = val;
			}
		});
		if(!notnull)
			return null;
		return ret;
	},
	storeOriginal: function()
	{
		this._orig = this.getFlatValue();
		if(this._orig === null)
			this._orig = {};
	},
	compareOriginal: function()
	{
		var me = this,
			cur = me.getFlatValue(),
			diff = false;

		if(cur === null)
			cur = {};
		diff = !Ext.Object.equals(cur, me._orig);
		me._orig = cur;
		if(diff)
			me.fireEvent('change', me, me.getValue());
	},
	getValue: function()
	{
		var ret = {},
			val;

		val = this.getFlatValue();
		if(!val)
			return {};
		ret[this.name] = val;
		return ret;
	}
});

