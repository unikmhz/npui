## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 2, 1, CONCAT_WS(" ",
		"New entity",
		CONCAT("[ID ", NEW.entityid, "]"),
		CONCAT("[TYPE ", NEW.etype, "]"),
		CONCAT("'", NEW.nick, "'")
	));
</%block>
