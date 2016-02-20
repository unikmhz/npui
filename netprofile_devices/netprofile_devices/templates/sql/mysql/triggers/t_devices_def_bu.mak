## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	IF @accessuid > 0 THEN
		SET NEW.mby := @accessuid;
	END IF;
	IF OLD.placeid <> NEW.placeid THEN
		SET NEW.itime := NOW();
		IF @accessuid > 0 THEN
			SET NEW.iby := @accessuid;
		END IF;
	END IF;
</%block>
