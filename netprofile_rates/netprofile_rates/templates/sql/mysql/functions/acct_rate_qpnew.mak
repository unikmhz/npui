## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: acct_rate_qpnew
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
	DECLARE endtime DATETIME;

	IF qpu IN('c_hour', 'c_day', 'c_month', 'c_year', 'f_hour', 'f_day', 'f_week', 'f_month', 'f_year') AND time IS NOT NULL THEN
		CASE qpu
			WHEN 'c_hour' THEN
				SET endtime := time + INTERVAL (qpa - 1) HOUR;
				SET curyear := YEAR(endtime);
				SET curmonth := MONTH(endtime);
				SET curday := DAYOFMONTH(endtime);
				SET curhour := HOUR(endtime);
				SET endtime := CONCAT(curyear, '-', curmonth, '-', curday, ' ', curhour, ':59:59');
			WHEN 'c_day' THEN
				SET endtime := time + INTERVAL (qpa - 1) DAY;
				SET curyear := YEAR(endtime);
				SET curmonth := MONTH(endtime);
				SET curday := DAYOFMONTH(endtime);
				SET endtime := CONCAT(curyear, '-', curmonth, '-', curday, ' 23:59:59');
			WHEN 'c_month' THEN
				SET endtime := CONCAT(LAST_DAY(time + INTERVAL (qpa - 1) MONTH), ' 23:59:59');
			WHEN 'c_year' THEN
				SET endtime := time + INTERVAL (qpa - 1) YEAR;
				SET curyear := YEAR(endtime);
				SET endtime := CONCAT(curyear, '-12-31 23:59:59');
			WHEN 'f_hour' THEN
				SET endtime := time + INTERVAL (qpa) HOUR;
			WHEN 'f_day' THEN
				SET endtime := time + INTERVAL (qpa) DAY;
			WHEN 'f_week' THEN
				SET endtime := time + INTERVAL (qpa) WEEK;
			WHEN 'f_month' THEN
				SET endtime := time + INTERVAL (qpa) MONTH;
			WHEN 'f_year' THEN
				SET endtime := time + INTERVAL (qpa) YEAR;
		END CASE;
		SET s := UNIX_TIMESTAMP(endtime) - UNIX_TIMESTAMP(time);
	ELSE
		CASE qpu
			WHEN 'a_hour' THEN SET s := 3600;
			WHEN 'a_day' THEN SET s := 86400;
			WHEN 'a_week' THEN SET s := 604800;
			WHEN 'a_month' THEN SET s := 2592000;
			WHEN 'a_year' THEN SET s := 31536000;
		END CASE;
		SET s := s * qpa;
	END IF;
	RETURN s;
</%block>
