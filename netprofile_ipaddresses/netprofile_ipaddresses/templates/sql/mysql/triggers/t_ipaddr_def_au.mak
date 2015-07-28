## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE xdate, cdate DATE DEFAULT NULL;
	DECLARE xrev TINYINT UNSIGNED DEFAULT 0;
	DECLARE ipm INT UNSIGNED DEFAULT 0;
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

	IF (OLD.hostid <> NEW.hostid)
	OR (OLD.netid <> NEW.netid)
	OR (OLD.offset <> NEW.offset)
	OR (OLD.hwaddr <> NEW.hwaddr)
	OR (OLD.ttl <> NEW.ttl)
	THEN
		SET cdate := CURDATE();

		SELECT `ipaddr` INTO ipm
		FROM `nets_def`
		WHERE `netid` = NEW.netid;
		SET ipm := (ipm + NEW.offset) & 0xFFFFFF00;

		SELECT `date`, `rev`
		INTO xdate, xrev
		FROM `revzone_serials`
		WHERE `ipaddr` = ipm
		AND `date` = cdate
		FOR UPDATE;

		IF xdate IS NULL THEN
			REPLACE INTO `revzone_serials` (`ipaddr`, `date`, `rev`)
			VALUES (ipm, cdate, 1);
		ELSE
			UPDATE `revzone_serials`
			SET `rev` = xrev + 1
			WHERE `ipaddr` = ipm;
		END IF;
	END IF;

	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 8, 2, CONCAT_WS(" ",
		"Modified IP address",
		CONCAT("[ID ", NEW.ipaddrid, "]")
	));
</%block>
