## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.mby := IF(@accessuid > 0, @accessuid, NULL);
	IF OLD.tstid <> NEW.tstid THEN
		SET NEW.ttime := NOW();
		SET NEW.tby := NEW.mby;
	END IF;
</%block>
