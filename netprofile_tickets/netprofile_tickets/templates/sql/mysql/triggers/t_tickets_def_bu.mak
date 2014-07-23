## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.mby := @accessuid;
	IF OLD.tstid <> NEW.tstid THEN
		SET NEW.ttime := NOW();
		SET NEW.tby := @accessuid;
	END IF;
</%block>
