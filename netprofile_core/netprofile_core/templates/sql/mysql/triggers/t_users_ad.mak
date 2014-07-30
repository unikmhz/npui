## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 7, 3, CONCAT_WS(" ",
		"Deleted user",
		CONCAT("[ID ", OLD.uid, "]")
	));
</%block>
