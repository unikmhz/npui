/**
 * @class NetProfile.controller.GlobalSettingsForm
 * @extends NetProfile.controller.SettingsForm
 */
Ext.define('NetProfile.controller.GlobalSettingsForm', {
	extend: 'NetProfile.controller.SettingsForm',

	formFn: NetProfile.api.GlobalSetting.gsform_get,
	submitFn: NetProfile.api.GlobalSetting.gsform_submit
});

