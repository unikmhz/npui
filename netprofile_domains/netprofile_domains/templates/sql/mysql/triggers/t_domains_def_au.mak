## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 5, 2, CONCAT_WS(" ",
		"Modified domain",
		CONCAT("[ID ", NEW.domainid, "]")
	));
</%block>
