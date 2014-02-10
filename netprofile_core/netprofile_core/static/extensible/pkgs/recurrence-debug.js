/*!
 * Extensible 1.6.0-rc.1
 * Copyright(c) 2010-2013 Extensible, LLC
 * licensing@ext.ensible.com
 * http://ext.ensible.com
 */
/**
 * Represents an iCalendar recurrence rule and parses recurrence rule strings
 * to generate a textual description of each recurrence rule for human readability.
 *
 * Note that currently only a subset of the iCalendar recurrence rule attributes are supported.
 * They are `FREQ`, `INTERVAL`, `BYDAY`, `BYMONTHDAY`, `BYMONTH`, `COUNT` and `UNTIL`.
 *
 * Portions of this implementation were inspired by the recurrence rule parser of [Vincent Romagnoli][1].
 *
 * Reference documentation is at [http://www.ietf.org/rfc/rfc2445.txt][2],
 * although a more practical guide can be found at [http://www.kanzaki.com/docs/ical/rrule.html][3].
 * 
 * Authored by [Gabriel Sidler][4]
 * 
 * [1]: https://github.com/skyporter/rrule_parser
 * [2]: http://www.ietf.org/rfc/rfc2445.txt
 * [3]: http://www.kanzaki.com/docs/ical/rrule.html
 * [4]: http://teamup.com
 * 
 * @author Gabriel Sidler
 */
