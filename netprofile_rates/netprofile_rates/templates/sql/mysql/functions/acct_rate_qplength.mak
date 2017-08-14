## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: acct_rate_qplength
## Copyright © 2014-2017 Alex Unigovsky
##
## This file is part of NetProfile.
## NetProfile is free software: you can redistribute it and/or
## modify it under the terms of the GNU Affero General Public
## License as published by the Free Software Foundation, either
## version 3 of the License, or (at your option) any later
## version.
##
## NetProfile is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General
## Public License along with NetProfile. If not, see
## <http://www.gnu.org/licenses/>.
##
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE s INT UNSIGNED DEFAULT 0;
	DECLARE curyear SMALLINT UNSIGNED;
	DECLARE curmonth TINYINT UNSIGNED;
	DECLARE curday TINYINT UNSIGNED;
	DECLARE curhour TINYINT UNSIGNED;
	DECLARE cutoff DATETIME;

	IF qpu IN('f_hour', 'f_day', 'f_week', 'f_month', 'f_year') THEN
		CASE qpu
			WHEN 'f_hour' THEN SET cutoff := endtime - INTERVAL qpa HOUR;
			WHEN 'f_day' THEN SET cutoff := endtime - INTERVAL qpa DAY;
			WHEN 'f_week' THEN SET cutoff := endtime - INTERVAL qpa WEEK;
			WHEN 'f_month' THEN SET cutoff := endtime - INTERVAL qpa MONTH;
			WHEN 'f_year' THEN SET cutoff := endtime - INTERVAL qpa YEAR;
		END CASE;
		SET s := UNIX_TIMESTAMP(endtime) - UNIX_TIMESTAMP(cutoff);
	ELSEIF qpu IN('c_hour', 'c_day', 'c_month', 'c_year') THEN
		CASE qpu
			WHEN 'c_hour' THEN SET cutoff := endtime - INTERVAL (qpa - 1) HOUR;
			WHEN 'c_day' THEN SET cutoff := endtime - INTERVAL (qpa - 1) DAY;
			WHEN 'c_month' THEN SET cutoff := endtime - INTERVAL (qpa - 1) MONTH;
			WHEN 'c_year' THEN SET cutoff := endtime - INTERVAL (qpa - 1) YEAR;
		END CASE;
		SET curhour := HOUR(cutoff);
		SET curday := DAYOFMONTH(cutoff);
		SET curmonth := MONTH(cutoff);
		SET curyear := YEAR(cutoff);
		CASE qpu
			WHEN 'c_hour' THEN SET cutoff := CONCAT(curyear, '-', curmonth, '-', curday, ' ', curhour, ':00:00');
			WHEN 'c_day' THEN SET cutoff := CONCAT(curyear, '-', curmonth, '-', curday, ' 00:00:00');
			WHEN 'c_month' THEN SET cutoff := CONCAT(curyear, '-', curmonth, '-01 00:00:00');
			WHEN 'c_year' THEN SET cutoff := CONCAT(curyear, '-01-01 00:00:00');
		END CASE;
		SET s := UNIX_TIMESTAMP(endtime) - UNIX_TIMESTAMP(cutoff);
	ELSE
		CASE qpu
			WHEN 'a_hour' THEN SET s := 3600 * qpa;
			WHEN 'a_day' THEN SET s := 86400 * qpa;
			WHEN 'a_week' THEN SET s := 604800 * qpa;
			WHEN 'a_month' THEN SET s := 2592000 * qpa;
			WHEN 'a_year' THEN SET s := 31536000 * qpa;
		END CASE;
		SET s := UNIX_TIMESTAMP(endtime) - UNIX_TIMESTAMP(endtime - INTERVAL s SECOND);
	END IF;
	RETURN s;
</%block>
