/**
 * Based on Ext.ux.DataView.DragSelector by Ed Spencer
 */
Ext.define('NetProfile.plugin.DragSelector', {
	extend: 'Ext.plugin.Abstract',
	requires: [
		'Ext.dd.DragTracker',
		'Ext.util.Region'
	],
	alias: 'plugin.dragselector',
	pluginId: 'dragselector',

	/**
	 * Initializes the plugin by setting up the drag tracker
	 */
	init: function(view)
	{
		var me = this;

		/**
		 * @property view
		 * @type Ext.view.View
		 * The DataView bound to this instance
		 */
		me.view = view;
		me.viewListeners = view.on({
			beforecontainerclick: {
				fn: me.cancelClick,
				scope: me
			},
			render: {
				fn: me.onRender,
				scope: me,
				single: true
			},
			destroyable: true
		});
		me.selected = null;
	},
	destroy: function()
	{
		var me = this;

		if(me.viewListeners)
			Ext.destroy(me.viewListeners);
		Ext.destroyMembers(this, 'tracker', 'dragRegion', 'proxy');
	},

	/**
	 * @private
	 * Called when the attached DataView is rendered. This sets up the DragTracker instance that will be used
	 * to created a dragged selection area
	 */
	onRender: function()
	{
		var me = this;

		/**
		 * @property tracker
		 * @type Ext.dd.DragTracker
		 * The DragTracker attached to this instance. Note that the 4 on* functions are called in the scope of the 
		 * DragTracker ('this' refers to the DragTracker inside those functions), so we pass a reference to the 
		 * DragSelector so that we can call this class's functions.
		 */
		me.tracker = Ext.create('Ext.dd.DragTracker', {
			view: me.view,
			el: me.view.getEl(),
			dragSelector: me,
			onBeforeStart: me.onBeforeStart,
			onStart: me.onStart,
			onDrag: me.onDrag,
			onEnd: me.onEnd
		});

		/**
		 * @property dragRegion
		 * @type Ext.util.Region
		 * Represents the region currently dragged out by the user. This is used to figure out which dataview nodes are
		 * in the selected area and to set the size of the Proxy element used to highlight the current drag area
		 */
		me.dragRegion = Ext.create('Ext.util.Region');
	},

	/**
	 * @private
	 * Listener attached to the DragTracker's onBeforeStart event. Returns false if the drag didn't start within the
	 * DataView's el
	 */
	onBeforeStart: function(e)
	{
		return e.target == this.view.getEl().dom;
	},

	/**
	 * @private
	 * Listener attached to the DragTracker's onStart event. Cancel's the DataView's containerclick event from firing
	 * and sets the start co-ordinates of the Proxy element. Clears any existing DataView selection
	 * @param {Ext.event.Event} e The click event
	 */
	onStart: function(e)
	{
		var me = this,
			dragSelector = me.dragSelector,
			advDrag = e.ctrlKey || e.shiftKey,
			view = me.view;

		// Flag which controls whether the cancelClick method vetoes the processing of the DataView's containerclick event.
		// On IE (where else), this needs to remain set for a millisecond after mouseup because even though the mouse has
		// moved, the mouseup will still trigger a click event.
		me.dragging = true;

		//here we reset and show the selection proxy element and cache the regions each item in the dataview take up
		dragSelector.fillRegions();
		dragSelector.getProxy().show();
		if(advDrag)
			dragSelector.snapshotSelected();
		else
			view.getSelectionModel().deselectAll();
	},

	/**
	 * @private
	 * Reusable handler that's used to cancel the container click event when dragging on the dataview. See onStart for
	 * details
	 */
	cancelClick: function()
	{
		if(!this.view.ownerCt)
			return true;
		return !this.tracker.dragging;
	},

	/**
	 * @private
	 * Listener attached to the DragTracker's onDrag event. Figures out how large the drag selection area should be and
	 * updates the proxy element's size to match. Then iterates over all of the rendered items and marks them selected
	 * if the drag region touches them
	 * @param {Ext.event.Event} e The drag event
	 */
	onDrag: function(e)
	{
		var me = this,
			dragSelector = me.dragSelector,
			selModel = dragSelector.view.getSelectionModel(),
			dragRegion = dragSelector.dragRegion,
			bodyRegion = dragSelector.bodyRegion,
			snapshot = dragSelector.selected,
			proxy = dragSelector.getProxy(),
			regions = dragSelector.regions,
			length = regions.length,

			startXY = me.startXY,
			currentXY = me.getXY(),
			minX = Math.min(startXY[0], currentXY[0]),
			minY = Math.min(startXY[1], currentXY[1]),
			width = Math.abs(startXY[0] - currentXY[0]),
			height = Math.abs(startXY[1] - currentXY[1]),

			region, selected, i, cursel;

		Ext.apply(dragRegion, {
			top: minY,
			left: minX,
			right: minX + width,
			bottom: minY + height
		});

		dragRegion.constrainTo(bodyRegion);
		proxy.setBox(dragRegion);

		for(i = 0; i < length; i++)
		{
			region = regions[i];
			selected = dragRegion.intersect(region);

			if(snapshot && snapshot.length)
			{
				cursel = (snapshot.indexOf(i) !== -1);
				if(selected)
				{
					if(cursel)
						selModel.deselect(i);
					else
						selModel.select(i, true);
				}
				else
				{
					if(cursel)
						selModel.select(i, true);
					else
						selModel.deselect(i);
				}
			}
			else
			{
				if(selected)
					selModel.select(i, true);
				else
					selModel.deselect(i);
			}
		}
	},

	/**
	 * @private
	 * Listener attached to the DragTracker's onEnd event. This is a delayed function which executes 1
	 * millisecond after it has been called. This is because the dragging flag must remain active to cancel
	 * the containerclick event which the mouseup event will trigger.
	 * @param {Ext.event.Event} e The event object
	 */
	onEnd: Ext.Function.createDelayed(function(e)
	{
		var me = this,
			view = me.view,
			selModel = view.getSelectionModel(),
			dragSelector = me.dragSelector;

		me.dragging = false;
		dragSelector.selected = null;
		dragSelector.destroyProxy();
	}, 1),

	/**
	 * @private
	 * Creates a Proxy element that will be used to highlight the drag selection region
	 * @return {Ext.Element} The Proxy element
	 */
	getProxy: function()
	{
		var me = this;

		if(!me.proxy)
			me.proxy = me.view.getEl().createChild({
				tag: 'div',
				cls: 'x-view-selector'
			});
		return me.proxy;
	},
	destroyProxy: function()
	{
		var me = this;

		if(me.proxy)
		{
			me.proxy.hide();
			Ext.destroyMembers(me, 'proxy');
		}
	},

	/**
	 * @private
	 * Gets the region taken up by each rendered node in the DataView. We use these regions to figure out which nodes
	 * to select based on the selector region the user has dragged out
	 */
	fillRegions: function()
	{
		var me = this,
			view = me.view,
			regions = me.regions = [];

		view.all.each(function(node)
		{
			regions.push(node.getRegion());
		});
		me.bodyRegion = view.getEl().getRegion();
	},
	snapshotSelected: function()
	{
		var me = this,
			view = me.view,
			selModel = view.getSelectionModel(),
			snapshot = [],
			idx;

		Ext.each(selModel.getSelection(), function(rec)
		{
			idx = view.indexOf(rec);
			if(idx !== -1)
				snapshot.push(idx);
		});
		me.selected = snapshot;
	}
});

