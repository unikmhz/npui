## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 5, 3, CONCAT_WS(" ",
		"Deleted domain",
		CONCAT("[ID ", OLD.domainid, "]")
	));
</%block>
