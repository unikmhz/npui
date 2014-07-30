## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE str VARCHAR(15) DEFAULT NULL;
	SELECT INET_NTOA(`n`.`ipaddr` + `a`.`offset`) INTO str
	FROM `ipaddr_def` AS `a`
	LEFT JOIN `nets_def` AS `n`
	USING(`netid`)
	WHERE `a`.`ipaddrid` = ip;
	RETURN str;
</%block>
