Ext.define('NetProfile.form.FileUpload', {
	extend: 'Ext.form.Panel',
	alias: 'widget.fileuploadform',
	requires: [
		'Ext.form.*',
		'Ext.button.Button'
	],

	cls: 'np-file-upload',
	border: false,
	layout: 'anchor',
	resizable: {
		handles: 'e',
		pinned: true
	},
	defaults: {
		anchor: '100%'
	},
	minWidth: 280,

	titleText: 'Upload Files',
	closeText: 'Close',
	addText: 'Add',
	uploadText: 'Upload',
	removeText: 'Remove',
	errorText: 'Error',

	waitMsg: 'Uploading Files...',
	clientInvalidMsg: 'Form fields may not be submitted with invalid values.',
	connectFailureMsg: 'Can\'t connect to server.',

	initComponent: function()
	{
		var me = this;

		me.title = me.titleText;
		me.items = [me.getUploadField()];
		me.buttons = [{
			text: this.closeText,
			iconCls: 'ico-cancel',
			handler: 'onButtonClose',
			scope: me
		}, '->', {
			text: this.addText,
			iconCls: 'ico-add',
			handler: 'onButtonAdd',
			scope: me
		}, {
			text: this.uploadText,
			formBind: true,
			disabled: true,
			iconCls: 'ico-upload',
			handler: 'onButtonSubmit',
			scope: me
		}];

		me.callParent(arguments);
	},
	onButtonClose: function()
	{
		var me = this,
			fb = me.ownerCt,
			tbar = fb.down('toolbar[dock=top]'),
			btn = tbar.getComponent('btn_upload');

		btn.toggle(false);
		me.removeAll(true);
		me.add(me.getUploadField());
	},
	onButtonAdd: function()
	{
		this.add(this.getUploadField());
	},
	onButtonSubmit: function()
	{
		var me = this,
			form = me.getForm(),
			fb = me.ownerCt;

		if(!form || !form.isValid())
			return;
		form.submit({
			params: fb.getUploadParams(),
			success: function(rform, act)
			{
				fb.updateStore();
				me.onButtonClose();
			},
			failure: function(rform, act)
			{
				// TODO: externalize this code
				switch(act.failureType)
				{
					case Ext.form.action.Action.CLIENT_INVALID:
						NetProfile.msg.err(me.errorText, me.clientInvalidMsg);
						break;
					case Ext.form.action.Action.CONNECT_FAILURE:
						NetProfile.msg.err(me.errorText, me.connectFailureMsg);
						break;
					case Ext.form.action.Action.SERVER_INVALID:
						NetProfile.msg.err(me.errorText, act.result && act.result.msg);
						break;
					case Ext.form.action.Action.LOAD_FAILURE:
						// TODO: write this
						break;
					default:
						break;
				}
				fb.updateStore();
				me.onButtonClose();
			},
			waitMsg: me.waitMsg
		});
	},
	getUploadField: function()
	{
		var me = this,
			cfg = {
				xtype: 'container',
				cls: 'np-file-upload-cont',
				layout: {
					type: 'hbox',
					align: 'stretch',
					pack: 'end'
				},
				defaults: {
					margin: 0
				},
				items: [{
					xtype: 'filefield',
					name: 'file',
					flex: 1,
					allowBlank: false
				}, {
					xtype: 'tool',
					cls: 'np-file-upload-close',
					tooltip: this.uploadRemoveText,
					type: 'close',
					handler: function()
					{
						var cont, pcont;

						cont = this.up('container[cls~=np-file-upload-cont]');
						if(!cont || !cont.ownerCt)
							return;
						pcont = cont.ownerCt;
						pcont.remove(cont, true);
					},
					width: 20
				}]
			};
		return cfg;
	}
});

