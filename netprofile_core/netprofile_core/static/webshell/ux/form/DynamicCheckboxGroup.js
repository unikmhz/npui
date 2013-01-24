Ext.define('Ext.ux.form.DynamicCheckboxGroup', {
	extend: 'Ext.form.CheckboxGroup',
	alias: 'widget.dyncheckboxgroup',
	requires: [
	],
	store: null,
	valueField: null,
	displayField: null,

	onRender: function(p, idx)
	{
		this.callParent();
		if(this.store && this.valueField)
		{
			if(!this.displayField)
				this.displayField = '__str__';
			if(this.store.isLoading())
				this.store.on({
					load: this.onLoad,
					prefetch: this.onLoad,
					scope: this
				});
			else
			{
				this.suspendLayouts();
				this.store.each(function(rec)
				{
					this.addCheckbox(
						rec.get(this.valueField),
						rec.get(this.displayField)
					);
				}, this);
				this.resumeLayouts(true);
			}
		}
	},
	addCheckbox: function(k, v)
	{
		this.add({
			name: this.name,
			boxLabel: v,
			inputValue: k
		});
	},
	onLoad: function(store, recs, ok)
	{
		var len, i;

		this.suspendLayouts();
		for(i = 0, len = recs.length; i < len; i++)
		{
			this.addCheckbox(
				recs[i].get(this.valueField),
				recs[i].get(this.displayField)
			);
		}
		this.resumeLayouts(true);
	}
});

