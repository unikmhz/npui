## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE ipid, pid, entid, rid, xnasid INT UNSIGNED DEFAULT 0;
	DECLARE sid BIGINT UNSIGNED DEFAULT 0;
	DECLARE EXIT HANDLER FOR NOT FOUND BEGIN
		SELECT 0 AS `ipstr`, 0 AS `nasid`;
		ROLLBACK;
	END;

	START TRANSACTION;

	SELECT `entityid`
	INTO entid
	FROM `entities_def`
	WHERE `nick` = ename AND `etype` = 'access';

	SELECT `ipaddrid`, `rateid`
	INTO ipid, rid
	FROM `entities_access`
	WHERE `entityid` = entid;

	SELECT `nasid`
	INTO xnasid
	FROM `nas_def`
	WHERE `idstr` LIKE nid;

	IF ipid IS NULL THEN
		SELECT `poolid`
		INTO pid
		FROM `rates_def`
		WHERE `rateid` = rid;

		IF pid IS NULL THEN
			SELECT `poolid`
			INTO pid
			FROM `nas_pools`
			WHERE `nasid` = xnasid
			ORDER BY RAND()
			LIMIT 1;
		ELSE
			SELECT `poolid`
			INTO pid
			FROM `nas_pools`
			WHERE `nasid` = xnasid
			AND `poolid` = pid
			LIMIT 1;
		END IF;

		SELECT `ipaddrid`
		INTO ipid
		FROM `ipaddr_def`
		WHERE `inuse` = 'N' AND `poolid` = pid
		LIMIT 1
		FOR UPDATE;
	ELSE
		BEGIN
			DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

			SELECT `sessid`
			INTO sid
			FROM `sessions_def`
			WHERE `ipaddrid` = ipid;

			IF sid > 0 THEN
				DELETE FROM `sessions_def`
				WHERE `sessid` = sid;
			END IF;
		END;

		SELECT `ipaddrid`
		INTO ipid
		FROM `ipaddr_def`
		WHERE `ipaddrid` = ipid
		FOR UPDATE;
	END IF;

	UPDATE `ipaddr_def` SET
		`inuse` = 'Y'
	WHERE `ipaddrid` = ipid;

	SELECT ipid AS `ipstr`, xnasid AS `nasid`;
	COMMIT;
</%block>

