## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.uid := IF(@accessuid > 0, @accessuid, NULL);
	SET NEW.ts := NOW();
</%block>
