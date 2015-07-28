## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	IF NEW.contractid IS NULL THEN
		SET NEW.contractid := NEW.entityid;
	END IF;
</%block>