Ext.define('Extensible.form.recurrence.Rule', {
    config: {
        /**
         * @cfg {String} dateValueFormat
         * The date string format to return in the RRULE (defaults to 'Ymd\\THis\\Z'). This is the standard
         * ISO-style iCalendar date format (e.g. January 31, 2012, 14:00 would be formatted as: "20120131T140000Z")
         * and should not typically be changed. Note that per the iCal specification, date values should always be
         * specified in UTC time format, which is why the format string ends with 'Z'.
         */
        dateValueFormat: 'Ymd\\THis\\Z',
        /**
         * @cfg {String} rule
         * A recurrence rule string conforming to the standard iCalendar RRULE/EXRULE format, e.g.
         * "FREQ=WEEKLY;INTERVAL=2;COUNT=10;" (default is null).
         */
        rule: null,
        /**
         * @cfg {Date/String} startDate
         * Optional start date for the recurrence rule (default is null). Not required just to parse the RRULE
         * values, but it is required in conjunction with the RRULE to calculate specific recurring date instances,
         * or to provide accurate textual descriptions for certain rules when calling {@link #getDescription}.
         * May be provided as a Date object, or as a string that can be parsed as a valid date.
         */
        startDate: null,
        /**
         * @cfg {Number} frequency
         * The value of the FREQ attribute of the recurrence rule, or null if no recurrence rule has been set
         * (default is null). Supported string values are "DAILY", "WEEKLY", "MONTHLY" and "YEARLY".
         */
        frequency: null,
        /**
         * @cfg {Number} count
         * The value of the COUNT attribute of the recurrence rule, or null if the recurrence rule has no COUNT
         * attribute or if no recurrence rule has been set (default is null). Supported values are any integer >= 1.
         */
        count: null,
        /**
         * @cfg {Date} until
         * The value of the UNTIL attribute of the recurrence rule as a Date object, or null if the recurrence
         * rule has no UNTIL attribute or if no recurrence rule has been set (default is null).
         * Note that per the iCal specification, this date should always be specified in UTC time format (which
         * is why the {@link #dateValueFormat} always ends with 'Z').
         */
        until: null,
        /**
         * @cfg {Number} interval
         * The value of the INTERVAL attribute of the recurrence rule, defaults to 1. Supported values are
         * any integer >= 1.
         */
        interval: 1,
        /**
         * @cfg {String} byDay
         * The value of the BYDAY attribute of the recurrence rule, or null if the recurrence rule has no
         * BYDAY attribute or if no recurrence rule has been set (default is null).
         *
         * The BYDAY attribute can contain 3 different types of values:
         *
         *	* A comma-delimited string of 2-character weekday abbreviations, e.g. 'MO,TU,FR,SU'
         *	* A numbered weekday abbreviation that can be positive or negative, e.g. '4TH' or '-1FR'
         *	* An integer day offset from the start or end of the period, e.g. 3, 20 or -10.
         *
         * See also {@link #byDayWeekdays} and {@link #byDayNumberedWeekday} for more
         * information about how these values are used.
         */
        byDay: null,
        /**
         * @cfg {String} byDayWeekdays
         * A comma separated list of abbreviated weekday names representing the days of the week on which
         * the recurrence pattern should repeat (e.g. ['TU', 'TH', 'FR']), or null if not applicable (default).
         */
        byDayWeekdays: null,
        /**
         * @cfg {Number} byMonthDay
         * The value of the BYMONTHDAY attribute of the recurrence rule or null if the recurrence rule has no
         * BYMONTHDAY attribute, or if no recurrence rule has been set (default is null). This value is an integer
         * relative offset from the start or end of the month (e.g. 10 means "the 10th day of the month", or -5
         * means "the 5th to last day of the month"). Supported values are between 1 and 31, or between -31 and -1.
         */
        byMonthDay: null,
        /**
         * @cfg {Number} byMonth
         * The value of the BYMONTH attribute of the recurrence rule or null if the recurrence rule has no
         * BYMONTH attribute, or if no recurrence rule has been set (default is null). Supported values are
         * integers between 1 and 12 corresponding to the months of the year from January to December.
         */
        byMonth: null,
        /**
         * @cfg {Object} strings
         * Strings used to generate plain text descriptions of the recurrence rule. There are a lot of strings and
         * they are not individually documented since typically they will be defined in locale files, and not
         * overridden as typical configs (though you could also do that). For complete details see the source code
         * or look at the locale files.
         */
        strings: {
            dayNamesShort: {
                SU: 'Sun',
                MO: 'Mon',
                TU: 'Tue',
                WE: 'Wed',
                TH: 'Thu',
                FR: 'Fri',
                SA: 'Sat'
            },

            dayNamesShortByIndex: {
                0: 'Sun',
                1: 'Mon',
                2: 'Tue',
                3: 'Wed',
                4: 'Thu',
                5: 'Fri',
                6: 'Sat'
            },

            dayNamesLong: {
                SU: 'Sunday',
                MO: 'Monday',
                TU: 'Tuesday',
                WE: 'Wednesday',
                TH: 'Thursday',
                FR: 'Friday',
                SA: 'Saturday'
            },
            
            ordinals: {
                1: 'first',
                2: 'second',
                3: 'third',
                4: 'fourth',
                5: 'fifth',
                6: 'sixth'
            },
            
            frequency: {
                none: 'Does not repeat',
                daily: 'Daily',
                weekly: 'Weekly',
                weekdays: 'Every weekday (Mon-Fri)',
                monthly: 'Monthly',
                yearly: 'Yearly'
            },
            
            every: 'Every',       // e.g. Every 2 days
            days: 'days',
            weeks: 'weeks',
            weekdays: 'weekdays',
            months: 'months',
            years: 'years',
            time: 'time',        // e.g. Daily, 1 time
            times: 'times',      // e.g. Daily, 5 times
            until: 'until',      // e.g. Daily, until Dec, 31 2012
            untilFormat: 'M j, Y', // e.g. Dec 10, 2012
            and: 'and',          // e.g. Weekly on Tuesday and Friday
            on: 'on',            // e.g. Weekly on Thursday
            onDay: 'on day',     // e.g. Monthly on day 23
            onDayPostfix: '',    // In some languages a postfix is need for the onDay term,
                                 // for example in German: 'Monatlich am 23.'
                                 // Here the postfix would be '.'
            onThe: 'on the',     // e.g. Monthly on the first Thursday
            onTheLast: 'on the last', // e.g. Monthly on the last Friday
            onTheLastDay: 'on the last day', // e.g. Monthly on the last day
            of: 'of',            // e.g. Annually on the last day of November
            monthFormat: 'F',    // e.g. November
            monthDayFormat: 'F j' // e.g. November 10
        }
    },
    
    /**
     * @private
     * @property byDayNames
     * @type Array[String]
     * The abbreviated day names used in "by*Day" recurrence rules. These values are used when creating
     * the RRULE strings and should not be modified (they are not used for localization purposes).
     */
    byDayNames: [ "SU", "MO", "TU", "WE", "TH", "FR", "SA" ],
    
    /**
     * @private
     */
    constructor: function(config) {
        // Have to do this manually since we are not extending Ext.Component, otherwise
        // the configs will never get initialized:
        return this.initConfig(config);
    },

    /**
     * Initializes recurrence rule and attributes
     */
    init: function()  {
        var me = this;

        me.startDate = null;
        me.frequency = null;
        me.count = null;
        me.until = null;
        me.interval = 1;
        me.byDay = null;
        me.byDayWeekdays = null;
        me.byDayNthWeekday = null;
        me.byMonthDay = null;
        me.byMonth = null;
    },

    /**
     * @private
     */
    applyStartDate: function(dt) {
        this.startDate = new Date(dt);
    },
    
    /**
     * @private
     */
    applyFrequency: function(freq) {
        this.init();
        this.frequency = freq;
    },

    /**
     * @private
     */
    applyCount: function(count) {
        // Only one of UNTIL and COUNT are allowed. Therefore need to clear UNTIL attribute.
        this.until = null;
        this.count = count;
    },
    
    /**
     * @private
     * Transforms the string value of the UNTIL attribute to a Date object if needed.
     * @param {Date/String} until A Date object or a string in the standard ISO-style iCalendar
     * date format, e.g. January 31, 2012, 14:00 would be formatted as: "20120131T140000Z". See section 4.3.5 in
     * the iCalendar specification at http://www.ietf.org/rfc/rfc2445.txt.
     */
    applyUntil: function(until) {
        // Only one of UNTIL and COUNT are allowed. Therefore, clear COUNT attribute.
        this.count = this.until = null;

        if (Ext.isDate(until)) {
            this.until = until;
        }
        else if (typeof until === 'string') {
            this.until = this.parseDate(until);
        }
    },
    
    /**
     * Parses a date string in {@link #dateValueFormat iCal format} and returns a Date object if possible. This
     * method is the inverse of {@link #formatDate}.
     * @param {String} dateString A date string in {@link #dateValueFormat iCal format}
     * @param {Object} options An optional options object. This can contain:
     *
     *	A String <tt>format</tt> property to override the default {@link #dateValueFormat} used when parsing the string (not recommended)
     *	A Boolean <tt>strict</tt> property that gets passed to the {@link Ext.Date.parse} method to determine whether or not strict date parsing should be used (defaults to false)
     *	A Date <tt>defaultValue</tt> property to be used in case the string cannot be parsed as a valid date (defaults to the current date)
     *
     * @returns {Date} The corresponding Date object
     */
    parseDate: function(dateString, options) {
        options = options || {};
        
        try {
            var date = Ext.Date.parse(dateString, options.format || this.dateValueFormat, options.strict);
            if (date) {
                return date;
            }
        }
        catch(ex) {}
        
        return options.defaultValue || new Date();
    },
    
    /**
     * Formats a Date object into a date string in {@link #dateValueFormat iCal format}. This method is the
     * inverse of {@link #parseDate}.
     * @param {Date} date The Date object to format
     * @returns {String} The corresponding date string
     */
    formatDate: function(date) {
        return Ext.Date.format(date, this.dateValueFormat);
    },

    /**
     * @private
     * Applies the value of the BYDAY attribute to the underlying RRULE.
     * @param {String/Array/Object} byDay The new value of the BYDAY attribute. There are three ways to pass a
     * parameter value:
     * 
     *	1. As a string, e.g. 'MO,TU,WE' or '3TH' or '-1FR'
     *	2. As an array of weekday identifiers, e.g. ['MO', 'TU', 'WE']. 
     *	3. As an object with two attributes *number* and *weekday*, e.g. 
     *		
     *			{ number: 4, weekday:'TH' }
     * 
     *	or
     *  
     *			{ number: -1, weekday:'WE' }
     */
    applyByDay: function(byDay) {
        var me = this;
        // Only one of BYDAY and BYMONTHDAY are allowed. Clear BYMONTHDAY.
        me.byMonthDay = null;

        // Reset derived attributes
        me.byDayWeekdays = null;
        me.byDayNthWeekday = null;

        if (typeof byDay === 'string') {
            me.byDay = byDay;

            // There are three cases to consider.
            var n = parseInt(byDay, 10);
            
            if (Ext.isNumber(n)) {
                if (n === -1 ) {
                    // The last weekday of period was specified, e.g. -1SU, -1MO, ... -1SA.
                    me.byDayNthWeekday = {number: n, weekday: byDay.substr(2, 2)};
                }
                else {
                    // A numbered weekday was specified, e.g. 1SU, 2SU, ... 5SA
                    me.byDayNthWeekday = {number: n, weekday: byDay.substr(1, 2)};
                }
            }
            else {
                // A comma separated list of weekdays was specified, e.g. MO,TU,FR
                me.byDayWeekdays = byDay.split(",");
            }
        }
        else if (Array.isArray(byDay)) {
            // byDay is an array with a list of weekdays, e.g. ['MO', 'TU', 'FR']
            me.byDay = byDay.join(',');
            me.byDayWeekdays = byDay;
        }
        else if (Ext.isObject(byDay)) {
            // byDay is an object with two properties number and weekday, e.g. {number: 4, weekday: 'TH'}
            me.byDay = byDay.number + byDay.weekday;
            me.byDayNthWeekday = byDay;
        }
    },

    /**
     * If attribute BYDAY of the recurrence rule holds a numbered weekday following iCal relative syntax
     * (e.g. '4TU' meaning "the fourth Tuesday of the month") then this function returns an Object with two
     * attributes *number* and *weekday* (e.g. {number: 4, weekday: 'TU'}), otherwise this method
     * returns null. This object is provided as a convenience when accessing the individual parts of the value.
     * For iCal RRULE representation the {@link #getByDay BYDAY} string should always be used instead.
     * Use function {@link #setByDay} to set the underlying values.
     */
    getByDayNthWeekday: function() {
        return this.byDayNthWeekday;
    },

    /**
     * @private
     * Sets the value of the BYMONTHDAY attribute of the RRULE.
     * @param {int} day Supported values are -1 and 1 to 31.
     */
    applyByMonthDay: function(day) {
        // Only one of BYDAY and BYMONTHDAY are allowed. Clear BYDAY and derived attributes.
        this.byDay = null;
        this.byDayWeekdays = null;
        this.byDayNthWeekday = null;
        this.byMonthDay = day;
    },
    
    /**
     * Returns a textual representation of the underlying rules in [iCal RRULE format](http://www.kanzaki.com/docs/ical/rrule.html), 
     * e.g. "FREQ=WEEKLY;INTERVAL=2;". This is the standard format that is typically 
     * used to store and transmit recurrence rules between systems.
     * @returns {String} The iCal-formatted RRULE string, or empty string if a valid RRULE cannot be returned
     */
    getRule: function() {
        var rule = [],
            me = this;
        
        if (!me.frequency) {
            return '';
        }
        rule.push('FREQ=' + me.frequency);
        
        if (me.interval !== 1) {
            rule.push('INTERVAL=' + me.interval);
        }
        if (me.byDay) {
            rule.push('BYDAY=' + me.byDay);
        }
        if (me.byMonthDay) {
            rule.push('BYMONTHDAY=' + me.byMonthDay);
        }
        if (me.byMonth) {
            rule.push('BYMONTH=' + me.byMonth);
        }
        if (me.count) {
            rule.push('COUNT=' + me.count);
        }
        if (me.until) {
            rule.push('UNTIL=' + Ext.Date.format(me.until, me.dateValueFormat));
        }
        return rule.join(';') + ';';
    },

    /**
     * @private
     * Parses a recurrence rule string conforming to the iCalendar standard. Note that currently only the following
     * recurrence rule attributes are supported: FREQ, INTERVAL, BYDAY, BYMONTHDAY, BYMONTH, COUNT and UNTIL.
     *
     * This function can be used to set a new rule or update an existing rule. If rule attribute FREQ is present
     * in the passed recurrence rule string, then the rule is initialized first before rule properties are set. If
     * rule attribute FREQ is not present, then the rule properties are updated without first initializing the rule.
     *
     * @param {String} rRule iCalendar recurrence rule as a text string. E.g. "FREQ=WEEKLY;INTERVAL=2;"
     */
    applyRule: function(rRule) {
        var rrParams, nbParams, p, v,
            i = 0,
            me = this;
        
        if (!rRule) {
            this.init();
            return;
        }
        rrParams = rRule.split(";");
        nbParams = rrParams.length;

        // Process the FREQ attribute first because this initializes the rule.
        for (; i < nbParams; i++) {
            p = rrParams[i].split("=");
            if (p[0] === "FREQ") {
                me.setFrequency(p[1]); // This will initialize the rule.
                break;
            }
        }

        // Now process all attributes except the FREQ attribute.
        for (i = 0; i < nbParams; i++) {
            p = rrParams[i].split("=");
            v = p[1];
            
            switch (p[0]) {
                case 'INTERVAL':
                    me.setInterval(parseInt(v, 10));
                    break;
                case 'COUNT':
                    me.setCount(parseInt(v, 10));
                    break;
                case 'UNTIL':
                    me.setUntil(v);
                    break;
                case 'BYDAY':
                    me.setByDay(v);
                    break;
                case 'BYMONTHDAY':
                    me.setByMonthDay(parseInt(v, 10));
                    break;
                case 'BYMONTH':
                    me.setByMonth(parseInt(v, 10));
                    break;
            }
        }
    },

    /**
     * Return a textual description of the iCalendar recurrence rule. E.g. the rule "FREQ=DAILY;INTERVAL=2;COUNT=5"
     * is returned as the text "Every 2 days, 5 times".
     * @param {Date} [startDate] Optional start date of the event series, only required for certain rule types
     * (e.g., any rule that is specified as date-relative like "BYDAY=-1FR" can only be represented relative
     * to a specific start date).
     * @return {String} The textual description
     */
    getDescription: function(startDate) {
        var me = this,
            desc = [],
            freq = me.frequency ? Ext.String.capitalize(me.frequency.toLowerCase()) : '';

        startDate = startDate || this.startDate;
        
        if (freq && me['getDescription' + freq]) {
            me['getDescription' + freq](desc, startDate);
        }
        me.getDescriptionCount(desc, startDate);
        me.getDescriptionUntil(desc, startDate);

        return desc.join('');
    },
    
    /**
     * @protected
     * Returns the description if the rule is of type "FREQ=DAILY".
     * May be overridden to customize the output strings, especially for localization.
     * @param {Array[String]} desc An array of strings representing the rule description parts collected
     * so far. This array is passed around, and each method should typically append any needed strings to
     * it. After all logic is complete, the array will be joined and the final description returned.
     * @param {Date} [startDate] The start date of the recurring series (optional).
     */
    getDescriptionDaily: function(desc, startDate) {
        var me = this,
            strings = me.strings;
        
        if (me.interval === 1) {
            // E.g. Daily
            desc.push(strings.frequency.daily);
        }
        else {
            // E.g. Every 2 days
            desc.push(strings.every, ' ', me.interval, ' ', strings.days);
        }
    },
    
    /**
     * @protected
     * Returns the description if the rule is of type "FREQ=WEEKLY".
     * May be overridden to customize the output strings, especially for localization.
     * @param {Array[String]} desc An array of strings representing the rule description parts collected
     * so far. This array is passed around, and each method should typically append any needed strings to
     * it. After all logic is complete, the array will be joined and the final description returned.
     * @param {Date} [startDate] The start date of the recurring series (optional).
     */
    getDescriptionWeekly: function(desc, startDate) {
        var me = this,
            strings = me.strings;
        
        if (me.interval === 1) {
            // E.g. Weekly
            desc.push(strings.frequency.weekly);
        }
        else {
            // E.g. Every 2 weeks
            desc.push(strings.every, ' ', me.interval, ' ', strings.weeks);
        }

        // Have specific weekdays been specified? E.g. Weekly on Tuesday, Wednesday and Thursday
        if (me.byDayWeekdays) {
            var len = me.byDayWeekdays.length;
            
            desc.push(' ', strings.on, ' ');
            
            for (var i=0; i < len; i++) {
                if (i > 0 && i < len-1) {
                    desc.push(', ');
                }
                else if (len > 1 && i === len-1) {
                    desc.push(' ', strings.and, ' ');
                }
                // If more than 2 weekdays have been specified, use short day names, otherwise long day names.
                if (len > 2) {
                    desc.push(strings.dayNamesShort[me.byDayWeekdays[i]]);
                }
                else {
                    desc.push(strings.dayNamesLong[me.byDayWeekdays[i]]);
                }
            }
        }
        else if (startDate) {
            // No weekdays are specified. Use weekday of parameter startDate as the weekday. E.g. Weekly on Monday
            desc.push(' ', strings.on, ' ', strings.dayNamesLong[me.byDayNames[startDate.getDay()]]);
        }
    },
    
    /**
     * @protected
     * Returns the description if the rule is of type "FREQ=WEEKDAYS". Note that WEEKDAYS is not
     * part of the iCal standard -- it is a special frequency value supported by Extensible as a shorthand
     * that is commonly used in applications. May be overridden to customize the output strings, especially
     * for localization.
     * @param {Array[String]} desc An array of strings representing the rule description parts collected
     * so far. This array is passed around, and each method should typically append any needed strings to
     * it. After all logic is complete, the array will be joined and the final description returned.
     * @param {Date} [startDate] The start date of the recurring series (optional).
     */
    getDescriptionWeekdays: function(desc, startDate) {
        if (this.interval === 1) {
            desc.push(this.strings.frequency.weekdays);
        }
        else {
            // E.g. Every two weekdays
            desc.push(this.strings.every, ' ', this.interval, ' ', this.strings.weekdays);
        }
    },
    
    /**
     * @protected
     * Returns the description if the rule is of type "FREQ=MONTHLY".
     * May be overridden to customize the output strings, especially for localization.
     * @param {Array[String]} desc An array of strings representing the rule description parts collected
     * so far. This array is passed around, and each method should typically append any needed strings to
     * it. After all logic is complete, the array will be joined and the final description returned.
     * @param {Date} [startDate] The start date of the recurring series (optional).
     */
    getDescriptionMonthly: function(desc, startDate) {
        var me = this,
            strings = me.strings;
        
        if (me.interval === 1) {
            // E.g. Monthly
            desc.push(strings.frequency.monthly);
        }
        else {
            // E.g. Every 2 months
            desc.push(strings.every, ' ', me.interval, ' ', strings.months);
        }

        if (me.byMonthDay > 0) {
            // A specific month day has been selected, e.g. Monthly on day 23.
            desc.push(' ' + strings.onDay + ' ' + me.byMonthDay + strings.onDayPostfix);
        }
        else if (me.byMonthDay === -1) {
            // The last day of the month has been selected, e.g. Monthly on the last day.
            desc.push(' ' + strings.onTheLastDay);
        }
        else if (me.byDayNthWeekday) {
            // A numbered weekday of the month has been selected, e.g. Monthly on the first Monday
            if (me.byDayNthWeekday.number > 0) {
                desc.push(' ', strings.onThe, ' ', strings.ordinals[me.byDayNthWeekday.number], ' ',
                    strings.dayNamesLong[me.byDayNthWeekday.weekday]);
            }
            else {
                // Last weekday of the month has been selected, e.g. Monthly on the last Sunday
                desc.push(' ' + strings.onTheLast + ' ' + strings.dayNamesLong[me.byDayNthWeekday.weekday]);
            }
        }
    },
    
    /**
     * @protected
     * Returns the description if the rule is of type "FREQ=YEARLY".
     * May be overridden to customize the output strings, especially for localization.
     * @param {Array[String]} desc An array of strings representing the rule description parts collected
     * so far. This array is passed around, and each method should typically append any needed strings to
     * it. After all logic is complete, the array will be joined and the final description returned.
     * @param {Date} [startDate] The start date of the recurring series (optional).
     */
    getDescriptionYearly: function(desc, startDate) {
        var me = this,
            strings = me.strings;
        
        if (me.interval === 1) {
            // E.g. Yearly
            desc.push(strings.frequency.yearly);
        }
        else {
            // E.g. Every two years
            desc.push(strings.every, ' ', me.interval, ' ', strings.years);
        }
        
        if (!startDate) {
            // StartDate is required for formatting beyond this point
            return;
        }
        
        if (me.byMonthDay === -1) {
            // The last day of the month, e.g. Annually on the last day of November.
            desc.push(' ', strings.onTheLastDay, ' ', strings.of, ' ', Ext.Date.format(startDate, strings.monthFormat));
        }
        else if (me.byDayNthWeekday) {
            // A numbered weekday of the month has been selected, e.g. Monthly on the first Monday
            if (me.byDayNthWeekday.number > 0) {
                // A numbered weekday of the month, e.g. Annually on the second Wednesday of November.
                desc.push(' ', strings.onThe, ' ', strings.ordinals[me.byDayNthWeekday.number], ' ',
                    strings.dayNamesLong[me.byDayNthWeekday.weekday], ' ', strings.of, ' ',
                    Ext.Date.format(startDate, strings.monthFormat));
            }
            else {
                // Last weekday of the month, e.g. Annually on the last Sunday of November
                desc.push(' ', strings.onTheLast, ' ', strings.dayNamesLong[me.byDayNthWeekday.weekday], ' ',
                    strings.of, ' ', Ext.Date.format(startDate, strings.monthFormat));
            }
        }
        else {
            // Yearly on the current start date of the current start month, e.g. Annually on November 27
            desc.push(' ', strings.on, ' ', Ext.Date.format(startDate, strings.monthDayFormat));
        }
    },
    
    /**
     * @protected
     * Returns the description only for the "COUNT=5" portion of the rule (e.g., "5 times").
     * May be overridden to customize the output strings, especially for localization.
     * @param {Array[String]} desc An array of strings representing the rule description parts collected
     * so far. This array is passed around, and each method should typically append any needed strings to
     * it. After all logic is complete, the array will be joined and the final description returned.
     * @param {Date} [startDate] The start date of the recurring series (optional).
     */
    getDescriptionCount: function(desc, startDate) {
        if (this.count) {
            // E.g. Daily, 5 times
            desc.push(', ', this.count, ' ', (this.count === 1 ? this.strings.time : this.strings.times));
        }
    },
    
    /**
     * @protected
     * Returns the description only for the "UNTIL" portion of the rule.
     * May be overridden to customize the output strings, especially for localization.
     * @param {Array[String]} desc An array of strings representing the rule description parts collected
     * so far. This array is passed around, and each method should typically append any needed strings to
     * it. After all logic is complete, the array will be joined and the final description returned.
     * @param {Date} [startDate] The start date of the recurring series (optional).
     */
    getDescriptionUntil: function(desc, startDate) {
        if (this.until) {
            // E.g. Daily, until December 31, 2012
            desc.push(', ', this.strings.until, ' ', Ext.Date.format(this.until, this.strings.untilFormat));
        }
    }
});
/**
 * A global instance of Extensible.form.recurrence.Rule.
 * @singleton
 * 
 */
