/**
 * @class NetProfile.view.WizardPane
 * @extends Ext.form.Panel
 */
Ext.define('NetProfile.view.WizardPane', {
	extend: 'Ext.form.Panel',
	alias: 'widget.npwizardpane',

	border: 0,
	bodyPadding: 5,
	width: 400,
	autoScroll: true,
	doValidation: true,
	doGetValues: true,
	remotePrev: false,
	remoteNext: false,
	allowSubmit: false,
	fieldDefaults: {
		labelWidth: 120,
		labelAlign: 'right'
//		msgTarget: 'side'
	}
});

