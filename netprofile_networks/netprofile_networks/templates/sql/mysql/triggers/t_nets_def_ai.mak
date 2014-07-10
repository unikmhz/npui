## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 6, 1, CONCAT_WS(" ",
		"New network",
		CONCAT("[ID ", NEW.netid, "]"),
		CONCAT("'", NEW.name, "'")
	));
</%block>
