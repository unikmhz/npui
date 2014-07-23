## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE done, f_id, f_stashid INT UNSIGNED DEFAULT 0;
	DECLARE f_diff, xpsum DECIMAL(20,8) DEFAULT 0.0;
	DECLARE f_ctime, f_ptime DATETIME;
	DECLARE cur CURSOR FOR
		SELECT `futureid`, `stashid`, `diff`, `ctime`, `ptime`
		FROM `futures_def`
		WHERE `state` = 'A'
		AND `ptime` < NOW()
		FOR UPDATE;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;

	START TRANSACTION;

	OPEN cur;
	REPEAT
		SET f_id := 0;
		FETCH cur INTO f_id, f_stashid, f_diff, f_ctime, f_ptime;
		IF f_id > 0 THEN
			SET xpsum := 0.0;
			SELECT SUM(`diff`)
			INTO xpsum
			FROM `stashes_io_def`
			WHERE (`stashid` = f_stashid)
			AND (`ts` BETWEEN f_ctime AND f_ptime)
			AND `siotypeid` IN(101, 105, 106, 107, 108, 109);
			IF xpsum >= f_diff THEN
				UPDATE `futures_def`
				SET `state` = 'P'
				WHERE `futureid` = f_id;
			ELSE
				UPDATE `futures_def`
				SET `state` = 'C'
				WHERE `futureid` = f_id;
				UPDATE `entities_access`
				SET `state` = 1
				WHERE `stashid` = f_stashid;
			END IF;
		END IF;
	UNTIL done END REPEAT;
	CLOSE cur;

	COMMIT;
</%block>
