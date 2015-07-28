## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE sio INT UNSIGNED DEFAULT 0;
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

	IF OLD.state = 'CLR' THEN
		SET NEW.state := 'CLR';
	ELSEIF NEW.state = 'CLR' THEN
		IF NEW.stashid IS NOT NULL THEN
			SELECT `siotypeid` INTO sio
			FROM `xop_providers`
			WHERE `xoppid` = NEW.xoppid;
			IF sio > 0 THEN
				INSERT INTO `stashes_io_def` (`siotypeid`, `stashid`, `uid`, `entityid`, `ts`, `diff`)
				VALUES (sio, NEW.stashid, @accessuid, NEW.entityid, NEW.ts, NEW.diff);
				UPDATE `stashes_def`
				SET `amount` = `amount` + NEW.diff
				WHERE `stashid` = NEW.stashid;
			END IF;
		ELSE
			SET NEW.state := OLD.state;
		END IF;
	END IF;
</%block>
