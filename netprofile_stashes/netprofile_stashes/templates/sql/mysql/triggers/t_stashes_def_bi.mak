## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.alltime_max := NEW.amount;
	SET NEW.alltime_min := NEW.amount;
</%block>
