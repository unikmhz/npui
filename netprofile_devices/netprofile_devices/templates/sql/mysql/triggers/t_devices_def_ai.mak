## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 9, 1, CONCAT_WS(" ",
		"New device",
		CONCAT("[ID ", NEW.did, "]"),
		CONCAT("[DTID ", NEW.dtid, "]")
	));
</%block>
