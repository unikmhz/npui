## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE tmps VARCHAR(255);
	SET tmps := hwstr;
	SET tmps := REPLACE(tmps, '-', '');
	SET tmps := REPLACE(tmps, ':', '');
	SET tmps := REPLACE(tmps, '.', '');
	SET tmps := REPLACE(tmps, ' ', '');
	RETURN UNHEX(tmps);
</%block>
