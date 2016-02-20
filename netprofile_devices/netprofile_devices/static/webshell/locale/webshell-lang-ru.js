Ext.onReady(function()
{
	Ext.define('NetProfile.locale.ru.devices.controller.HostProbe', {
		override: 'NetProfile.devices.controller.HostProbe',

		probeResultsText: 'Результаты зондирования'
	});
	Ext.define('NetProfile.locale.ru.devices.grid.ProbeResults', {
		override: 'NetProfile.devices.grid.ProbeResults',

		okText: 'OK',
		partialText: 'Потеря пакетов',
		noneText: 'Недоступен',
		firewallText: 'Брандмауэр',

		hostText: 'Узел',
		addressText: 'Адрес',
		stateText: 'Состояние',
		detailsText: 'Подробности',

		hostUnreachableText: 'Узел недоступен',
		behindFirewallText: 'Узел за брандмауэром',
		hostDetailsTpl: '{0}/{1} мин.:{2} ср.:{3} макс.:{4}'
	});
});

