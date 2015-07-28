## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DELETE FROM `entities_def` WHERE `entityid` = OLD.entityid;
</%block>
