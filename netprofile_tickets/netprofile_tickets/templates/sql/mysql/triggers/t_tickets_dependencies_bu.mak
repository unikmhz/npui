## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	IF NEW.ticketid_parent = NEW.ticketid_child THEN
		SET NEW.ticketid_parent := NULL;
		SET NEW.ticketid_child := NULL;
	END IF;
</%block>
