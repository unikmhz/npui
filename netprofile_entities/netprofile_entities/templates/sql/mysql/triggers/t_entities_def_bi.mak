## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.ctime := NOW();
	SET NEW.cby := IF(@accessuid > 0, @accessuid, NULL);
	SET NEW.mby := NEW.cby;
</%block>
