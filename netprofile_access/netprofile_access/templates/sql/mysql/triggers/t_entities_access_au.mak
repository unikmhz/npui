## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE xuid INT(10) UNSIGNED DEFAULT NULL;

	IF @accessuid > 0 THEN
		SET xuid := @accessuid;
	END IF;
	IF (OLD.state <> NEW.state) OR (OLD.password <> NEW.password) OR (OLD.rateid <> NEW.rateid) THEN
		INSERT INTO `entities_access_changes` (`entityid`, `uid`, `ts`, `pwchanged`, `state_old`, `state_new`, `rateid_old`, `rateid_new`, `descr`)
		VALUES (NEW.entityid, xuid, NOW(), IF(OLD.password <> NEW.password, 'Y', 'N'), OLD.state, NEW.state, OLD.rateid, NEW.rateid, @comments);
	END IF;
</%block>
