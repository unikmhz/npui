/**
 * @class NetProfile.form.field.ModelSelect
 * @extends Ext.form.field.Text
 */
Ext.define('NetProfile.form.field.ModelSelect', {
	extend: 'Ext.form.field.Text',
	alias: 'widget.modelselect',
	requires: [
		'NetProfile.window.CenterWindow'
	],

	chooseText: 'Choose an object',

	config: {
		apiModule: null,
		apiClass: null,
		hiddenField: null,
		gridConfig: null,
		extraParams: null,
		showLink: true,
		triggers: {
			clear: {
				cls: Ext.baseCSSPrefix + 'form-clear-trigger',
				weight: 1,
				hidden: true,
				handler: 'onTriggerClear'
			},
			select: {
				weight: 2,
				hidden: false,
				handler: 'onTriggerSelect'
			},
			link: {
				cls: Ext.baseCSSPrefix + 'form-search-trigger',
				weight: 3,
				hidden: true,
				hideOnReadOnly: false,
				disableOnReadOnly: false,
				handler: 'onTriggerLink'
			}
		}
	},

	initComponent: function()
	{
		if(this.allowBlank && !this.readOnly)
			this.getTrigger('clear').show();
		if(this.showLink)
			this.getTrigger('link').show();
		this.callParent(arguments);
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
		var sel_win = Ext.create('NetProfile.window.CenterWindow', {
//			animateTarget: this,
			title: this.chooseText
		});

		var sel_grid_class = 'NetProfile.view.grid.'
			+ this.apiModule
			+ '.'
			+ this.apiClass;
		var form = this.up('form'),
			hf = form.down('field[name=' + this.hiddenField + ']');
		if(!hf)
			hf = this.hiddenField;
		var sel_grid_cfg = Ext.apply({
//		var sel_grid = Ext.create(sel_grid_class, {
			rowEditing: false,
			actionCol: false,
			selectRow: true,
			selectField: this,
			selectIdField: hf,
			extraParams: this.extraParams,
			stateful: false
		}, this.gridConfig || {});
		var sel_grid = Ext.create(sel_grid_class, sel_grid_cfg);

		sel_win.add(sel_grid);
		sel_win.show();
	},
	onTriggerLink: function()
	{
		var ff,
			store = NetProfile.StoreManager.getStore(
				this.apiModule,
				this.apiClass,
				null, true
			),
			hf = this.up('form').down('field[name=' + this.hiddenField + ']');

		if(!store)
			return false;
		if(!hf)
			hf = this.hiddenField;
		if(!hf)
			return false;
		hf = hf.getValue();
		if(!hf)
			return false;
		ff = { __ffilter: [{
			property: store.model.prototype.idProperty,
			operator: 'eq',
			value:    parseInt(hf)
		}] };
		store.load({
			params: ff,
			callback: function(recs, op, success)
			{
				var dp, pb, poly, apim, apic;
				poly = recs[0].get('__poly');
				if(poly)
				{
					apim = poly[0];
					apic = poly[1];
				}
				else
				{
					apim = this.apiModule;
					apic = this.apiClass;
				}

				pb = this.up('propbar');
				dp = NetProfile.view.grid[apim][apic].prototype.detailPane;
				if(success && pb && dp)
					pb.addRecordTab(apim, apic, dp, recs[0]);
			},
			scope: this,
			synchronous: false
		});
		return true;
	}
});

