/**
 * @class Ext.ux.EnumColumn
 * @extends Ext.grid.column.Column
 */
Ext.define('Ext.ux.EnumColumn', {
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
