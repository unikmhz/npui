Ext.onReady(function()
{
	Ext.define('Ext.locale.ru.Date', {
		override: 'Ext.Date',
		defaultFormat: 'd.m.Y'
	});
	Ext.define('Ext.locale.ru.NetProfile.form.field.DateTime', {
		override: 'NetProfile.form.field.DateTime',
		format: 'd.m.Y H:i',
		altFormats: 'Y-m-d H:i|Y-m-d H:i:s|Y-m-d\\TH:i:s|Y-m-d\\TH:i:sP|C', // FIXME
		timeFormat: 'H:i'
	});
	Ext.define('Ext.locale.ru.picker.Date', {
		override: 'Ext.picker.Date',
		format: 'd.m.Y'
	});
	Ext.define('Ext.locale.ru.form.field.Date', {
		override: 'Ext.form.field.Date',
		format: 'd.m.Y'
	});
	Ext.define('Ext.locale.ru.NetProfile.picker.DateTime', {
		override: 'NetProfile.picker.DateTime',
		applyText: 'Применить',
		cancelText: 'Отмена'
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

	Ext.define('Ext.locale.ru.grid.filters.Filters', {
		override: 'Ext.grid.filters.Filters',
		menuFilterText: 'Фильтры'
	});
	Ext.define('Ext.locale.ru.grid.filters.filter.String', {
		override: 'Ext.grid.filters.filter.String',
		emptyText: 'Введите текст...'
	});
	Ext.define('Ext.locale.ru.grid.filters.filter.Boolean', {
		override: 'Ext.grid.filters.filter.Boolean',
		yesText: 'Да',
		noText: 'Нет'
	});
	Ext.define('Ext.locale.ru.grid.filters.filter.Date', {
		override: 'Ext.grid.filters.filter.Date',
		config: {
			fields: {
				gt: { text: 'Позднее' },
				lt: { text: 'Раньше' },
				eq: { text: 'В' }
			}
		}
	});
	Ext.define('Ext.locale.ru.NetProfile.grid.filters.filter.Date', {
		override: 'NetProfile.grid.filters.filter.Date',
		config: {
			fields: {
				ge: { text: 'Позднее' },
				le: { text: 'Раньше' },
				eq: { text: 'В' }
			}
		}
	});
	Ext.define('Ext.locale.ru.grid.filters.filter.List', {
		override: 'Ext.grid.filters.filter.List',
		loadingText: 'Загрузка...'
	});
	Ext.define('Ext.locale.ru.grid.filters.filter.Number', {
		override: 'Ext.grid.filters.filter.Number',
		emptyText: 'Введите число...'
	});
	Ext.define('Ext.locale.ru.NetProfile.grid.filters.filter.Number', {
		override: 'NetProfile.grid.filters.filter.Number',
		emptyText: 'Введите число...'
	});
	Ext.define('Ext.locale.ru.NetProfile.grid.filters.filter.IPv6', {
		override: 'NetProfile.grid.filters.filter.IPv6',
		emptyText: 'Введите адрес IPv6...'
	});
	Ext.define('Ext.locale.ru.NetProfile.grid.plugin.SimpleSearch', {
		override: 'NetProfile.grid.plugin.SimpleSearch',
		fieldEmptyText: 'Поиск...'
	});
	Ext.define('Ext.locale.ru.NetProfile.grid.plugin.ExtraSearch', {
		override: 'NetProfile.grid.plugin.ExtraSearch',
		searchText: 'Поиск',
		searchTipText: 'Дополнительные условия поиска.',
		advSearchText: 'Расширенный поиск',
		clearText: 'Сбросить'
	});

	Ext.define('Ext.locale.ru.NetProfile.grid.ModelGrid', {
		override: 'NetProfile.grid.ModelGrid',
		emptyText: 'По вашему запросу ничего не найдено.',
		clearText: 'Сбросить',
		clearTipText: 'Сбросить фильтры и порядок сортировки.',
		addText: 'Добавить',
		addTipText: 'Добавить новый объект.',
		addWindowText: 'Добавить новый объект',
		propTipText: 'Просмотр свойств объекта',
		deleteTipText: 'Удалить объект',
		deleteMsgText: 'Вы уверены в том, что хотите удалить данный объект?',
		actionTipText: 'Действия для объекта',
		exportText: 'Экспорт'
	});

	Ext.define('Ext.locale.ru.NetProfile.form.field.ModelSelect', {
		override: 'NetProfile.form.field.ModelSelect',
		chooseText: 'Выберите объект'
	});
	Ext.define('Ext.locale.ru.NetProfile.form.field.FileSelect', {
		override: 'NetProfile.form.field.FileSelect',
		chooseText: 'Выберите файл'
	});

	Ext.define('Ext.locale.ru.NetProfile.tab.PropBar', {
		override: 'NetProfile.tab.PropBar',
		recordText: 'Запись',
		submitText: 'Отправить'
	});

	Ext.define('Ext.locale.ru.NetProfile.toolbar.MainToolbar', {
		override: 'NetProfile.toolbar.MainToolbar',
		toolsText: 'Инструменты',
		toolsTipText: 'Различные второстепенные окна и настройки.',
		logoutText: 'Выход',
		logoutTipText: 'Выйти из системы.',
		chPassText: 'Изменить пароль',
		chLangText: 'Переключение языка',
		showConsoleText: 'Показать консоль',
		aboutText: 'О программе…'
	});

	Ext.define('Ext.locale.ru.NetProfile.form.Panel', {
		override: 'NetProfile.form.Panel',
		resetText: 'Сбросить',
		resetTipText: 'Вернуть значения полей в этой форме к исходным.',
		submitText: 'Сохранить',
		submitTipText: 'Проверить и сохранить данные в этой форме.'
	});

	Ext.define('Ext.locale.ru.NetProfile.panel.Wizard', {
		override: 'NetProfile.panel.Wizard',
		config: {
			cancelBtnCfg: { text: 'Отмена' },
			prevBtnCfg: { text: 'Назад' },
			nextBtnCfg: { text: 'Далее' },
			submitBtnCfg: { text: 'Готово' }
		}
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

	Ext.define('Ext.locale.ru.NetProfile.menu.FileFolder', {
		override: 'NetProfile.menu.FileFolder',
		createText: 'Создать подпапку',
		propText: 'Свойства',
		renameText: 'Переименовать',
		deleteText: 'Удалить',
		mountText: 'Подключить',
		newFolderText: 'Новая папка',
		deleteFolderText: 'Удаление папки',
		deleteFolderVerboseText: 'Вы уверены что хотите удалить эту папку?'
	});

	Ext.define('Ext.locale.ru.NetProfile.form.field.RightsBitmaskField', {
		override: 'NetProfile.form.field.RightsBitmaskField',
		ownerText: 'Владелец',
		groupText: 'Группа',
		otherText: 'Прочие',
		readText: 'Чтение',
		writeText: 'Запись',
		executeText: 'Выполнение',
		traverseText: 'Переход'
	});

	Ext.define('Ext.locale.ru.NetProfile.form.field.IPv4', {
		override: 'NetProfile.form.field.IPv4',
		octetErrorText: 'Октет {0}: {1}',
		blankText: 'Это поле не может быть пустым',
		config: {
			clearBtnCfg: {
				tooltip: 'Очистить поле'
			}
		}
	});
	Ext.define('Ext.locale.ru.NetProfile.form.field.IPv6', {
		override: 'NetProfile.form.field.IPv6',
		invalidAddressText: 'Некорректный адрес IPv6'
	});

	Ext.define('Ext.locale.ru.NetProfile.panel.FileBrowser', {
		override: 'NetProfile.panel.FileBrowser',

		emptyText: 'Папка пуста',

		viewText: 'Вид',
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
		btnFoldersText: 'Папки',

		btnRenameText: 'Переименовать',
		btnPropsText: 'Свойства',
		btnDownloadText: 'Скачать',

		searchEmptyText: 'Поиск...',

		gridNameText: 'Имя',
		gridSizeText: 'Размер',
		gridCreatedText: 'Создан',
		gridModifiedText: 'Изменён',

		dragText: 'Переместить или вложить файлы ({0})',

		bytesText: 'байт',
		kibText: 'Кбайт',
		mibText: 'Мбайт',
		gibText: 'Гбайт',
		tibText: 'Тбайт',
		pibText: 'Пбайт',
		eibText: 'Эбайт'
	});
	Ext.define('Ext.locale.ru.NetProfile.form.FileUpload', {
		override: 'NetProfile.form.FileUpload',

		titleText: 'Заливка файлов',
		closeText: 'Закрыть',
		addText: 'Добавить',
		uploadText: 'Залить',
		removeText: 'Убрать',
		errorText: 'Ошибка заливки',

		waitMsg: 'Файлы заливаются...',
		clientInvalidMsg: 'Форма содержит некорректные данные и не может быть отправлена.',
		connectFailureMsg: 'Ошибка соединения с сервером.',
	});
	Ext.define('Ext.locale.ru.NetProfile.view.FileIconView', {
		override: 'NetProfile.view.FileIconView',
		sizeText: 'Размер: {0}',
		mimeTypeText: 'MIME тип: {0}'
	});

	Ext.define('Ext.locale.ru.NetProfile.grid.CapabilityGrid', {
		override: 'NetProfile.grid.CapabilityGrid',

		textName: 'Название',
		textValue: 'Значение',
		textAllowed: 'Разрешено',
		textDenied: 'Запрещено',
		textNotDefined: 'Не определено',
		textTipACL: 'Редактирование ACL'
	});
});

