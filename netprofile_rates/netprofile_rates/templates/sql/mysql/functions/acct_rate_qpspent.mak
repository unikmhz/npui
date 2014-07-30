## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE s INT UNSIGNED DEFAULT 0;
	DECLARE curyear SMALLINT UNSIGNED;
	DECLARE curmonth TINYINT UNSIGNED;
	DECLARE curday TINYINT UNSIGNED;
	DECLARE curhour TINYINT UNSIGNED;
	DECLARE cutoff DATETIME;

	IF qpu IN('f_hour', 'f_day', 'f_week', 'f_month') THEN
		CASE qpu
			WHEN 'f_hour' THEN SET cutoff := endtime - INTERVAL qpa HOUR;
			WHEN 'f_day' THEN SET cutoff := endtime - INTERVAL qpa DAY;
			WHEN 'f_week' THEN SET cutoff := endtime - INTERVAL qpa WEEK;
			WHEN 'f_month' THEN SET cutoff := endtime - INTERVAL qpa MONTH;
		END CASE;
		SET s := UNIX_TIMESTAMP(time) - UNIX_TIMESTAMP(cutoff);
	ELSEIF qpu IN('c_hour', 'c_day', 'c_month') THEN
		CASE qpu
			WHEN 'c_hour' THEN SET cutoff := endtime - INTERVAL (qpa - 1) HOUR;
			WHEN 'c_day' THEN SET cutoff := endtime - INTERVAL (qpa - 1) DAY;
			WHEN 'c_month' THEN SET cutoff := endtime - INTERVAL (qpa - 1) MONTH;
		END CASE;
		SET curhour := HOUR(cutoff);
		SET curday := DAYOFMONTH(cutoff);
		SET curmonth := MONTH(cutoff);
		SET curyear := YEAR(cutoff);
		CASE qpu
			WHEN 'c_hour' THEN SET cutoff := CONCAT(curyear, '-', curmonth, '-', curday, ' ', curhour, ':00:00');
			WHEN 'c_day' THEN SET cutoff := CONCAT(curyear, '-', curmonth, '-', curday, ' 00:00:00');
			WHEN 'c_month' THEN SET cutoff := CONCAT(curyear, '-', curmonth, '-01 00:00:00');
		END CASE;
		SET s := UNIX_TIMESTAMP(time) - UNIX_TIMESTAMP(cutoff);
	ELSE
		CASE qpu
			WHEN 'a_hour' THEN SET s := 3600 * qpa;
			WHEN 'a_day' THEN SET s := 86400 * qpa;
			WHEN 'a_week' THEN SET s := 604800 * qpa;
			WHEN 'a_month' THEN SET s := 2592000 * qpa;
		END CASE;
		SET s := UNIX_TIMESTAMP(time) - UNIX_TIMESTAMP(endtime - INTERVAL s SECOND);
	END IF;
	RETURN s;
</%block>
