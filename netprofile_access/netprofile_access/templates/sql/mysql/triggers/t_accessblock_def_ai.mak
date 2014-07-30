## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	IF (NEW.entityid > 0) THEN
		IF (NEW.bstate = 'active') THEN
			UPDATE `entities_access`
			SET `state` = 2
			WHERE `entityid` = NEW.entityid;
		ELSE
			UPDATE `entities_access`
			SET `bcheck` = 'Y'
			WHERE `entityid` = NEW.entityid;
		END IF;
	END IF;
</%block>
