## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.ctime := NOW();
	SET NEW.ttime := NULL;
	IF @accessuid > 0 THEN
		SET NEW.cby := @accessuid;
		SET NEW.mby := @accessuid;
	END IF;
	SET NEW.tby := NULL;
</%block>
