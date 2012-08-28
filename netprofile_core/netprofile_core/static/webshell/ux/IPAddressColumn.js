/**
 * @class Ext.ux.IPAddressColumn
 * @extends Ext.grid.column.Column
 */
Ext.define('Ext.ux.IPAddressColumn', {
    extend: 'Ext.grid.column.Column',
    alias: 'widget.ipaddrcolumn',

    renderer: function(value, meta, record, rowidx, colidx, store)
	{
		if(value)
	        return value.toString();
		return value;
    }
});
