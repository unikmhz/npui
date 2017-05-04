## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE sio INT UNSIGNED DEFAULT 0;
	DECLARE x_bsid, cser, uid, stash_currid INT UNSIGNED DEFAULT NULL;
	DECLARE bill_sum DECIMAL(20,8) DEFAULT 0.0;
	DECLARE xrate_from, xrate_to DECIMAL(20,8) DEFAULT 1.0;
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

	IF @accessuid > 0 THEN
		SET uid := @accessuid;
	END IF;
	SET NEW.ctime := NOW();
	SET NEW.ptime := NULL;
	SET NEW.cby := uid;
	SET NEW.mby := uid;
	SET NEW.pby := NULL;

	SELECT `bsid`
	INTO x_bsid
	FROM `bills_types`
	WHERE `btypeid` = NEW.btypeid;
	IF x_bsid IS NOT NULL THEN
		SELECT `value`
		INTO cser
		FROM `bills_serials`
		WHERE `bsid` = x_bsid
		FOR UPDATE;

		UPDATE `bills_serials`
		SET `value` = cser + 1
		WHERE `bsid` = x_bsid;

		SET NEW.serial := cser;
	ELSE
		SET NEW.serial := NULL;
	END IF;

	IF NEW.state = 'P' THEN
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
