## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 13, 1, CONCAT_WS(" ",
		"New rate",
		CONCAT("[ID ", NEW.rateid, "]"),
		CONCAT("'", NEW.name, "'")
	));
</%block>
