## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DELETE FROM `devices_types_def` WHERE `dtid` = OLD.dtid;
</%block>