Ext.define('Extensible.form.recurrence.Parser', {
    extend: 'Extensible.form.recurrence.Rule',
    singleton: true
});
/**
 * The abstract base class for all of the recurrence option widgets. Intended to be subclassed.
 * 
 * @private
 */
Ext.define('Extensible.form.recurrence.AbstractOption', {
    
    // TODO: Create Extensible.form.recurrence.Parser and factor all
    //       rrule value getting/setting out of these option classes
    //       and into the parser.
    
    extend: 'Ext.form.FieldContainer',
    
    requires: [
        'Extensible.form.recurrence.Rule'
    ],
    
    mixins: {
        field: 'Ext.form.field.Field'
    },
    
    layout: 'hbox',
    
    defaults: {
        margins: '0 5 0 0'
    },
    
    /**
     * @cfg {Extensible.form.recurrence.Rule} rrule
     * The {@link Extensible.form.recurrence.Rule recurrence Rule} instance underlying this recurrence
     * option widget. This is typically set by the parent {@link Extensible.form.recurrence.Fieldset fieldset}
     * so that the same instance is shared across option widgets.
     */
    rrule: undefined,
    /**
     * @cfg {Date} startDate
     * The start date of the underlying recurrence series. This is not always required, depending on the specific
     * recurrence rules in effect, and will default to the current date if required and not supplied. Like the
     * {@link #rrule} config, this is typically set by the parent {@link Extensible.form.recurrence.Fieldset fieldset}.
     */
    startDate: undefined,
    /**
     * @cfg {Number} startDay
     * The 0-based index for the day on which the calendar week begins (0=Sunday, which is the default).
     * Used anytime a calendar or date picker is displayed within the recurrence options.
     */
    startDay: 0,
    /**
     * Maximum end date allowed when choosing dates from date fields (defaults to 12/31/9999).
     */
    maxEndDate: new Date('12/31/9999'),
    
    key: undefined,
    
    optionDelimiter: ';', //TODO: remove
    
    initComponent: function() {
        var me = this;
        
        me.addEvents(
            /**
             * @event change
             * Fires when a user-initiated change is detected in the value of the field.
             * @param {Extensible.form.recurrence.AbstractOption} this
             * @param {Mixed} newValue The new value
             * @param {Mixed} oldValue The old value
             */
            'change'
        );
        
        me.initRRule();
        me.items = me.getItemConfigs();
        
        me.callParent(arguments);
        
        me.initRefs();
        me.initField();
    },
    
    initRRule: function() {
        var me = this;
        
        me.rrule = me.rrule || Ext.create('Extensible.form.recurrence.Rule');
        me.startDate = me.startDate || me.rrule.startDate || Extensible.Date.today();
        
        if (!me.rrule.startDate) {
            me.rrule.setStartDate(me.startDate);
        }
    },
    
    afterRender: function() {
        this.callParent(arguments);
        this.updateLabel();
    },
    
    initRefs: Ext.emptyFn,
    
    setFrequency: function(freq) {
        this.frequency = freq;
    },
    
    setStartDate: function(dt) {
        this.startDate = dt;
        return this;
    },
    
    getStartDate: function() {
        return this.startDate || Extensible.Date.today();
    },
    
    getDefaultValue: function() {
        return '';
    },
    
    preSetValue: function(v, readyField) {
        var me = this;
        
        if (!v) {
            v = me.getDefaultValue();
        }
        if (!readyField) {
            me.on('afterrender', function() {
                me.setValue(v);
            }, me, {single: true});
            return false;
        }
        
        me.value = v;
        
        return true;
    }
});/**
 * The widget that represents the duration portion of an RRULE.
 */
