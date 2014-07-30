## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE curts DATETIME DEFAULT NULL;
	DECLARE ost TINYINT DEFAULT -1;
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

	IF (NEW.startts > NEW.endts) THEN
		SET curts := NEW.startts;
		SET NEW.startts := NEW.endts;
		SET NEW.endts := curts;
	END IF;
	SET curts := NOW();
	IF (curts >= NEW.startts) THEN
		IF (curts <= NEW.endts) THEN
			SET NEW.bstate := 'active';
		ELSE
			SET NEW.bstate := 'expired';
		END IF;
	ELSE
		SET NEW.bstate := 'planned';
	END IF;

	IF (NEW.entityid > 0) THEN
		SELECT `state`
		INTO ost
		FROM `entities_access`
		WHERE `entityid` = NEW.entityid;
		IF (ost >= 0) THEN
			SET NEW.oldstate := ost;
		END IF;
	END IF;
</%block>
