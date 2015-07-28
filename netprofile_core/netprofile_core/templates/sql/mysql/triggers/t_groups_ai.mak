## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 11, 1, CONCAT_WS(" ",
		"New group",
		CONCAT("[ID ", NEW.gid, "]"),
		CONCAT("'", NEW.name, "'")
	));
</%block>
