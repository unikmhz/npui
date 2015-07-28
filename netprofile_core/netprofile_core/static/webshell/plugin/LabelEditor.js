/**
 * @class NetProfile.plugin.LabelEditor
 * @extends Ext.Editor
 */
Ext.define('NetProfile.plugin.LabelEditor', {
	extend: 'Ext.Editor',
	mixins: {
		plugin: 'Ext.plugin.Abstract'
	},
	requires: [
		'Ext.form.field.Text'
	],
	alias: 'plugin.labeleditor',
	pluginId: 'labeleditor',

	alignment: 'tl-tl',
	completeOnEnter: true,
	cancelOnEsc: true,
	shim: false,
	autoSize: {
		width: 'boundEl',
		height: 'field'
	},
	labelSelector: 'x-editable',

	constructor: function(config)
	{
		config.field = config.field || Ext.create('Ext.form.field.Text', {
			allowBlank: false,
			allowOnlyWhitespace: false,
			selectOnFocus:true
		});
		this.callParent([config]);
	},
	init: function(view)
	{
		var me = this;

		me.view = view;
		me.viewListeners = view.on({
			scope: me,
			destroyable: true,
			beforeitemmousedown: me.onItemMouseDown
		});
		me.on('complete', me.onSave, me);

		view.relayEvents(this, ['afteredit']);
	},
	destroy: function()
	{
		var me = this;

		if(me.activeRecord)
			delete me.activeRecord;
		Ext.destroyMembers(me, 'viewListeners');
	},
	recordFilter: Ext.emptyFn,
	onItemMouseDown: function(view, record, item, idx, ev)
	{
		var me = this;

		if(ev.button !== 0)
			return true;
		if(Ext.fly(ev.target).hasCls(me.labelSelector) && !me.editing && !ev.ctrlKey && !ev.shiftKey)
		{
			if(!view.getSelectionModel().isSelected(record))
				return true;
			if(me.recordFilter(record) === false)
				return true;
			ev.stopEvent();
			me.startEdit(ev.target, record.get(me.dataIndex));
			me.activeRecord = record;
			return false;
		}
		else if(me.editing)
		{
			me.field.blur();
			ev.preventDefault();
		}
	},
	onSave: function(ed, value)
	{
		this.activeRecord.set(this.dataIndex, value);
		this.fireEvent('afteredit', ed, this.activeRecord, value);
	}
});

