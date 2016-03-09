/**
 * @class NetProfile.controller.UserSettingsForm
 * @extends NetProfile.controller.SettingsForm
 */
Ext.define('NetProfile.controller.UserSettingsForm', {
	extend: 'NetProfile.controller.SettingsForm',

	formFn: NetProfile.api.UserSetting.usform_get,
	submitFn: NetProfile.api.UserSetting.usform_submit,
	onSuccessFn: function(form, action)
	{
		NetProfile.api.UserSetting.client_get(function(data, result)
		{
			if(!data || !data.settings)
				return false;

			NetProfile.userSettings = data.settings;
			return true;
		});
	}
});
