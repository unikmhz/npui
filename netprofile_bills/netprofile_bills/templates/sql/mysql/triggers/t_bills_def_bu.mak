## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE sio INT UNSIGNED DEFAULT 0;
	DECLARE uid, stash_currid INT UNSIGNED DEFAULT NULL;
	DECLARE bill_sum DECIMAL(20,8) DEFAULT 0.0;
	DECLARE xrate_from, xrate_to DECIMAL(20,8) DEFAULT 1.0;
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
			SET bill_sum := NEW.sum;

			SELECT `currid` INTO stash_currid
			FROM `stashes_def`
			WHERE `stashid` = NEW.stashid
			FOR UPDATE;

			INSERT INTO `stashes_io_def` (`siotypeid`, `stashid`, `currid`, `uid`, `ts`, `diff`)
			VALUES (sio, NEW.stashid, NEW.currid, uid, NEW.ptime, NEW.sum);

			IF NOT (NEW.currid <=> stash_currid) THEN
				IF NEW.currid IS NOT NULL THEN
					SELECT `xchange_rate` INTO xrate_from
					FROM `currencies_def`
					WHERE `currid` = NEW.currid;
					SET bill_sum := bill_sum * xrate_from;
				END IF;
				IF stash_currid IS NOT NULL THEN
					SELECT `xchange_rate` INTO xrate_to
					FROM `currencies_def`
					WHERE `currid` = stash_currid;
					SET bill_sum := bill_sum / xrate_to;
				END IF;
			END IF;

			UPDATE `stashes_def`
			SET `amount` = `amount` + bill_sum
			WHERE `stashid` = NEW.stashid;
		END IF;
	END IF;
</%block>
