## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 16, 1, CONCAT_WS(" ",
		"New future payment",
		CONCAT("[ID ", NEW.futureid, "]"),
		CONCAT("[ENTITYID ", NEW.entityid, "]"),
		CONCAT("[STASHID ", NEW.stashid, "]"),
		CONCAT("[DIFF ", NEW.diff, "]"),
		CONCAT("[PTIME ", NEW.ptime, "]")
	));
</%block>
