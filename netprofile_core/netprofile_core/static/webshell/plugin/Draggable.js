/*
 * Based on Ext.ux.DataView.Draggable by Ed Spencer
 */
Ext.define('NetProfile.plugin.Draggable', {
	extend: 'Ext.plugin.Abstract',
    requires: [
		'Ext.dd.DragZone'
	],
	alias: 'plugin.draggable',
	pluginId: 'draggable',

	/**
	 * @cfg {String} ghostCls The CSS class added to the outermost element of the created ghost proxy
	 * (defaults to 'x-dataview-draggable-ghost')
	 */
	ghostCls: 'x-dataview-draggable-ghost',
	/**
	 * @cfg {Ext.XTemplate/Array} ghostTpl The template used in the ghost DataView
	 */
	ghostTpl: [
		'<tpl for=".">',
			'{title}',
		'</tpl>'
	],

	/**
	 * @cfg {Object} ddConfig Config object that is applied to the internally created DragZone
	 */

	/**
	 * @cfg {String} ghostConfig Config object that is used to configure the internally created DataView
	 */
	ghostConfig: {},

	init: function(view)
	{
		var me = this;

		me.view = view;
		me.viewListeners = view.on({
			scope: me,
			destroyable: true,
			render: me.onRender
		});

		if(!me.itemSelector)
			me.itemSelector = view.itemSelector;
		Ext.applyIf(me.ghostConfig, {
			itemSelector: 'img',
			cls: me.ghostCls,
			tpl: me.ghostTpl
		});
	},

	/**
	 * @private
	 * Called when the attached DataView is rendered. Sets up the internal DragZone
	 */
	onRender: function(view)
	{
		var me = this,
			config = Ext.apply({}, me.ddConfig || {}, {
				view: me.view,
				dvDraggable: me,
				getDragData: me.getDragData,
				afterRepair: me.afterRepair,
				getRepairXY: me.getRepairXY
	        });

		/**
		 * @property dragZone
		 * @type Ext.dd.DragZone
		 * The attached DragZone instane
		 */
		me.dragZone = Ext.create('Ext.dd.DragZone', me.view.getEl(), config);
	},

	getDragData: function(e)
	{
		var me = this,
			draggable = me.dvDraggable,
			view = me.view,
			selModel = view.getSelectionModel(),
			target = e.getTarget(draggable.itemSelector),
			selected, dragData;

		if(target)
		{
			selected = view.getSelectedNodes();
			if(selected.length === 0)
			{
				if(!view.isSelected(target))
					selModel.select(view.getRecord(target));
				selected = view.getSelectedNodes();
			}
			dragData = {
				copy: true,
				nodes: selected,
				records: selModel.getSelection(),
				item: true
			};

			if(selected.length === 1)
			{
				dragData.single = true;
				dragData.ddel = target;
			}
			else
			{
				dragData.multi = true;
				dragData.ddel = draggable.prepareGhost(selModel.getSelection());
			}

			return dragData;
		}

		return false;
	},

	afterRepair: function()
	{
		this.dragging = false;

		var me = this,
			nodes = me.dragData.nodes,
			length = nodes.length,
			i;

		for(i = 0; i < length; i++)
		{
			Ext.fly(nodes[i]).frame('#8db2e3', 1);
		}
	},

	/**
	 * @private
	 * Returns the x and y co-ordinates that the dragged item should be animated back to if it was dropped on an
	 * invalid drop target. If we're dragging more than one item we don't animate back and just allow afterRepair
	 * to frame each dropped item.
	 */
	getRepairXY: function(e)
	{
		if(this.dragData.multi)
			return false;
		else
		{
			var repairEl = Ext.get(this.dragData.ddel),
				repairXY = repairEl.getXY();

			//take the item's margins and padding into account to make the repair animation line up perfectly
			repairXY[0] += repairEl.getPadding('t') + repairEl.getMargin('t');
			repairXY[1] += repairEl.getPadding('l') + repairEl.getMargin('l');

			return repairXY;
		}
	},

	/**
	 * Updates the internal ghost DataView by ensuring it is rendered and contains the correct records
	 * @param {Array} records The set of records that is currently selected in the parent DataView
	 * @return {HtmlElement} The Ghost DataView's encapsulating HtmnlElement.
	 */
	prepareGhost: function(records)
	{
		return this.createGhost(records).getEl().dom;
	},

	/**
	 * @private
	 * Creates the 'ghost' DataView that follows the mouse cursor during the drag operation. This div is usually a
	 * lighter-weight representation of just the nodes that are selected in the parent DataView.
	 */
	createGhost: function(records)
	{
		var me = this,
			store;

		if(me.ghost)
			(store = me.ghost.store).loadRecords(records);
		else
		{
			store = Ext.create('Ext.data.Store', {
				model: records[0].self
			});

			store.loadRecords(records);
			me.ghost = Ext.create('Ext.view.View', Ext.apply({
				renderTo: document.createElement('div'),
				store: store
			}, me.ghostConfig));
			me.ghost.container.skipGarbageCollection = me.ghost.el.skipGarbageCollection = true;
		}
		store.clearData();

		return me.ghost;
	},

	destroy: function()
	{
		if(this.ghost)
			this.ghost.container.destroy();
		Ext.destroyMembers(this, 'ghost', 'viewListeners');
	}
});

