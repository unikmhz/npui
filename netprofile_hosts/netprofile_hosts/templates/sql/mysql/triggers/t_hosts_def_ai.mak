## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 4, 1, CONCAT_WS(" ",
		"New host",
		CONCAT("[ID ", NEW.hostid, "]"),
		CONCAT("[DOMAINID ", NEW.domainid, "]"),
		CONCAT("'", NEW.name, "'")
	));
</%block>
