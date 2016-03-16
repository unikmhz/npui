## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.mby := IF(@accessuid > 0, @accessuid, NULL);
	IF OLD.placeid <> NEW.placeid THEN
		SET NEW.itime := NOW();
		SET NEW.iby := NEW.mby;
	END IF;
</%block>
