## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.ctime := NOW();
	IF @accessuid > 0 THEN
		SET NEW.uid := @accessuid;
	END IF;
</%block>
