## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 21, 2, CONCAT_WS(" ",
		"Modified global setting",
		CONCAT("[ID ", NEW.npglobid, "]"),
		CONCAT("[NAME ", NEW.name, "]"),
		CONCAT("'", OLD.value, "' -> '", NEW.value, "'")
	));
</%block>
