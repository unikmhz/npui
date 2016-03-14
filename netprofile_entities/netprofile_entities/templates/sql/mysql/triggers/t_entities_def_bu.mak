## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	IF @accessuid > 0 THEN
		SET NEW.mby := @accessuid;
	END IF;
</%block>
