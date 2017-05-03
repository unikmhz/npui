## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE sio INT UNSIGNED DEFAULT 0;
	DECLARE uid INT UNSIGNED DEFAULT NULL;
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

	IF @accessuid > 0 THEN
		SET uid := @accessuid;
	END IF;
	SET NEW.serial := OLD.serial;
	SET NEW.parts := OLD.parts;
	SET NEW.mby := uid;
	IF OLD.state = 'P' THEN
		SET NEW.state := 'P';
	ELSEIF OLD.state = 'R' THEN
		SET NEW.state = 'R';
	ELSEIF NEW.state = 'P' THEN
		SET NEW.ptime := NOW();
		SET NEW.pby := uid;
		SELECT `siotypeid` INTO sio
		FROM `bills_types`
		WHERE `btypeid` = NEW.btypeid;
		IF sio > 0 THEN
			INSERT INTO `stashes_io_def` (`siotypeid`, `stashid`, `uid`, `ts`, `diff`)
			VALUES (sio, NEW.stashid, uid, NEW.ptime, NEW.sum);
			UPDATE `stashes_def`
			SET `amount` = `amount` + NEW.sum
			WHERE `stashid` = NEW.stashid;
		END IF;
	END IF;
</%block>
