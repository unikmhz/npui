## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 7, 1, CONCAT_WS(" ",
		"New user",
		CONCAT("[ID ", NEW.uid, "]"),
		CONCAT("'", NEW.login, "'")
	));
</%block>
