## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE hg INT UNSIGNED DEFAULT 0;

	IF NEW.offset = 0 THEN
		SELECT `hgid`
		INTO hg
		FROM `hosts_def`
		WHERE `hostid` = NEW.hostid;
		SET NEW.offset := ip6addr_get_offset_hg(NEW.netid, hg);
	END IF;
</%block>