Ext.define('Extensible.form.recurrence.option.Duration', {
    extend: 'Extensible.form.recurrence.AbstractOption',
    alias: 'widget.extensible.recurrence-duration',
    
    requires: [
        'Ext.form.Label',
        'Ext.form.field.ComboBox',
        'Ext.form.field.Number',
        'Ext.form.field.Date'
    ],
    
    /**
     * Minimum number of recurring instances to allow when the "for" option is selected (defaults to 1).
     */
    minOccurrences: 1,
    /**
     * Maximum number of recurring instances to allow when the "for" option is selected (defaults to 999).
     */
    maxOccurrences: 999,
    /**
     * @cfg {Number} defaultEndDateOffset
     * The unit of time after the start date to set the end date field when no end date is specified in the
     * recurrence rule (defaults to 5). The specific date value depends on the recurrence frequency
     * (selected in the {@link Extensible.form.recurrence.FrequencyCombo FrequencyCombo}) which is the
     * unit by which this setting is multiplied to calculate the default date. For example, if recurrence
     * frequency is daily, then the resulting date would be 5 days after the start date. However, if
     * frequency is monthly, then the date would be 5 months after the start date.
     */
    defaultEndDateOffset: 5,
    /**
     * @cfg {Number} minDateOffset
     * The number of days after the start date to set as the minimum allowable end date
     * (defaults to 1).
     */
    minDateOffset: 1,
    /**
     * Width in pixels of the duration end date field (defaults to 120)
     */
    endDateWidth: 120,
    
    strings: {
        andContinuing: 'and continuing',
        occurrences: 'occurrences',
        forever: 'forever',
        forText: 'for',
        until: 'until'
    },
    
    cls: 'extensible-recur-duration',
    
    //endDateFormat: null, // inherit by default
    
    getItemConfigs: function() {
        var me = this;
        
        return [
            me.getContinuingLabelConfig(),
            me.getDurationComboConfig(),
            me.getDurationDateFieldConfig(),
            me.getDurationNumberFieldConfig(),
            me.getOccurrencesLabelConfig()
        ];
    },
    
    getContinuingLabelConfig: function() {
        return {
            xtype: 'label',
            text: this.strings.andContinuing
        };
    },
    
    getDurationComboConfig: function() {
        var me = this;
        
        return {
            xtype: 'combo',
            itemId: me.id + '-duration-combo',
            mode: 'local',
            width: 85,
            triggerAction: 'all',
            forceSelection: true,
            value: me.strings.forever,
            
            store: [
                me.strings.forever,
                me.strings.forText,
                me.strings.until
            ],
            
            listeners: {
                'change': Ext.bind(me.onComboChange, me)
            }
        };
    },
    
    getDurationDateFieldConfig: function() {
        var me = this,
            startDate = me.getStartDate();
        
        return {
            xtype: 'datefield',
            itemId: me.id + '-duration-date',
            showToday: false,
            width: me.endDateWidth,
            format: me.endDateFormat || Ext.form.field.Date.prototype.format,
            startDay: this.startDay,
            maxValue: me.maxEndDate,
            allowBlank: false,
            hidden: true,
            minValue: Ext.Date.add(startDate, Ext.Date.DAY, me.minDateOffset),
            value: me.getDefaultEndDate(startDate),
            
            listeners: {
                'change': Ext.bind(me.onEndDateChange, me)
            }
        };
    },
    
    getDurationNumberFieldConfig: function() {
        var me = this;
        
        return {
            xtype: 'numberfield',
            itemId: me.id + '-duration-num',
            value: 5,
            width: 55,
            minValue: me.minOccurrences,
            maxValue: me.maxOccurrences,
            allowBlank: false,
            hidden: true,
            
            listeners: {
                'change': Ext.bind(me.onOccurrenceCountChange, me)
            }
        };
    },
    
    getOccurrencesLabelConfig: function() {
        return {
            xtype: 'label',
            itemId: this.id + '-duration-num-label',
            text: this.strings.occurrences,
            hidden: true
        };
    },
    
    initRefs: function() {
        var me = this;
        me.untilCombo = me.down('#' + me.id + '-duration-combo');
        me.untilDateField = me.down('#' + me.id + '-duration-date');
        me.untilNumberField = me.down('#' + me.id + '-duration-num');
        me.untilNumberLabel = me.down('#' + me.id + '-duration-num-label');
    },
    
    onComboChange: function(combo, value) {
        this.toggleFields(value);
        this.checkChange();
    },
    
    toggleFields: function(toShow) {
        var me = this;
        
        me.untilCombo.setValue(toShow);
        
        if (toShow === me.strings.until) {
            if (!me.untilDateField.getValue()) {
                me.initUntilDate();
            }
            me.untilDateField.show();
        }
        else {
            me.untilDateField.hide();
            me.untilDateIsSet = false;
        }
        
        if (toShow === me.strings.forText) {
            me.untilNumberField.show();
            me.untilNumberLabel.show();
        }
        else {
            // recur forever
            me.untilNumberField.hide();
            me.untilNumberLabel.hide();
        }
    },
    
    onOccurrenceCountChange: function(field, value, oldValue) {
        this.checkChange();
    },
    
    onEndDateChange: function(field, value, oldValue) {
        this.checkChange();
    },
    
    setStartDate: function(dt) {
        var me = this,
            value = me.getValue();
        
        if (dt.getTime() !== me.startDate.getTime()) {
            me.callParent(arguments);
            me.untilDateField.setMinValue(dt);
            
            if (!value || me.untilDateField.getValue() < dt) {
                me.initUntilDate(dt);
            }
        }
        return me;
    },
    
    setFrequency: function() {
        this.callParent(arguments);
        this.initUntilDate();
        
        return this;
    },
    
    initUntilDate: function(startDate) {
        if (!this.untilDateIsSet) {
            this.untilDateIsSet = true;
            var endDate = this.getDefaultEndDate(startDate || this.getStartDate());
            this.untilDateField.setValue(endDate);
        }
        return this;
    },
    
    getDefaultEndDate: function(startDate) {
        var options = {},
            unit;
        
        switch (this.frequency) {
            case 'WEEKLY':
            case 'WEEKDAYS':
                unit = 'weeks';
                break;
            
            case 'MONTHLY':
                unit = 'months';
                break;
            
            case 'YEARLY':
                unit = 'years';
                break;
            
            default:
                unit = 'days';
        }
        
        options[unit] = this.defaultEndDateOffset;
        
        return Extensible.Date.add(startDate, options);
    },
    
    getValue: function() {
        var me = this;
        
        // sanity check that child fields are available first
        if (me.untilCombo) {
            if (me.untilNumberField.isVisible()) {
                return 'COUNT=' + me.untilNumberField.getValue();
            }
            if (me.untilDateField.isVisible()) {
                return 'UNTIL=' + me.rrule.formatDate(this.adjustUntilDateValue(me.untilDateField.getValue()));
            }
        }
        return '';
    },
    
    /**
     * If a recurrence UNTIL date is specified, it must be inclusive of all times on that date. By default
     * the returned date value is incremented by one day minus one second to ensure that.
     * @param {Object} untilDate The raw UNTIL date value returned from the untilDateField
     * @return {Date} The adjusted Date object
     */
    adjustUntilDateValue: function(untilDate) {
        return Extensible.Date.add(untilDate, {days: 1, seconds: -1});
    },
    
    setValue: function(v) {
        var me = this;
        
        if (!me.preSetValue(v, me.untilCombo)) {
            return me;
        }
        if (!v) {
            me.toggleFields(me.strings.forever);
            return me;
        }
        var options = Ext.isArray(v) ? v : v.split(me.optionDelimiter),
            didSetValue = false,
            parts;

        Ext.each(options, function(option) {
            parts = option.split('=');
            
            if (parts[0] === 'COUNT') {
                me.untilNumberField.setValue(parts[1]);
                me.toggleFields(me.strings.forText);
                didSetValue = true;
                return;
            }
            if (parts[0] === 'UNTIL') {
                me.untilDateField.setValue(me.rrule.parseDate(parts[1]));
                // If the min date is updated before this new value gets set it can sometimes
                // lead to a false validation error showing even though the value is valid. This
                // is a simple hack to essentially refresh the min value validation now:
                me.untilDateField.validate();
                me.toggleFields(me.strings.until);
                didSetValue = true;
                return;
            }
        }, me);
        
        if (!didSetValue) {
            me.toggleFields(me.strings.forever);
        }
        
        return me;
    }
});
/**
 * The widget that represents the interval portion of an RRULE.
 */
