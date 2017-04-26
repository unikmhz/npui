/**
 * @class NetProfile.data.PropertyTreeModel
 * @extends Ext.data.TreeModel
 */
Ext.define('NetProfile.data.PropertyTreeModel', {
	extend: 'Ext.data.TreeModel',
	fields: [{
		name: 'name',
		type: 'string',
		allowNull: true,
		allowBlank: true
	}, {
		name: 'type',
		type: 'string',
		allowNull: false,
		allowBlank: false
	}, {
		name: 'value',
		type: 'auto',
		allowNull: true,
		allowBlank: true
	}],

	getJSValue: function()
	{
		var me = this,
			type = me.get('type'),
			ret;

		switch(type)
		{
			case 'null':
				return null;
			case 'object':
			case 'dict':
				ret = {};
				me.eachChild(function(cn)
				{
					var name = cn.get('name');
					if(name)
						ret[name] = cn.getJSValue();
				});
				return ret;
			case 'array':
			case 'list':
				ret = [];
				me.eachChild(function(cn)
				{
					ret.push(cn.getJSValue());
				});
				return ret;
			case 'int':
			case 'integer':
				return parseInt(me.get('value'));
			case 'float':
			case 'double':
				return parseFloat(me.get('value'));
			default:
				break;
		}

		return me.get('value');
	},
	setJSValue: function(val)
	{
		var me = this,
			type = typeof val,
			child, idx;

		me.removeAll(true);
		if((val === null) || (type === 'undefined'))
			type = 'null';
		else if(type === 'object')
		{
			if(Ext.isArray(val))
				type = 'array';
		}
		else if(type === 'number')
		{
			if(val === parseInt(val, 10))
				type = 'int';
			else
				type = 'float';
		}
		else if(type === 'boolean')
			type = 'bool';

		me.set('type', type);
		switch(type)
		{
			case 'object':
				me.expand();
				Ext.Object.each(val, function(ok, ov)
				{
					child = new NetProfile.data.PropertyTreeModel({
						name: ok
					});
					me.appendChild(child);
					child.setJSValue(ov);
				});
				break;
			case 'array':
				me.expand();
				for(idx = 0; idx < val.length; idx++)
				{
					child = new NetProfile.data.PropertyTreeModel();
					me.appendChild(child);
					child.setJSValue(val[idx]);
				}
				break;
			default:
				me.set('value', val);
				break;
		}
	},
	isLeaf: function()
	{
		return !Ext.Array.contains(['object', 'array'], this.get('type'));
	}
});

