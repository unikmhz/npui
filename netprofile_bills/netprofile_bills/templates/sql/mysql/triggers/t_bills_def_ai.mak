## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 15, 1, CONCAT_WS(" ",
		"New bill",
		CONCAT("[ID ", NEW.billid, "]"),
		CONCAT("[SUM ", NEW.sum, "]"),
		CONCAT("'", NEW.title, "'")
	));
</%block>