Ext.define('Extensible.form.recurrence.option.Interval', {
    extend: 'Extensible.form.recurrence.AbstractOption',
    alias: 'widget.extensible.recurrence-interval',
    
    dateLabelFormat: 'l, F j',
    unit: 'day',
    minValue: 1,
    maxValue: 999,
    startDateWidth: 120,
    
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
    },
    
    cls: 'extensible-recur-interval',
    
    initComponent: function() {
        this.addEvents(
            /**
             * @event startchange
             * Fires when the start date of the recurrence series is changed
             * @param {Extensible.form.recurrence.option.Interval} this
             * @param {Date} newDate The new start date
             * @param {Date} oldDate The previous start date
             */
            'startchange'
        );
        this.callParent(arguments);
    },
    
    getItemConfigs: function() {
        return [
            this.getRepeatEveryLabelConfig(),
            this.getIntervalComboConfig(),
            this.getBeginDateLabelConfig(),
            this.getBeginDateFieldConfig()
        ];
    },
    
    getRepeatEveryLabelConfig: function() {
        return {
            xtype: 'label',
            text: this.strings.repeatEvery
        };
    },
    
    getIntervalComboConfig: function() {
        var me = this;
        
        return {
            xtype: 'numberfield',
            itemId: me.id + '-interval',
            value: 1,
            width: 55,
            minValue: me.minValue,
            maxValue: me.maxValue,
            allowBlank: false,
            enableKeyEvents: true,
            listeners: {
                'change': Ext.bind(me.onIntervalChange, me)
            }
        };
    },
    
    getBeginDateLabelConfig: function() {
        return {
            xtype: 'label',
            itemId: this.id + '-date-label'
        };
    },
    
    getBeginDateFieldConfig: function() {
        var me = this,
            startDate = me.getStartDate();
        
        return {
            xtype: 'datefield',
            itemId: me.id + '-start-date',
            width: me.startDateWidth,
            // format: me.endDateFormat || Ext.form.field.Date.prototype.format,
            startDay: this.startDay,
            maxValue: me.maxEndDate,
            allowBlank: false,
            value: startDate,
            
            listeners: {
                'change': Ext.bind(me.onStartDateChange, me)
            }
        };
    },
    
    initRefs: function() {
        var me = this;
        me.intervalField = me.down('#' + me.id + '-interval');
        me.dateLabel = me.down('#' + me.id + '-date-label');
        me.startDateField = me.down('#' + me.id + '-start-date');
    },
    
    onIntervalChange: function(field, value, oldValue) {
        this.checkChange();
        this.updateLabel();
    },
    
    onStartDateChange: function(field, value, oldValue) {
        this.checkChange();
        this.fireEvent('startchange', this, value, oldValue);
    },
    
    getValue: function() {
        if (this.intervalField) {
            return 'INTERVAL=' + this.intervalField.getValue();
        }
        return '';
    },
    
    setValue: function(v) {
        var me = this;
        
        if (!me.preSetValue(v, me.intervalField)) {
            return me;
        }
        if (!v) {
            me.intervalField.setValue(me.minValue);
            return me;
        }
        var options = Ext.isArray(v) ? v : v.split(me.optionDelimiter),
            parts;

        Ext.each(options, function(option) {
            parts = option.split('=');
            
            if (parts[0] === 'INTERVAL') {
                me.intervalField.setValue(parts[1]);
                me.updateLabel();
                return;
            }
        }, me);
        
        return me;
    },
    
    setStartDate: function(dt) {
        this.startDate = dt;
        this.startDateField.setValue(dt);
        return this;
    },
    
    setUnit: function(unit) {
        this.unit = unit;
        this.updateLabel();
        return this;
    },
    
    updateLabel: function(unit) {
        var me = this;
        
        if (me.intervalField) {
            // TODO: Change this to support locale text
            var s = me.intervalField.getValue() === 1 ? '' : 's';
            me.unit = unit ? unit.toLowerCase() : me.unit || 'day';
            
            if (me.dateLabel) {
                me.dateLabel.update(me.strings[me.unit + s] + ' ' + me.strings.beginning);
            }
        }
        return me;
    }
});
/**
 * The widget that represents the monthly recurrence options of an RRULE.
 */
Ext.define('Extensible.form.recurrence.option.Monthly', {
    extend: 'Extensible.form.recurrence.AbstractOption',
    alias: 'widget.extensible.recurrence-monthly',
    
    requires: [
        'Ext.form.field.ComboBox',
        'Extensible.lang.Number'
    ],
    
    cls: 'extensible-recur-monthly',
    
    nthComboWidth: 150,
    
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
    },
    
    afterRender: function() {
        this.callParent(arguments);
        this.initNthCombo();
    },
    
    getItemConfigs: function() {
        return [
            this.getOnTheLabelConfig(),
            this.getNthComboConfig(),
            this.getOfEachLabelConfig()
        ];
    },
    
    getOnTheLabelConfig: function() {
        return {
            xtype: 'label',
            text: this.strings.onThe
        };
    },
    
    getNthComboConfig: function() {
        return {
            xtype: 'combobox',
            itemId: this.id + '-nth-combo',
            queryMode: 'local',
            width: this.nthComboWidth,
            triggerAction: 'all',
            forceSelection: true,
            displayField: 'text',
            valueField: 'value',
            store: Ext.create('Ext.data.ArrayStore', {
                fields: ['text', 'value'],
                idIndex: 0,
                data: []
            }),
            listeners: {
                'change': Ext.bind(this.onComboChange, this)
            }
        };
    },
    
    getPeriodString: function() {
        // Overridden in the Yearly option class
        return this.strings.month;
    },
    
    getOfEachLabelConfig: function() {
        return {
            xtype: 'label',
            text: this.strings.ofEach + ' ' + this.getPeriodString()
        };
    },
    
    initRefs: function() {
        this.nthCombo = this.down('#' + this.id + '-nth-combo');
    },
    
    onComboChange: function(combo, value) {
        this.checkChange();
    },
    
    setStartDate: function(dt) {
        if (dt.getTime() !== this.startDate.getTime()) {
            this.callParent(arguments);
            this.initNthCombo();
        }
        return this;
    },
    
    initNthCombo: function() {
        if (!this.rendered) {
            return;
        }
        var me = this,
            combo = me.nthCombo,
            store = combo.store,
            dt = me.getStartDate(),
            
            // e.g. 30 (for June):
            lastDayOfMonth = Ext.Date.getLastDateOfMonth(dt).getDate(),
            // e.g. "28th day":
            monthDayText = Ext.Date.format(dt, me.strings.monthDayDateFormat) + ' ' + me.strings.day,
            // e.g. 28:
            dayNum = dt.getDate(),
            // index in the month, e.g. 4 for the 4th Tuesday
            dayIndex = Math.ceil(dayNum / 7),
            // e.g. "TU":
            dayNameAbbreviated = Extensible.form.recurrence.Parser.byDayNames[dt.getDay()],

            // e.g. "4th Tuesday":
            tempDate = new Date(2000, 0, dayIndex),
            dayOfWeekText = dayIndex + Ext.Date.format(tempDate, me.strings.nthWeekdayDateFormat) + Ext.Date.format(dt, ' l'),

            // year-specific additions to the resulting value string, used if we are currently
            // executing from within the Yearly option subclass.
            // e.g. "in 2012":
            yearlyText = me.isYearly ? ' ' + me.strings.inText +' ' + Ext.Date.format(dt, 'F') : '',
            // e.g. "BYMONTH=2;":
            byMonthValue = me.isYearly ? 'BYMONTH=' + Ext.Date.format(dt, 'n') : '',
            // only use this if yearly:
            delimiter = me.isYearly ? me.optionDelimiter : '',
            
            // the first two combo items, which are always included:
            data = [
                [monthDayText + yearlyText, me.isYearly ? byMonthValue : 'BYMONTHDAY=' + dayNum],
                [dayOfWeekText + yearlyText, byMonthValue + delimiter +
                    'BYDAY=' + dayIndex + dayNameAbbreviated]
            ],
            
            // the currently selected index, which we will try to restore after refreshing the combo:
            idx = store.find('value', combo.getValue());

        if (lastDayOfMonth - dayNum < 7) {
            // the start date is the last of a particular day (e.g. last Tuesday) for the month
            data.push([me.strings.last + ' ' + Ext.Date.format(dt, 'l') + yearlyText,
                byMonthValue + delimiter + 'BYDAY=-1' + dayNameAbbreviated]);
        }
        if (lastDayOfMonth === dayNum) {
            // the start date is the last day of the month
            data.push([me.strings.lastDay + yearlyText, byMonthValue + delimiter + 'BYMONTHDAY=-1']);
        }
        
        store.removeAll();
        combo.clearValue();
        store.loadData(data);
        
        if (idx > data.length - 1) {
            // if the previously-selected index is now greater than the number of items in the
            // combo default to the last item in the new list
            idx = data.length - 1;
        }
        
        combo.setValue(store.getAt(idx > -1 ? idx : 0).data.value);
        
        return me;
    },
    
    getValue: function() {
        var me = this;
        
        if (me.nthCombo) {
            return me.nthCombo.getValue();
        }
        return '';
    },
    
    setValue: function(v) {
        var me = this;
        
        if (!me.preSetValue(v, me.nthCombo)) {
            return me;
        }
        if (!v) {
            var defaultItem = me.nthCombo.store.getAt(0);
            if (defaultItem) {
                me.nthCombo.setValue(defaultItem.data.value);
            }
            return me;
        }
        var options = Ext.isArray(v) ? v : v.split(me.optionDelimiter),
            parts,
            values = [];

        Ext.each(options, function(option) {
            parts = option.split('=');
            if (parts[0] === 'BYMONTH') {
                // if BYMONTH is present make sure it goes to the beginning of the value
                // string since that's the order the combo sets it in and they must match
                values.unshift(option);
            }
            if (parts[0] === 'BYMONTHDAY' || parts[0] === 'BYDAY') {
                // these go to the back of the value string
                values.push(option);
            }
        }, me);
        
        if (values.length) {
            me.nthCombo.setValue(values.join(me.optionDelimiter));
        }
        
        return me;
    }
});
/**
 * The widget that represents the weekly recurrence options of an RRULE.
 */
