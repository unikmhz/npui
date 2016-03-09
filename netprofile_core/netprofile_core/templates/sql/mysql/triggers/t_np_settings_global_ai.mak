## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 21, 1, CONCAT_WS(" ",
		"New global setting",
		CONCAT("[ID ", NEW.npglobid, "]"),
		CONCAT(NEW.name, "='", NEW.value, "'")
	));
</%block>
