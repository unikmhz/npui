## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 5, 1, CONCAT_WS(" ",
		"New domain",
		CONCAT("[ID ", NEW.domainid, "]"),
		CONCAT("[PARENTID ", NEW.parentid, "]"),
		CONCAT("'", NEW.name, "'")
	));
</%block>
