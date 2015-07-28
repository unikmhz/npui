## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE xdate, cdate DATE DEFAULT NULL;
	DECLARE xrev TINYINT UNSIGNED DEFAULT 0;
	DECLARE ipm BINARY(16) DEFAULT NULL;
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

	SET cdate := CURDATE();

	SELECT `ip6addr` INTO ipm
	FROM `nets_def`
	WHERE `netid` = OLD.netid;

	SET ipm := UNHEX(RPAD(SUBSTRING(HEX(ipm) FROM 1 FOR 16), 32, '0'));

	SELECT `date`, `rev`
	INTO xdate, xrev
	FROM `revzone_serials6`
	WHERE `ip6addr` = ipm
	AND `date` = cdate
	FOR UPDATE;

	IF xdate IS NULL THEN
		REPLACE INTO `revzone_serials6` (`ip6addr`, `date`, `rev`)
		VALUES (ipm, cdate, 1);
	ELSE
		UPDATE `revzone_serials6`
		SET `rev` = xrev + 1
		WHERE `ip6addr` = ipm;
	END IF;

	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 19, 3, CONCAT_WS(" ",
		"Deleted IPv6 address",
		CONCAT("[ID ", OLD.ip6addrid, "]")
	));
</%block>
