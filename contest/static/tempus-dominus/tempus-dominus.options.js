var tdOptions = {
    restrictions: {
        minDate: undefined,
        maxDate: undefined,
        disabledDates: [],
        enabledDates: [],
        daysOfWeekDisabled: [],
        disabledTimeIntervals: [],
        disabledHours: [],
        enabledHours: []
    },
    display: {
        icons: {
            type: 'icons',
            time: 'fa fa-clock-o fa-fw',
            date: 'fa fa-calendar fa-fw',
            up: 'fa fa-chevron-up fa-fw',
            down: 'fa fa-chevron-down fa-fw',
            previous: 'fa fa-chevron-left fa-fw',
            next: 'fa fa-chevron-right fa-fw',
            today: 'fa fa-map-marker fa-fw',
            clear: 'fa fa-refresh fa-fw',
            close: 'fa fa-times fa-fw'
        },
        sideBySide: false,
        calendarWeeks: false,
        viewMode: 'calendar',
        toolbarPlacement: 'bottom',
        keepOpen: false,
        buttons: {
            today: true,
            clear: false,
            close: false
        },
        components: {
            calendar: true,
            date: true,
            month: true,
            year: true,
            decades: true,
            clock: true,
            hours: true,
            minutes: true,
            seconds: false,
            useTwentyfourHour: true
        },
        inline: false,
        theme: 'light'
    },
    stepping: 1,
    useCurrent: false,
    defaultDate: undefined,
    localization: {
        today: 'Выбрать сегодня',
        clear: 'Очистить',
        close: 'Закрыть',
        selectMonth: 'Выберите месяц',
        previousMonth: 'Предыдущий месяц',
        nextMonth: 'Следующий месяц',
        selectYear: 'Выберите год',
        previousYear: 'Предыдущий год',
        nextYear: 'Следующий год',
        selectDecade: 'Выберите десятилетие',
        previousDecade: 'Предыдущее десятилетие',
        nextDecade: 'Следующее десятилетие',
        previousCentury: 'Предыдущий век',
        nextCentury: 'Следующий век',
        pickHour: 'Выберите час',
        incrementHour: 'Увеличить часы',
        decrementHour: 'Уменьшить часы',
        pickMinute: 'Выберите минуту',
        incrementMinute: 'Увеличить минуты',
        decrementMinute: 'Уменьшить минуты',
        pickSecond: 'Выберите секунду',
        incrementSecond: 'Увеличить секунды',
        decrementSecond: 'Уменьшить секунды',
        toggleMeridiem: 'Переключить период',
        selectTime: 'Выберите время',
        selectDate: 'Выберите дату',
        dayViewHeaderFormat: {month: 'long', year: '2-digit'},
        locale: 'ru',
        startOfTheWeek: 1,
        dateFormats: {
            LT: 'H:mm',
            LTS: 'H:mm:ss',
            L: 'DD.MM.YYYY',
            LL: 'D MMMM YYYY г.',
            LLL: 'D MMMM YYYY г., H:mm',
            LLLL: 'dddd, D MMMM YYYY г., H:mm'
        },
        ordinal: (n) => n,
        format: 'L LT'
    },
    keepInvalid: false,
    debug: false,
    allowInputToggle: false,
    //viewDate: new DateTime(),
    multipleDates: false,
    multipleDatesSeparator: '; ',
    promptTimeOnDateChange: false,
    promptTimeOnDateChangeTransitionDelay: 200,
    meta: {},
    container: undefined
}
