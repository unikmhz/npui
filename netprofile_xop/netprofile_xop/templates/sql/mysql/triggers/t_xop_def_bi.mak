## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE sio INT UNSIGNED DEFAULT 0;
	DECLARE stash_currid INT UNSIGNED DEFAULT NULL;
	DECLARE conv_sum DECIMAL(20,8) DEFAULT 0.0;
	DECLARE xrate_xop, xrate_stash DECIMAL(20,8) DEFAULT 1.0;
	DECLARE conv_ok ENUM('Y', 'N') CHARACTER SET ascii DEFAULT 'Y';
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

	SET conv_sum := NEW.diff;

	IF (NEW.state = 'CLR') AND (NEW.stashid IS NOT NULL) THEN
		SELECT `siotypeid` INTO sio
		FROM `xop_providers`
		WHERE `xoppid` = NEW.xoppid;
		IF sio > 0 THEN
			SELECT `currid`
			INTO stash_currid
			FROM `stashes_def`
			WHERE `stashid` = NEW.stashid
			FOR UPDATE;

			IF NOT (NEW.currid <=> stash_currid) THEN
				IF NEW.currid IS NOT NULL THEN
					SELECT `xchange_rate`, `xchange_from`
					INTO xrate_xop, conv_ok
					FROM `currencies_def`
					WHERE `currid` = NEW.currid;

					IF conv_ok = 'N' THEN
						SET sio := 0;
					ELSE
						SET conv_sum := conv_sum * xrate_xop;
					END IF;
				END IF;
				IF stash_currid IS NOT NULL THEN
					IF stash_currid = NEW.currid THEN
						SET xrate_stash := xrate_xop;
					ELSE
						SELECT `xchange_rate`, `xchange_to`
						INTO xrate_stash, conv_ok
						FROM `currencies_def`
						WHERE `currid` = stash_currid;
					END IF;

					IF conv_ok = 'N' THEN
						SET sio := 0;
					ELSE
						SET conv_sum := conv_sum / xrate_stash;
					END IF;
				END IF;
			END IF;

			IF sio > 0 THEN
				INSERT INTO `stashes_io_def` (`siotypeid`, `stashid`, `currid`, `uid`, `entityid`, `ts`, `diff`)
				VALUES (sio, NEW.stashid, stash_currid, IF(@accessuid > 0, @accessuid, NULL), NEW.entityid, NEW.ts, conv_sum);
				SET NEW.sioid := LAST_INSERT_ID();

				UPDATE `stashes_def`
				SET `amount` = `amount` + conv_sum
				WHERE `stashid` = NEW.stashid;
			ELSE
				SET NEW.sioid := NULL;
				SET NEW.state := 'CNF';
			END IF;
		END IF;
	END IF;
</%block>
