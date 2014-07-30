## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 20, 1, CONCAT_WS(" ",
		"New folder",
		CONCAT("[ID ", NEW.ffid, "]"),
		CONCAT("[UID ", NEW.uid, "]"),
		CONCAT("[GID ", NEW.gid, "]"),
		CONCAT("'", NEW.name, "'")
	));
</%block>
