## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	IF NEW.name REGEXP '[[:blank:]]' THEN
		SET NEW.name := NULL;
	END IF;
</%block>
