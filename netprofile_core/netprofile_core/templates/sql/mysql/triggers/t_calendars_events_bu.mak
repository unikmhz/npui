## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.ctime := OLD.ctime;
	SET NEW.calid := OLD.calid;
	SET NEW.uid := OLD.uid;
</%block>
