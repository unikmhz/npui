## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 3, 3, CONCAT_WS(" ",
		"Deleted ticket",
		CONCAT("[ID ", OLD.ticketid, "]")
	));
</%block>