Ext.define('Extensible.form.recurrence.option.Weekly', {
    extend: 'Extensible.form.recurrence.AbstractOption',
    alias: 'widget.extensible.recurrence-weekly',
    
    requires: [
        'Ext.form.field.Checkbox', // should be required by CheckboxGroup but isn't
        'Ext.form.CheckboxGroup',
        'Extensible.form.recurrence.Parser'
    ],

    /**
     * @cfg {Number} startDay
     * The 0-based index for the day on which the calendar week begins (0=Sunday, which is the default)
     */
    startDay: 0,

    dayValueDelimiter: ',',
    
    cls: 'extensible-recur-weekly',

    strings: {
        on: 'on'
    },

    /**
     * Creates the item configuration for the checkbox group. Takes into account the week start day.
     * For example:
     *		[
     *			{ boxLabel: 'Sun', name: 'SU', id: this.id + '-SU' },
     *			{ boxLabel: 'Mon', name: 'MO', id: this.id + '-MO' },
     *			{ boxLabel: 'Tue', name: 'TU', id: this.id + '-TU' },
     *			{ boxLabel: 'Wed', name: 'WE', id: this.id + '-WE' },
     *			{ boxLabel: 'Thu', name: 'TH', id: this.id + '-TH' },
     *			{ boxLabel: 'Fri', name: 'FR', id: this.id + '-FR' },
     *			{ boxLabel: 'Sat', name: 'SA', id: this.id + '-SA' }
     *		];
     * @return {Array}
     */
    getCheckboxGroupItems: function() {
        var weekdaysId = Extensible.form.recurrence.Parser.byDayNames,
            weekdaysText = Extensible.form.recurrence.Parser.strings.dayNamesShortByIndex,
            checkboxArray = [],
            i = this.startDay;

        for (var n=0; n<7; n++) {
            checkboxArray[n] = {boxLabel: weekdaysText[i], name: weekdaysId[i], id: this.id + '-' + weekdaysId[i]};
            i = i === 6 ? 0 : i+1;
        }
        return checkboxArray;
    },


    getItemConfigs: function() {
        var id = this.id;

        return [{
            xtype: 'label',
            text: this.strings.on + ':'
        },{
            xtype: 'checkboxgroup',
            itemId: id + '-days',
            flex: 1,
            items: this.getCheckboxGroupItems(),
            listeners: {
                'change': Ext.bind(this.onSelectionChange, this)
            }
        }];
    },
    
    initValue: function() {
        this.callParent(arguments);
        
        if (!this.value) {
            this.selectByDate();
        }
    },
    
    initRefs: function() {
        this.daysCheckboxGroup = this.down('#' + this.id + '-days');
    },
    
    onSelectionChange: function(field, value, oldValue) {
        this.checkChange();
        this.updateLabel();
    },
    
    selectByDate: function(dt) {
        var day = Ext.Date.format(dt || this.getStartDate(), 'D').substring(0,2).toUpperCase();
        this.setValue('BYDAY=' + day);
    },
    
    clearValue: function() {
        this.value = undefined;
        
        if (this.daysCheckboxGroup) {
            this.daysCheckboxGroup.setValue({
                SU:0, MO:0, TU:0, WE:0, TH:0, FR:0, SA:0
            });
        }
    },
    
    getValue: function() {
        var me = this;
        
        if (me.daysCheckboxGroup) {
            // Checkbox group value will look like {MON:"on", TUE:"on", FRI:"on"}
            var fieldValue = me.daysCheckboxGroup.getValue(),
                days = [],
                property;
            
            for (property in fieldValue) {
                if (fieldValue.hasOwnProperty(property)) {
                    // Push the name ('MON') not the value ('on')
                    days.push(property);
                }
            }
            return days.length > 0 ? 'BYDAY=' + days.join(me.dayValueDelimiter) : '';
        }
        return '';
    },
    
    setValue: function(v) {
        var me = this;
        
        if (!me.preSetValue(v, me.daysCheckboxGroup)) {
            return me;
        }
        // Clear all checkboxes
        me.daysCheckboxGroup.setValue(null);
        if (!v) {
            return me;
        }
        var options = Ext.isArray(v) ? v : v.split(me.optionDelimiter),
            compositeValue = {},
            parts, days;

        Ext.each(options, function(option) {
            parts = option.split('=');
            
            if (parts[0] === 'BYDAY') {
                days = parts[1].split(me.dayValueDelimiter);
                    
                Ext.each(days, function(day) {
                    compositeValue[day] = true;
                }, me);
                
                me.daysCheckboxGroup.setValue(compositeValue);
                return;
            }
        }, me);
        
        return me;
    }
});/**
 * The widget that represents the yearly recurrence options of an RRULE.
 */
Ext.define('Extensible.form.recurrence.option.Yearly', {
    extend: 'Extensible.form.recurrence.option.Monthly',
    alias: 'widget.extensible.recurrence-yearly',
    
    cls: 'extensible-recur-yearly',
    
    nthComboWidth: 200,
    
    isYearly: true,
    
    getPeriodString: function() {
        return this.strings.year;
    }
});/**
 * The widget used to choose the frequency of recurrence. While this could be created
 * as a standalone widget, it is typically created automatically as part of a
 * Extensible.form.recurrence.Fieldset and does not normally need to be configured directly.
 */
Ext.define('Extensible.form.recurrence.FrequencyCombo', {
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.extensible.recurrence-frequency',
    
    requires: [
        'Ext.data.ArrayStore',
        'Extensible.form.recurrence.Parser'
    ],
    
    fieldLabel: 'Repeats',
    queryMode: 'local',
    triggerAction: 'all',
    forceSelection: true,
    displayField: 'pattern',
    valueField: 'id',
    cls: 'extensible-recur-frequency',
    
    initComponent: function() {
        var me = this;
        
        /**
         * @event frequencychange
         * Fires when a frequency list item is selected.
         * @param {Extensible.form.recurrence.Combo} combo This combo box
         * @param {String} value The selected frequency value (one of the names
         * from {@link #frequencyOptions}, e.g. 'DAILY')
         */
        me.addEvents('frequencychange');
        
        var freq = Extensible.form.recurrence.Parser.strings.frequency;
        
        /**
         * @cfg {Array} frequencyOptions
         * An array of arrays, each containing the name/value pair that defines a recurring
         * frequency option supported by the frequency combo. This array is bound to the underlying
         * {@link Ext.data.ArrayStore store} to provide the combo list items. The string descriptions
         * are defined in the {@link Extensible.form.recurrence.Parser#strings} config.
         * Defaults to:
         *
         *		[
         *			['NONE', 'Does not repeat'],
         *			['DAILY', 'Daily'],
         *			['WEEKDAYS', 'Every weekday (Mon-Fri)'],
         *			['WEEKLY', 'Weekly'],
         *			['MONTHLY', 'Monthly'],
         *			['YEARLY', 'Yearly']
         *		]
         */
        me.frequencyOptions = me.frequencyOptions || [
            ['NONE',     freq.none],
            ['DAILY',    freq.daily],
            ['WEEKDAYS', freq.weekdays],
            ['WEEKLY',   freq.weekly],
            ['MONTHLY',  freq.monthly],
            ['YEARLY',   freq.yearly]
        ];
        
        me.store = me.store || Ext.create('Ext.data.ArrayStore', {
            fields: ['id', 'pattern'],
            idIndex: 0,
            data: me.frequencyOptions
        });
        
        me.on('select', me.onSelect, me);
        
        me.callParent(arguments);
    },
    
    onSelect: function(combo, records) {
        this.fireEvent('frequencychange', records[0].data.id);
    }
});/**
 * The widget that represents a single recurrence rule field in the UI.
 * In reality, it is made up of many constituent
 * {@link #Extensible.form.recurrence.AbstractOption option widgets} internally.
 */
