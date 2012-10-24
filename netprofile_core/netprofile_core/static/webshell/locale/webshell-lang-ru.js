Ext.onReady(function() {

	Ext.define('Ext.locale.ru.grid.column.Action', {
		override: 'Ext.grid.column.Action',
		menuText: '<i>Действия</i>'
	});

	Ext.define('Ext.locale.ru.ux.grid.FiltersFeature', {
		override: 'Ext.ux.grid.FiltersFeature',
		menuFilterText: 'Фильтры'
	});
	Ext.define('Ext.locale.ru.ux.grid.filter.BooleanFilter', {
		override: 'Ext.ux.grid.filter.BooleanFilter',
		yesText: 'Да',
		noText: 'Нет'
	});
	Ext.define('Ext.locale.ru.ux.grid.filter.DateFilter', {
		override: 'Ext.ux.grid.filter.DateFilter',
		afterText: 'Позднее',
		beforeText: 'Раньше',
		dateFormat: 'd.m.Y',
		onText: 'В'
	});
	Ext.define('Ext.locale.ru.ux.grid.menu.ListMenu', {
		override: 'Ext.ux.grid.menu.ListMenu',
		loadingText: 'Загрузка...'
	});
	Ext.define('Ext.locale.ru.ux.grid.menu.RangeMenu', {
		override: 'Ext.ux.grid.menu.RangeMenu',
		fieldLabels: {
			gt: 'Больше',
			lt: 'Меньше',
			eq: 'Равно'
		},
		menuItemCfgs: {
			emptyText: 'Введите число...',
			selectOnFocus: false,
			width: 155
		}
	});
	Ext.define('Ext.locale.ru.ux.grid.menu.StringMenu', {
		override: 'Ext.ux.grid.menu.StringMenu',
		fieldLabels: {
			contains: 'Содержит',
			startswith: 'Начинается на',
			endswith: 'Заканчивается на'
		},
		menuItemCfgs: {
			emptyText: 'Введите фильтр...',
			selectOnFocus: true,
			width: 155
		}
	});

	Ext.define('Ext.locale.ru.ux.grid.SimpleSearchFeature', {
		override: 'Ext.ux.grid.SimpleSearchFeature',
		fieldEmptyText: 'Поиск...'
	});

	Ext.define('Ext.locale.ru.NetProfile.view.ModelGrid', {
		override: 'NetProfile.view.ModelGrid',
		emptyText: 'По вашему запросу ничего не найдено.',
		searchText: 'Поиск',
		searchTipText: 'Дополнительные условия поиска.',
		clearText: 'Сбросить',
		clearTipText: 'Сбросить фильтры и порядок сортировки.',
		addText: 'Добавить',
		addTipText: 'Добавить новый объект.',
		addWindowText: 'Добавить новый объект',
		propTipText: 'Просмотр свойств объекта',
		deleteTipText: 'Удалить объект',
		deleteMsgText: 'Вы уверены в том, что хотите удалить данный объект?',
		actionTipText: 'Действия для объекта'
	});

	Ext.define('Ext.locale.ru.NetProfile.view.ModelSelect', {
		override: 'NetProfile.view.ModelSelect',
		chooseText: 'Выберите объект'
	});

	Ext.define('Ext.locale.ru.NetProfile.view.PropBar', {
		override: 'NetProfile.view.PropBar',
		recordText: 'Запись'
	});

	Ext.define('Ext.locale.ru.NetProfile.view.TopBar', {
		override: 'NetProfile.view.TopBar',
		logoutText: 'Выход',
		logoutTipText: 'Выйти из системы.'
	});

	Ext.define('Ext.locale.ru.NetProfile.view.Form', {
		override: 'NetProfile.view.Form',
		resetText: 'Сбросить',
		resetTipTitleText: 'Сбросить данные',
		resetTipText: 'Вернуть значения полей в этой форме к исходным.',
		submitText: 'Сохранить',
		submitTipTitleText: 'Сохранить данные',
		submitTipText: 'Проверить и сохранить данные в этой форме.'
	});

	Ext.define('Ext.locale.ru.NetProfile.view.Wizard', {
		override: 'NetProfile.view.Wizard',
		btnPrevText: 'Назад',
		btnNextText: 'Далее',
		btnCancelText: 'Отмена',
		btnSubmitText: 'Готово'
	});

});

