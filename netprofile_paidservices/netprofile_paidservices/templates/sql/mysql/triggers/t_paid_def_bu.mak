## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.aeid := OLD.aeid;
	SET NEW.stashid := OLD.stashid;
	SET NEW.paidid := OLD.paidid;
</%block>