Ext.define('Extensible.form.recurrence.Fieldset', {
    extend: 'Ext.form.FieldContainer',
    alias: 'widget.extensible.recurrencefield',
    
    mixins: {
        field: 'Ext.form.field.Field'
    },
    
    requires: [
        'Ext.form.Label',
        'Extensible.form.recurrence.Rule',
        'Extensible.form.recurrence.FrequencyCombo',
        'Extensible.form.recurrence.option.Interval',
        'Extensible.form.recurrence.option.Weekly',
        'Extensible.form.recurrence.option.Monthly',
        'Extensible.form.recurrence.option.Yearly',
        'Extensible.form.recurrence.option.Duration'
    ],

    /**
     * @cfg {Extensible.form.recurrence.Rule} rrule
     * The {@link Extensible.form.recurrence.Rule recurrence Rule} instance underlying this component and
     * shared by all child recurrence option widgets. If not supplied a default instance will be created.
     */
    rrule: undefined,

    /**
     * @cfg {Date} startDate
     * The start date of the underlying recurrence series. This is not always required, depending on the specific
     * recurrence rules in effect, and will default to the current date if required and not supplied.
     */
    startDate: undefined,

    /**
     * @cfg {Number} startDay
     * The 0-based index for the day on which the calendar week begins (0=Sunday, which is the default)
     */
    startDay: 0,

    //TODO: implement code to use this config.
    // Maybe use xtypes instead for dynamic loading of custom options?
    // Include secondly/minutely/hourly, plugins for M-W-F, T-Th, weekends
    options: [
        'daily', 'weekly', 'weekdays', 'monthly', 'yearly'
    ],
    
    //TODO: implement
    displayStyle: 'field', // or 'dialog'
    
    fieldLabel: 'Repeats',
    fieldContainerWidth: 400,
    
    //enableFx: true,
    monitorChanges: true,
    cls: 'extensible-recur-field',
    
    frequencyWidth: null, // defaults to the anchor value
    
    layout: 'anchor',
    defaults: {
        anchor: '100%'
    },
    
    initComponent: function() {
        var me = this;
        
        if (!me.height || me.displayStyle === 'field') {
            delete me.height;
            me.autoHeight = true;
        }
        
        this.addEvents(
            /**
             * @event startchange
             * Fires when the start date of the recurrence series is changed
             * @param {Extensible.form.recurrence.option.Interval} this
             * @param {Date} newDate The new start date
             * @param {Date} oldDate The previous start date
             */
            'startchange'
        );
        
        me.initRRule();
        
        me.items = [{
            xtype: 'extensible.recurrence-frequency',
            hideLabel: true,
            width: this.frequencyWidth,
            itemId: this.id + '-frequency',
            
            listeners: {
                'frequencychange': {
                    fn: this.onFrequencyChange,
                    scope: this
                }
            }
        },{
            xtype: 'container',
            itemId: this.id + '-inner-ct',
            cls: 'extensible-recur-inner-ct',
            autoHeight: true,
            layout: 'anchor',
            hideMode: 'offsets',
            hidden: true,
            width: this.fieldContainerWidth,
            
            defaults: {
                hidden: true,
                rrule: me.rrule
            },
            items: [{
                xtype: 'extensible.recurrence-interval',
                itemId: this.id + '-interval'
            },{
                xtype: 'extensible.recurrence-weekly',
                itemId: this.id + '-weekly',
                startDay: this.startDay
            },{
                xtype: 'extensible.recurrence-monthly',
                itemId: this.id + '-monthly'
            },{
                xtype: 'extensible.recurrence-yearly',
                itemId: this.id + '-yearly'
            },{
                xtype: 'extensible.recurrence-duration',
                itemId: this.id + '-duration',
                startDay: this.startDay
            }]
        }];
        
        me.callParent(arguments);
        
        me.initField();
    },
    
    initRRule: function() {
        var me = this;
        
        me.rrule = me.rrule || Ext.create('Extensible.form.recurrence.Rule');
        me.startDate = me.startDate || me.rrule.startDate || Extensible.Date.today();
        
        if (!me.rrule.startDate) {
            me.rrule.setStartDate(me.startDate);
        }
    },
    
    afterRender: function() {
        this.callParent(arguments);
        this.initRefs();
    },
    
    initRefs: function() {
        var me = this,
            id = me.id;
        
        me.innerContainer = me.down('#' + id + '-inner-ct');
        me.frequencyCombo = me.down('#' + id + '-frequency');
        me.intervalField = me.down('#' + id + '-interval');
        me.weeklyField = me.down('#' + id + '-weekly');
        me.monthlyField = me.down('#' + id + '-monthly');
        me.yearlyField = me.down('#' + id + '-yearly');
        me.durationField = me.down('#' + id + '-duration');
        
        me.initChangeEvents();
    },
    
    initChangeEvents: function() {
        var me = this;
        
        me.intervalField.on('startchange', me.onStartDateChange, me);
        
        me.intervalField.on('change', me.onChange, me);
        me.weeklyField.on('change', me.onChange, me);
        me.monthlyField.on('change', me.onChange, me);
        me.yearlyField.on('change', me.onChange, me);
        me.durationField.on('change', me.onChange, me);
    },
    
    onStartDateChange: function(interval, newDate, oldDate) {
        this.fireEvent('startchange', this, newDate, oldDate);
    },
    
    onChange: function() {
        this.fireEvent('change', this, this.getValue());
    },
    
    onFrequencyChange: function(freq) {
        this.setFrequency(freq);
        this.onChange();
    },
    
    // private
    initValue: function() {
        var me = this;

        me.originalValue = me.lastValue = me.value;

        // Set the initial value - prevent validation on initial set
        me.suspendCheckChange++;
        
        me.setStartDate(me.startDate);
        
        if (me.value !== undefined) {
            me.setValue(me.value);
        }
        else if (me.frequency !== undefined) {
            me.setValue('FREQ=' + me.frequency);
        }
        else{
            me.setValue('');
        }
        me.suspendCheckChange--;
        
        Ext.defer(me.doLayout, 1, me);
        me.onChange();
    },
    
    /**
     * Sets the start date of the recurrence pattern
     * @param {Date} The new start date
     * @return {Extensible.form.recurrence.Fieldset} this
     */
    setStartDate: function(dt) {
        var me = this;
        
        me.startDate = dt;
        
        if (me.innerContainer) {
            me.innerContainer.items.each(function(item) {
                if (item.setStartDate) {
                    item.setStartDate(dt);
                }
            });
        }
        else {
            me.on('afterrender', function() {
                me.setStartDate(dt);
            }, me, {single: true});
        }
        return me;
    },
    
    /**
     * Returns the start date of the recurrence pattern (defaults to the current date
     * if not explicitly set via {@link #setStartDate} or the constructor).
     * @return {Date} The recurrence start date
     */
    getStartDate: function() {
        return this.startDate;
    },
    
    /**
     * Return true if the fieldset currently has a recurrence value set, otherwise returns false.
     */
    isRecurring: function() {
        return this.getValue() !== '';
    },
    
    getValue: function() {
        if (!this.innerContainer) {
            return this.value;
        }
        if (this.frequency === 'NONE') {
            return '';
        }
        
        var values,
            itemValue;
        
        if (this.frequency === 'WEEKDAYS') {
            values = ['FREQ=WEEKLY','BYDAY=MO,TU,WE,TH,FR'];
        }
        else {
            values = ['FREQ=' + this.frequency];
        }
        
        this.innerContainer.items.each(function(item) {
            if(item.isVisible() && item.getValue) {
                itemValue = item.getValue();
                if (this.includeItemValue(itemValue)) {
                    values.push(itemValue);
                }
            }
        }, this);
        
        return values.length > 1 ? values.join(';') : values[0];
    },
    
    includeItemValue: function(value) {
        if (value) {
            if (value === 'INTERVAL=1') {
                // Interval is assumed to be 1 in the spec by default, no need to include it
                return false;
            }
            var day = Ext.Date.format(this.startDate, 'D').substring(0,2).toUpperCase();
            if (value === ('BYDAY=' + day)) {
                // BYDAY is only required if different from the pattern start date
                return false;
            }
            return true;
        }
        return false;
    },
    
    getDescription: function() {
        // TODO: Should not have to set value here
        return this.rrule.setRule(this.getValue()).getDescription();
    },
    
    setValue: function(value) {
        var me = this;
        
        me.value = (!value || value === 'NONE' ? '' : value);
        
        if (!me.frequencyCombo || !me.innerContainer) {
            me.on('afterrender', function() {
                me.setValue(value);
            }, me, {
                single: true
            });
            return;
        }

        var parts = me.value.split(';');
        
        if (me.value === '') {
            me.setFrequency('NONE');
        }
        else {
            Ext.each(parts, function(part) {
                if (part.indexOf('FREQ') > -1) {
                    var freq = part.split('=')[1];
                    me.setFrequency(freq);
                    me.checkChange();
                    return;
                }
            }, me);
        }
        
        me.innerContainer.items.each(function(item) {
            if (item.setValue) {
                item.setValue(me.value);
            }
        });
        
        me.checkChange();
        
        return me;
    },
    
    setFrequency: function(freq) {
        var me = this;
        
        me.frequency = freq;
        
        if (me.frequencyCombo) {
            me.frequencyCombo.setValue(freq);
            me.showOptions(freq);
            
            this.innerContainer.items.each(function(item) {
                item.setFrequency(freq);
            });
        }
        else {
            me.on('afterrender', function() {
                me.frequencyCombo.setValue(freq);
                me.showOptions(freq);
            }, me, {single: true});
        }
        return me;
    },
    
    showOptions: function(freq) {
        var me = this,
            unit = 'day';
        
        if (freq === 'NONE') {
            // me.innerContainer.items.each(function(item) {
                // item.hide();
            // });
            me.innerContainer.hide();
        }
        else {
            me.intervalField.show();
            me.durationField.show();
            me.innerContainer.show();
        }
        
        switch(freq) {
            case 'DAILY':
            case 'WEEKDAYS':
                me.weeklyField.hide();
                me.monthlyField.hide();
                me.yearlyField.hide();
                
                if (freq === 'WEEKDAYS') {
                    unit = 'week';
                }
                break;
            
            case 'WEEKLY':
                me.weeklyField.show();
                me.monthlyField.hide();
                me.yearlyField.hide();
                unit = 'week';
                break;
            
            case 'MONTHLY':
                me.monthlyField.show();
                me.weeklyField.hide();
                me.yearlyField.hide();
                unit = 'month';
                break;
            
            case 'YEARLY':
                me.yearlyField.show();
                me.weeklyField.hide();
                me.monthlyField.hide();
                unit = 'year';
                break;
        }

        me.intervalField.updateLabel(unit);
    }
});/**
 * This panel is used during recurrence editing. It enables the user to indicate which
 * style of edit is currently being performed on a recurring series. The types currently
 * supported are:
 * 
 * - Edit a single instance
 * - Edit the current and future instances (past instances are unchanged)
 * - Edit all instances in the series
 * 
 * Typically this panel is created implicitly by the Extensible.form.recurrence.RangeEditWindow
 * and should not typically be instantiated directly.
 * 
 * @protected
 */
