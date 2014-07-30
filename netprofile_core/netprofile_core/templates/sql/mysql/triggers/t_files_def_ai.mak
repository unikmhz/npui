## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 17, 1, CONCAT_WS(" ",
		"New file",
		CONCAT("[ID ", NEW.fileid, "]"),
		CONCAT("[FFID ", NEW.ffid, "]"),
		CONCAT("'", NEW.fname, "'")
	));
</%block>
