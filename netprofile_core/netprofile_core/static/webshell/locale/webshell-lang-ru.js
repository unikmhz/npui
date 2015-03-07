Ext.onReady(function()
{
	Ext.define('Ext.locale.ru.ux.DateTimePicker', {
		override: 'Ext.ux.DateTimePicker',
		todayText: 'Сейчас',
		timeLabel: 'Время'
	});

	Ext.define('Ext.locale.ru.grid.RowEditor', {
		override: 'Ext.grid.RowEditor',
		saveBtnText: 'Применить',
		cancelBtnText: 'Отмена',
		errorsText: 'Ошибки',
		dirtyText: 'Вам необходимо применить либо отменить изменения'
	});

	Ext.define('Ext.locale.ru.view.Table', {
		override: 'Ext.view.Table',
		loadingText: 'Загрузка...'
	});

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

	Ext.define('Ext.locale.ru.ux.grid.ExtraSearchFeature', {
		override: 'Ext.ux.grid.ExtraSearchFeature',
		searchText: 'Поиск',
		searchTipText: 'Дополнительные условия поиска.',
		advSearchText: 'Расширенный поиск',
		clearText: 'Сбросить'
	});

	Ext.define('Ext.locale.ru.NetProfile.view.ModelGrid', {
		override: 'NetProfile.view.ModelGrid',
		emptyText: 'По вашему запросу ничего не найдено.',
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
		recordText: 'Запись',
		submitText: 'Отправить'
	});

	Ext.define('Ext.locale.ru.NetProfile.view.TopBar', {
		override: 'NetProfile.view.TopBar',
		toolsText: 'Инструменты',
		toolsTipText: 'Различные второстепенные окна и настройки.',
		logoutText: 'Выход',
		logoutTipText: 'Выйти из системы.',
		chLangText: 'Переключение языка',
		showConsoleText: 'Показать консоль',
		aboutText: 'О программе…'
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

	Ext.define('Ext.locale.ru.NetProfile.controller.UserSettingsForm', {
		override: 'NetProfile.controller.UserSettingsForm',
		btnResetText: 'Сбросить',
		btnResetTipTitleText: 'Сбросить настройки',
		btnResetTipText: 'Вернуть значения полей в этой форме к исходным.',
		btnSaveText: 'Сохранить',
		btnSaveTipTitleText: 'Сохранить настройки',
		btnSaveTipText: 'Проверить и сохранить ваши настройки'
	});

	Ext.define('Ext.locale.ru.NetProfile.view.FileFolderContextMenu', {
		override: 'NetProfile.view.FileFolderContextMenu',
		createText: 'Создать подпапку',
		propText: 'Свойства',
		renameText: 'Переименовать',
		deleteText: 'Удалить',
		mountText: 'Подключить',
		newFolderText: 'Новая папка',
		deleteFolderText: 'Удаление папки',
		deleteFolderVerboseText: 'Вы уверены что хотите удалить эту папку?'
	});

	Ext.define('Ext.locale.ru.ux.form.RightsBitmaskField', {
		override: 'Ext.ux.form.RightsBitmaskField',
		ownerText: 'Владелец',
		groupText: 'Группа',
		otherText: 'Прочие',
		readText: 'Чтение',
		writeText: 'Запись',
		executeText: 'Выполнение',
		traverseText: 'Переход'
	});

	Ext.define('Ext.locale.ru.ux.form.field.IPv6', {
		override: 'Ext.ux.form.field.IPv6',
		invalidAddressText: 'Некорректный адрес IPv6'
	});

	Ext.define('Ext.locale.ru.NetProfile.view.FileBrowser', {
		override: 'NetProfile.view.FileBrowser',

		emptyText: 'Папка пуста',

		viewText: 'Просмотр',
		viewAsIconsText: 'Иконки',
		viewAsListText: 'Список',
		viewAsGridText: 'Таблица',

		sortText: 'Сортировка',
		sortByNameText: 'По имени файла',
		sortByCTimeText: 'По времени создания',
		sortByMTimeText: 'По времени изменения',
		sortBySizeText: 'По размеру',

		sortAscText: 'По возрастанию',
		sortDescText: 'По убыванию',

		btnDeleteText: 'Удалить',

		deleteTipText: 'Удалить файл',
		deleteMsgText: 'Вы уверены что хотите удалить выбранный файл?',
		deleteManyTipText: 'Удалить файлы',
		deleteManyMsgText: 'Вы уверены что хотите удалить выбранные файлы?',

		btnUploadText: 'Залить',

		uploadTitleText: 'Заливка файлов',
		uploadCloseText: 'Закрыть',
		uploadAddText: 'Добавить',
		uploadUploadText: 'Залить',
		uploadRemoveText: 'Убрать',
		uploadWaitMsg: 'Файлы заливаются...',

		btnRenameText: 'Переименовать',
		btnPropsText: 'Свойства',
		btnDownloadText: 'Скачать',

		searchEmptyText: 'Поиск...',

		gridNameText: 'Имя',
		gridSizeText: 'Размер',
		gridCreatedText: 'Создан',
		gridModifiedText: 'Изменён',

		kibText: 'Кбайт',
		mibText: 'Мбайт',
		gibText: 'Гбайт',
		tibText: 'Тбайт'
	});

	Ext.define('Ext.locale.ru.NetProfile.view.CapabilityGrid', {
		override: 'NetProfile.view.CapabilityGrid',

		textName: 'Название',
		textValue: 'Значение',
		textAllowed: 'Разрешено',
		textDenied: 'Запрещено',
		textNotDefined: 'Не определено',
		textTipACL: 'Редактирование ACL'
	});
});

