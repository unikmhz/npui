/**
 * @class NetProfile.grid.column.EnumColumn
 * @extends Ext.grid.column.Column
 */
Ext.define('NetProfile.grid.column.EnumColumn', {
    extend: 'Ext.grid.column.Column',
    alias: 'widget.enumcolumn',

    /**
     * @cfg {Object}
     */
	valueMap: {},

    renderer: function(value, meta, record, rowidx, colidx, store)
	{
		var vmap = this.columns[colidx].valueMap;

		if(value in vmap)
			return vmap[value];
        return value;
    }
});
