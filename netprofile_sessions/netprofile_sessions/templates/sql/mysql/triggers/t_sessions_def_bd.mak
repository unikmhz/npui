## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	IF OLD.ipaddrid IS NOT NULL THEN
		UPDATE `ipaddr_def` SET `inuse` = 'N' WHERE `ipaddrid` = OLD.ipaddrid;
	END IF;
	IF OLD.ip6addrid IS NOT NULL THEN
		UPDATE `ip6addr_def` SET `inuse` = 'N' WHERE `ip6addrid` = OLD.ip6addrid;
	END IF;
</%block>
