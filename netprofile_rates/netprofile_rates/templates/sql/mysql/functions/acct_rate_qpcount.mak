## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE n INT UNSIGNED DEFAULT 0;

	CASE qpu
		WHEN 'a_hour' THEN SET n := FLOOR((UNIX_TIMESTAMP(dto) - UNIX_TIMESTAMP(dfrom)) / (3600 * qpa));
		WHEN 'a_day' THEN SET n := FLOOR((UNIX_TIMESTAMP(dto) - UNIX_TIMESTAMP(dfrom)) / (86400 * qpa));
		WHEN 'a_week' THEN SET n := FLOOR((UNIX_TIMESTAMP(dto) - UNIX_TIMESTAMP(dfrom)) / (604800 * qpa));
		WHEN 'a_month' THEN SET n := FLOOR((UNIX_TIMESTAMP(dto) - UNIX_TIMESTAMP(dfrom)) / (2592000 * qpa));
		WHEN 'c_hour' THEN SET n := FLOOR(TIMESTAMPDIFF(HOUR, dfrom, dto) / qpa);
		WHEN 'c_day' THEN SET n := FLOOR(DATEDIFF(dto, dfrom) / qpa);
		WHEN 'c_month' THEN SET n := FLOOR(TIMESTAMPDIFF(MONTH, dfrom, dto) / qpa);
	END CASE;
	RETURN n;
</%block>