Ext.define('Extensible.form.recurrence.RangeEditPanel', {
    extend: 'Ext.form.Panel',
    alias: 'widget.extensible.recurrence-rangeeditpanel',
    
    cls: 'extensible-recur-edit-options',
    
    headerText: 'There are multiple events in this series. How would you like your changes applied?',
    optionSingleButtonText: 'Single',
    optionSingleDescription: 'Apply to this event only. No other events in the series will be affected.',
    optionFutureButtonText: 'Future',
    optionFutureDescription: 'Apply to this and all following events only. Past events will be unaffected.',
    optionAllButtonText: 'All Events',
    optionAllDescription: 'Apply to every event in this series.',
    
    editModes: {
        SINGLE: 'single',
        FUTURE: 'future',
        ALL: 'all'
    },
    
    border: false,
    
    layout: {
        type: 'vbox',
        align: 'stretch'
    },
    
    // private
    initComponent: function() {
        var me = this;
        
        me.editMode = me.editMode || me.editModes.ALL;
        
        me.items = [
            me.getHeaderConfig(),
            me.getOptionPanelConfig(),
            me.getSummaryConfig()
        ];
        me.callParent(arguments);
    },
    
    getHeaderConfig: function() {
        return {
            xtype: 'component',
            html: this.headerText,
            height: 55,
            padding: 15
        };
    },
    
    getSummaryConfig: function() {
        return {
            xtype: 'component',
            itemId: this.id + '-summary',
            html: this.optionAllDescription,
            flex: 1,
            padding: 15
        };
    },
    
    getOptionPanelConfig: function() {
        return {
            xtype: 'panel',
            border: false,
            layout: {
                type: 'hbox',
                pack: 'center'
            },
            items: this.getOptionButtonConfigs()
        };
    },
    
    getOptionButtonConfigs: function() {
        var me = this,
            defaultConfig = {
                xtype: 'button',
                iconAlign: 'top',
                enableToggle: true,
                scale: 'large',
                width: 80,
                toggleGroup: 'recur-toggle',
                toggleHandler: me.onToggle,
                scope: me
        },
        items = [Ext.apply({
            itemId: me.id + '-single',
            text: me.optionSingleButtonText,
            iconCls: 'recur-edit-single',
            pressed: me.editMode === me.editModes.SINGLE
        }, defaultConfig),
        Ext.apply({
            itemId: me.id + '-future',
            text: me.optionFutureButtonText,
            iconCls: 'recur-edit-future',
            pressed: me.editMode === me.editModes.FUTURE
        }, defaultConfig),
        Ext.apply({
            itemId: me.id + '-all',
            text: me.optionAllButtonText,
            iconCls: 'recur-edit-all',
            pressed: me.editMode === me.editModes.ALL
        }, defaultConfig)];
        
        return items;
    },
    
    getEditMode: function() {
        return this.editMode;
    },
    
    showEditModes: function(modes) {
        modes = modes || [];
        
        var me = this,
            i = 0,
            btn,
            len = modes.length;
        
        // If modes were passed in hide all by default so we can only show the
        // passed ones, otherwise if nothing was passed in show all
        me.down('#' + me.id + '-single')[len ? 'hide' : 'show']();
        me.down('#' + me.id + '-future')[len ? 'hide' : 'show']();
        me.down('#' + me.id + '-all')[len ? 'hide' : 'show']();
        
        for (; i < len; i++) {
            btn = me.down('#' + me.id + '-' + modes[i]);
            if (btn) {
                btn.show();
            }
        }
    },
    
    onToggle: function(btn) {
        var me = this,
            summaryEl = me.getComponent(me.id + '-summary').getEl();
        
        if (btn.itemId === me.id + '-single') {
            summaryEl.update(me.optionSingleDescription);
            me.editMode = me.editModes.SINGLE;
        }
        else if (btn.itemId === me.id + '-future') {
            summaryEl.update(me.optionFutureDescription);
            me.editMode = me.editModes.FUTURE;
        }
        else {
            summaryEl.update(me.optionAllDescription);
            me.editMode = me.editModes.ALL;
        }
    }
});/**
 * This window contains an instance of Extensible.form.recurrence.RangeEditPanel and,
 * by default, is displayed to the user anytime a recurring event is edited. This window
 * allows the user to indicate which style of edit is being performed on the recurring series.
 * See the RangeEditPanel docs for additional information on supported edit types.
 * 
 * This window is created automatically by Extensible and should not typically be
 * instantiated directly.
 * 
 * @protected
 */
Ext.define('Extensible.form.recurrence.RangeEditWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.extensible.recurrence-rangeeditwindow',
    id: 'ext-cal-rangeeditwin',

    requires: [
        'Extensible.form.recurrence.RangeEditPanel'
    ],
    
    // Locale configs
    title: 'Recurring Event Options',
    width: 350,
    height: 240,
    saveButtonText: 'Save',
    cancelButtonText: 'Cancel',
    
    // General configs
    closeAction: 'hide',
    modal: true,
    resizable: false,
    constrain: true,
    buttonAlign: 'right',
    layout: 'fit',
    
    formPanelConfig: {
        border: false
    },
    
    initComponent: function() {
        this.items = [{
            xtype: 'extensible.recurrence-rangeeditpanel',
            itemId: this.id + '-recur-panel'
        }];
        this.fbar = this.getFooterBarConfig();
        
        this.callParent(arguments);
    },
    
    getRangeEditPanel: function() {
        return this.down('#' + this.id + '-recur-panel');
    },
    
    /**
     * Configure the window and show it
     * @param {Object} options Valid properties: editModes[], callback, scope
     */
    prompt: function(o) {
        this.callbackFunction = Ext.bind(o.callback, o.scope || this);
        this.getRangeEditPanel().showEditModes(o.editModes);
        this.show();
    },
    
    getFooterBarConfig: function() {
        var cfg = ['->', {
                text: this.saveButtonText,
                itemId: this.id + '-save-btn',
                disabled: false,
                handler: this.onSaveAction,
                scope: this
            },{
                text: this.cancelButtonText,
                itemId: this.id + '-cancel-btn',
                disabled: false,
                handler: this.onCancelAction,
                scope: this
            }];
        
        return cfg;
    },
    
    onSaveAction: function() {
        var mode = this.getComponent(this.id + '-recur-panel').getEditMode();
        this.callbackFunction(mode);
        this.close();
    },
    
    onCancelAction: function() {
        this.callbackFunction(false);
        this.close();
    }
});