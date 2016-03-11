## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.ctime := NOW();
	IF @accessuid > 0 THEN
		SET NEW.cby := @accessuid;
		SET NEW.mby := @accessuid;
	END IF;
</%block>
