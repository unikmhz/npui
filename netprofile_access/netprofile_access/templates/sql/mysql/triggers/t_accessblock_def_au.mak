## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	IF (OLD.bstate = 'active') AND (NEW.bstate = 'expired') THEN
		UPDATE `entities_access`
		SET `state` = OLD.oldstate
		WHERE `entityid` = OLD.entityid;
	END IF;
</%block>
