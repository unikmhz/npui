/*!
 * Extensible 1.6.0-rc.1
 * Copyright(c) 2010-2013 Extensible, LLC
 * licensing@ext.ensible.com
 * http://ext.ensible.com
 */
/*!
 * Extensible 1.6.0-rc.1
 * Copyright(c) 2010-2013 Extensible, LLC
 * licensing@ext.ensible.com
 * http://ext.ensible.com
 */
/*
 * Russian locale
 * By Alex 'Unik' Unigovsky
 */

Ext.onReady(function()
{
	var exists = Ext.Function.bind(Ext.ClassManager.get, Ext.ClassManager);

	function plural(f1, f2, f3)
	{
		return function(num)
		{
			var mod10 = num % 10,
				mod100 = num % 100;
			if((mod100 > 10) && (mod100 <= 20))
				return f3;
			if(mod10 === 0)
				return f3;
			if(mod10 === 1)
				return f1;
			if(mod10 < 5)
				return f2;
			return f3;
		}
	}

	Extensible.Date.use24HourTime = true;

	if(exists('Extensible.calendar.view.AbstractCalendar'))
		Ext.apply(Extensible.calendar.view.AbstractCalendar.prototype, {
			startDay: 1,
			todayText: 'Сегодня',
			defaultEventTitleText: '(Без названия)',
			ddCreateEventText: 'Создать событие {0}',
			ddCopyEventText: 'Создать копию события {0}',
			ddMoveEventText: 'Переназначить на {0}',
			ddResizeEventText: 'Переназначить на {0}'
		});

	if(exists('Extensible.calendar.view.Month'))
		Ext.apply(Extensible.calendar.view.Month.prototype, {
			moreText: '+ ещё {0}…', // deprecated
			getMoreText: function(numEvents) {
				return '+ ещё {0}…';
			},
			detailsTitleDateFormat: 'F j'
		});

	if(exists('Extensible.calendar.CalendarPanel'))
		Ext.apply(Extensible.calendar.CalendarPanel.prototype, {
			startDay: 1,
			todayText: 'Сегодня',
			dayText: 'День',
			weekText: 'Неделя',
			monthText: 'Месяц',
			jumpToText: 'Перейти к:',
			goText: 'Перейти',
			multiDayText: '{0} дней', // deprecated
			multiWeekText: '{0} недель', // deprecated
			getMultiDayText: plural('{0} день', '{0} дня', '{0} дней'),
			getMultiWeekText: plural('{0} неделя', '{0} недели', '{0} недель')
		});

	if(exists('Extensible.calendar.form.EventWindow'))
		Ext.apply(Extensible.calendar.form.EventWindow.prototype, {
			width: 650,
			labelWidth: 65,
			titleTextAdd: 'Добавление события',
			titleTextEdit: 'Изменение события',
			savingMessage: 'Сохранение изменений…',
			deletingMessage: 'Удаление события…',
			detailsLinkText: 'Редактировать детали…',
			saveButtonText: 'Сохранить',
			deleteButtonText: 'Удалить',
			cancelButtonText: 'Отмена',
			titleLabelText: 'Заголовок',
			datesLabelText: 'Когда',
			calendarLabelText: 'Календарь'
		});

	if(exists('Extensible.calendar.form.EventDetails'))
		Ext.apply(Extensible.calendar.form.EventDetails.prototype, {
			labelWidth: 65,
			labelWidthRightCol: 65,
			title: 'Форма события',
			titleTextAdd: 'Добавление события',
			titleTextEdit: 'Изменение события',
			saveButtonText: 'Сохранить',
			deleteButtonText: 'Удалить',
			cancelButtonText: 'Отмена',
			titleLabelText: 'Заголовок',
			datesLabelText: 'Когда',
			reminderLabelText: 'Напоминание',
			notesLabelText: 'Заметки',
			locationLabelText: 'Место',
			webLinkLabelText: 'Ссылка',
			calendarLabelText: 'Календарь',
			repeatsLabelText: 'Повторяется'
		});

	if(exists('Extensible.form.field.DateRange'))
		Ext.apply(Extensible.form.field.DateRange.prototype, {
			toText: 'до',
			allDayText: 'Весь день'
		});

	if(exists('Extensible.calendar.form.field.CalendarCombo'))
		Ext.apply(Extensible.calendar.form.field.CalendarCombo.prototype, {
			fieldLabel: 'Календарь'
		});

	if(exists('Extensible.calendar.gadget.CalendarListPanel'))
		Ext.apply(Extensible.calendar.gadget.CalendarListPanel.prototype, {
			title: 'Календари'
		});

	if(exists('Extensible.calendar.gadget.CalendarListMenu'))
		Ext.apply(Extensible.calendar.gadget.CalendarListMenu.prototype, {
			displayOnlyThisCalendarText: 'Показывать только этот календарь'
		});

	if(exists('Extensible.form.recurrence.Combo'))
		Ext.apply(Extensible.form.recurrence.Combo.prototype, {
			fieldLabel: 'Повторяется',
			recurrenceText: {
				none: 'Не повторяется',
				daily: 'Ежедневно',
				weekly: 'Еженедельно',
				monthly: 'Ежемесячно',
				yearly: 'Ежегодно'
			}
		});

	if(exists('Extensible.calendar.form.field.ReminderCombo'))
		Ext.apply(Extensible.calendar.form.field.ReminderCombo.prototype, {
			fieldLabel: 'Напоминание',
			noneText: 'Нет',
			atStartTimeText: 'По наступлении',
			getMinutesText: plural('минуту', 'минуты', 'минут'),
			getHoursText: plural('час', 'часа', 'часов'),
			getDaysText: plural('день', 'дня', 'дней'),
			getWeeksText: plural('неделю', 'недели', 'недель'),
			reminderValueFormat: 'За {0} {1} до начала' // e.g. "2 hours before start"
		});

	if(exists('Extensible.form.field.DateRange'))
		Ext.apply(Extensible.form.field.DateRange.prototype, {
			dateFormat: 'd.m.Y'
		});

	if(exists('Extensible.calendar.menu.Event'))
		Ext.apply(Extensible.calendar.menu.Event.prototype, {
			editDetailsText: 'Изменить детали',
			deleteText: 'Удалить',
			moveToText: 'Переместить…',
			copyToText: 'Копировать…'
		});

	if(exists('Extensible.calendar.dd.DropZone'))
		Ext.apply(Extensible.calendar.dd.DropZone.prototype, {
			dateRangeFormat: '{0}-{1}',
			dateFormat: 'M j'
		});

	if(exists('Extensible.calendar.dd.DayDropZone'))
		Ext.apply(Extensible.calendar.dd.DayDropZone.prototype, {
			dateRangeFormat: '{0}-{1}',
			dateFormat : 'M j'
		});

	if(exists('Extensible.calendar.template.BoxLayout'))
		Ext.apply(Extensible.calendar.template.BoxLayout.prototype, {
			firstWeekDateFormat: 'D j',
			otherWeeksDateFormat: 'j',
			singleDayDateFormat: 'l, F j, Y',
			multiDayFirstDayFormat: 'M j, Y',
			multiDayMonthStartFormat: 'M j'
		});

	if(exists('Extensible.calendar.template.Month'))
		Ext.apply(Extensible.calendar.template.Month.prototype, {
			dayHeaderFormat: 'D',
			dayHeaderTitleFormat: 'l, F j, Y'
		});

	/*
	 * Recurrence strings added in v.1.6.0
	 */
	if(exists('Extensible.form.recurrence.Rule'))
		Ext.apply(Extensible.form.recurrence.Rule.prototype, {
			strings: {
				dayNamesShort: {
					SU: 'Вс',
					MO: 'Пн',
					TU: 'Вт',
					WE: 'Ср',
					TH: 'Чт',
					FR: 'Пт',
					SA: 'Сб'
				},

				dayNamesShortByIndex: [
					'Вс',
					'Пн',
					'Вт',
					'Ср',
					'Чт',
					'Пт',
					'Сб'
				],

				dayNamesLong: {
					SU: 'Воскресенье',
					MO: 'Понедельник',
					TU: 'Вторник',
					WE: 'Среда',
					TH: 'Четверг',
					FR: 'Пятница',
					SA: 'Суббота'
				},

				ordinals: {
					1: 'первый',
					2: 'второй',
					3: 'третий',
					4: 'четвёртый',
					5: 'пятый',
					6: 'шестой'
				},

				frequency: {
					none: 'Не повторяется',
					daily: 'Ежедневно',
					weekly: 'Еженедельно',
					weekdays: 'По рабочим дням (пн-пт)',
					monthly: 'Ежемесячно',
					yearly: 'Ежегодно'
				},

				every: 'Каждые',       // e.g. Every 2 days
				days: 'дня',
				weeks: 'недели',
				weekdays: 'раб. дня',
				months: 'месяца',
				years: 'года',
				time: 'раз',        // e.g. Daily, 1 time
				times: 'раза',      // e.g. Daily, 5 times
				until: 'до',      // e.g. Daily, until Dec, 31 2012
				untilFormat: 'M j, Y', // e.g. Dec 10, 2012
				and: 'и',          // e.g. Weekly on Tuesday and Friday
				on: 'on',            // e.g. Weekly on Thursday
				onDay: 'на',     // e.g. Monthly on day 23
				onDayPostfix: 'й день',    // In some languages a postfix is need for the onDay term,
				// for example in German: 'Monatlich am 23.'
				// Here the postfix would be '.'
				onThe: 'в',     // e.g. Monthly on the first Thursday
				onTheLast: 'в последний', // e.g. Monthly on the last Friday
				onTheLastDay: 'в последний день', // e.g. Monthly on the last day
				of: '',            // e.g. Annually on the last day of November
				monthFormat: 'F',    // e.g. November
				monthDayFormat: 'F j' // e.g. November 10
			}
		});

	if(exists('Extensible.form.recurrence.FrequencyCombo'))
		Ext.apply(Extensible.form.recurrence.FrequencyCombo.prototype, {
			fieldLabel: 'Повторяется'
		});

	if(exists('Extensible.form.recurrence.RangeEditWindow'))
		Ext.apply(Extensible.form.recurrence.RangeEditWindow.prototype, {
			title: 'Настройки повторения события',
			saveButtonText: 'Сохранить',
			cancelButtonText: 'Отмена'
		});

	if(exists('Extensible.form.recurrence.RangeEditPanel'))
		Ext.apply(Extensible.form.recurrence.RangeEditPanel.prototype, {
			headerText: 'There are multiple events in this series. How would you like your changes applied?',
			optionSingleButtonText: 'Single',
			optionSingleDescription: 'Apply to this event only. No other events in the series will be affected.',
			optionFutureButtonText: 'Future',
			optionFutureDescription: 'Apply to this and all following events only. Past events will be unaffected.',
			optionAllButtonText: 'All Events',
			optionAllDescription: 'Apply to every event in this series.'
		});

	if(exists('Extensible.form.recurrence.option.Interval'))
		Ext.apply(Extensible.form.recurrence.option.Interval.prototype, {
			dateLabelFormat: 'l, F j',
			strings: {
				repeatEvery: 'Repeat every',
				beginning: 'beginning',
				day: 'day',
				days: 'days',
				week: 'week',
				weeks: 'weeks',
				month: 'month',
				months: 'months',
				year: 'year',
				years: 'years'
			}
		});

	if(exists('Extensible.form.recurrence.option.Duration'))
		Ext.apply(Extensible.form.recurrence.option.Duration.prototype, {
			strings: {
				andContinuing: 'and continuing',
				occurrences: 'occurrences',
				forever: 'forever',
				forText: 'for',
				until: 'until'
			}
		});

	if(exists('Extensible.form.recurrence.option.Weekly'))
		Ext.apply(Extensible.form.recurrence.option.Weekly.prototype, {
			strings: {
				on: 'on'
			}
		});

	if(exists('Extensible.form.recurrence.option.Monthly'))
		Ext.apply(Extensible.form.recurrence.option.Monthly.prototype, {
			strings: {
				// E.g. "on the 15th day of each month/year"
				onThe: 'on the',
				ofEach: 'of each',
				inText: 'in',
				day: 'day',
				month: 'month',
				year: 'year',
				last: 'last',
				lastDay: 'last day',
				monthDayDateFormat: 'jS',
				nthWeekdayDateFormat: 'S' // displays the ordinal postfix, e.g. th for 5th.

			}
		});
});

