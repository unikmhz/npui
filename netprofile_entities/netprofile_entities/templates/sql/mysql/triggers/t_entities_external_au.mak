## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	UPDATE `entities_def`
	SET
		`mby` = IF(@accessuid > 0, @accessuid, NULL),
		`mtime` = NOW()
	WHERE `entityid` IN (OLD.entityid, NEW.entityid);
</%block>
