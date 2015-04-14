/**
 * @class NetProfile.documents.button.DocumentButton
 * @extends Ext.button.Button
 */
Ext.define('NetProfile.documents.button.DocumentButton', {
	extend: 'Ext.button.Button',
	alias: 'widget.docbutton',
	requires: [
		'Ext.XTemplate'
	],

	objectType: null,

	handler: function()
	{
		var me = this,
			gen_panel = me.up('menu'),
			rec_panel = gen_panel.up('panel[cls~=record-tab]'),
			doc_box, obj_id, doc_id;

		if(rec_panel && rec_panel.record)
			obj_id = rec_panel.record.getId();
		doc_box = gen_panel.getComponent('docid');
		if(doc_box)
			doc_id = parseInt(doc_box.getValue());
		if(!obj_id || !doc_id)
			return;
		NetProfile.api.Document.prepare_template({
			'objid'   : obj_id,
			'objtype' : me.objectType,
			'docid'   : doc_id
		}, me.onPrepareTemplate, me);
	},

	onPrepareTemplate: function(data, res)
	{
		var doc, body, tpl, win, el;

		if(!res.result || !res.result.success)
			return;
		doc = data.doc;
		body = doc.body;
		if(doc.type == 'html-ext')
		{
			tpl = new Ext.XTemplate(body);
			body = tpl.apply(data.vars);
		}
		if(body && Ext.Array.contains(['html-plain', 'html-ext'], doc.type))
		{
			win = window.open(
				'', 'doc_print',
				'menubar=no,location=no,resizable=yes,scrollbars=yes,status=yes'
			);
			if(!win)
				return; // TODO: alert user about blocked window
			win.document.write('\074!DOCTYPE html\076\
\074html xmlns="http://www.w3.org/1999/xhtml"\076\
\074head\076\
\074meta charset="UTF-8"\076\
\074meta http-equiv="X-UA-Compatible" content="IE=edge;chrome=1" /\076\
\074title\076' + doc.name + '\074/title\076\
\074/head\076\
\074body\076\
\074/body\076\
\074/html\076\
			');
			el = win.document.getElementsByTagName('body');
			if(el && el.length)
			{
				el[0].innerHTML = body;
				win.focus();
				win.print();
			}
		}
	}
});

