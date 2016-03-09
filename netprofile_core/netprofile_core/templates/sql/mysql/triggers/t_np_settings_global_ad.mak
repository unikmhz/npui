## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 21, 3, CONCAT_WS(" ",
		"Deleted global setting",
		CONCAT("[ID ", OLD.npglobid, "]"),
		CONCAT(OLD.name, "='", OLD.value, "'")
	));
</%block>
