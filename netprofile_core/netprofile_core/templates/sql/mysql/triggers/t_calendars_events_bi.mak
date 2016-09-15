## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.ctime := NOW();
	SET NEW.uid := IF(@accessuid > 0, @accessuid, NULL);
</%block>
