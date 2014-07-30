## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE fo DECIMAL(39,0) UNSIGNED DEFAULT 1;
	DECLARE tmp, offmax DECIMAL(39,0) UNSIGNED DEFAULT 0;
	DECLARE done, found INT UNSIGNED DEFAULT 0;
	DECLARE cur CURSOR FOR
		SELECT `offset`
		FROM `ip6addr_def`
		WHERE `netid` = net
		ORDER BY `offset` ASC;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;

	SELECT POW(2, 128 - `cidr6`) - 1 INTO offmax
	FROM `nets_def`
	WHERE `netid` = net;
	IF done = 1 THEN
		RETURN NULL;
	END IF;
	OPEN cur;
	cfx: REPEAT
		IF fo >= offmax THEN
			LEAVE cfx;
		END IF;
		FETCH cur INTO tmp;
		IF tmp <> fo THEN
			SET found := 1;
			LEAVE cfx;
		END IF;
		SET fo := fo + 1;
	UNTIL done END REPEAT;
	CLOSE cur;
	IF found = 0 THEN
		RETURN NULL;
	END IF;
	RETURN fo;
</%block>
