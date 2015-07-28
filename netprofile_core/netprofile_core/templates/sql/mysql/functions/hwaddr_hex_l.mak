## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE tmps VARCHAR(12);
	SET tmps := LOWER(HEX(hwbin));
	RETURN CONCAT_WS(':',
		SUBSTRING(tmps FROM 1 FOR 2),
		SUBSTRING(tmps FROM 3 FOR 2),
		SUBSTRING(tmps FROM 5 FOR 2),
		SUBSTRING(tmps FROM 7 FOR 2),
		SUBSTRING(tmps FROM 9 FOR 2),
		SUBSTRING(tmps FROM 11 FOR 2)
	);
</%block>
