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
	}
});

