## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 22, 1, CONCAT_WS(" ",
		"New task",
		CONCAT("[ID ", NEW.taskid, "]"),
		CONCAT("[BEATSCHID ", NEW.beatschid, "]"),
		CONCAT("'", NEW.proc, "'")
	));
</%block>
