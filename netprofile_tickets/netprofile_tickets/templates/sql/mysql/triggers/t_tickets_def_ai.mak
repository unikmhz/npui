## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 3, 1, CONCAT_WS(" ",
		"New ticket",
		CONCAT("[ID ", NEW.ticketid, "]"),
		CONCAT("'", NEW.name, "'")
	));
</%block>
