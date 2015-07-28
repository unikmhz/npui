## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DELETE FROM `entities_def` WHERE `entityid` = OLD.entityid;

	IF OLD.ipaddrid IS NOT NULL THEN
		UPDATE `ipaddr_def`
		SET `owned` = 'N'
		WHERE `ipaddrid` = OLD.ipaddrid;
	END IF;

	IF OLD.ip6addrid IS NOT NULL THEN
		UPDATE `ip6addr_def`
		SET `owned` = 'N'
		WHERE `ip6addrid` = OLD.ip6addrid;
	END IF;
</%block>
