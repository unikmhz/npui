## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_event.mak"/>\
<%block name="sql">\
	DECLARE done, xipaddrid INT UNSIGNED DEFAULT 0;
	DECLARE xip6addrid BIGINT UNSIGNED DEFAULT 0;
	DECLARE cur4 CURSOR FOR
		SELECT `ipaddrid`
		FROM `ipaddr_def`
		WHERE `inuse` = 'Y'
		AND `ipaddrid` NOT IN(SELECT DISTINCT `ipaddrid` FROM `sessions_def` WHERE `ipaddrid` IS NOT NULL);
	DECLARE cur6 CURSOR FOR
		SELECT `ip6addrid`
		FROM `ip6addr_def`
		WHERE `inuse` = 'Y'
		AND `ip6addrid` NOT IN(SELECT DISTINCT `ip6addrid` FROM `sessions_def` WHERE `ip6addrid` IS NOT NULL);
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;

	SET @accessuid := 0;
	SET @accessgid := 0;
	SET @accesslogin := '[EV:IPADDR_CLEAR_STALE]';
	OPEN cur4;
	REPEAT
		SET xipaddrid := 0;
		FETCH cur4 INTO xipaddrid;
		IF xipaddrid > 0 THEN
			UPDATE `ipaddr_def`
			SET `inuse` = 'N'
			WHERE `ipaddrid` = xipaddrid;
		END IF;
	UNTIL done END REPEAT;
	CLOSE cur4;
	SET done := 0;
	OPEN cur6;
	REPEAT
		SET xip6addrid := 0;
		FETCH cur6 INTO xip6addrid;
		IF xip6addrid > 0 THEN
			UPDATE `ip6addr_def`
			SET `inuse` = 'N'
			WHERE `ip6addrid` = xip6addrid;
		END IF;
	UNTIL done END REPEAT;
	CLOSE cur6;
</%block>

