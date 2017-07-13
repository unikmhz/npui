## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE xuid INT(10) UNSIGNED DEFAULT NULL;

	IF @accessuid > 0 THEN
		SET xuid := @accessuid;
	END IF;
	IF (OLD.state <> NEW.state) OR (OLD.pwd_hashed <> NEW.pwd_hashed) OR (OLD.rateid <> NEW.rateid) THEN
		UPDATE `entities_def`
		SET `mby` = xuid, `mtime` = NOW()
		WHERE `entityid` IN (OLD.entityid, NEW.entityid);

		INSERT INTO `entities_access_changes` (`entityid`, `uid`, `ts`, `pwchanged`, `state_old`, `state_new`, `rateid_old`, `rateid_new`, `descr`)
		VALUES (NEW.entityid, xuid, NOW(), IF(OLD.pwd_hashed <> NEW.pwd_hashed, 'Y', 'N'), OLD.state, NEW.state, OLD.rateid, NEW.rateid, @comments);
	END IF;
</%block>
