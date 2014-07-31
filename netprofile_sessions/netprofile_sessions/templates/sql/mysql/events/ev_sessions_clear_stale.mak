## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_event.mak"/>\
<%block name="sql">\
	DECLARE stid, done INT UNSIGNED DEFAULT 0;
	DECLARE sid VARCHAR(255);
	DECLARE xsessid BIGINT UNSIGNED DEFAULT 0;
	DECLARE cur CURSOR FOR
		SELECT `stationid`, `name`
		FROM `sessions_def`
		WHERE `updatets` < NOW() - INTERVAL (SELECT CAST(`value` AS SIGNED) FROM `np_globalsettings_def` WHERE `name` = 'acct_stale_cutoff') SECOND;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;

	SET @accessuid := 0;
	SET @accessgid := 0;
	SET @accesslogin := '[EV:SESSIONS_CLEAR_STALE]';
	OPEN cur;
	REPEAT
		START TRANSACTION;

		SET stid := 0;
		SET xsessid := 0;
		FETCH cur INTO stid, sid;
		IF stid > 0 THEN
			SELECT `sessid` INTO xsessid
			FROM `sessions_def`
			WHERE `stationid` =  stid AND `name` = sid
			FOR UPDATE;

			IF xsessid > 0 THEN
				DELETE FROM `sessions_def` WHERE `sessid` = xsessid;
			END IF;
		END IF;

		COMMIT;
	UNTIL done END REPEAT;
	CLOSE cur;
</%block>

