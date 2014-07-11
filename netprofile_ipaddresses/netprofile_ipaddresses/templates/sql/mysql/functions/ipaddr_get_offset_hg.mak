## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE fo INT UNSIGNED DEFAULT 1;
	DECLARE tmp, done, found, offmin, offmax INT UNSIGNED DEFAULT 0;
	DECLARE dynstart, dynend SMALLINT UNSIGNED DEFAULT 0;
	DECLARE cur CURSOR FOR
		SELECT `offset`
		FROM `ipaddr_def`
		WHERE `netid` = net
		ORDER BY `offset` ASC;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;

	SELECT POW(2, 32 - `cidr`) - 1, `gueststart`, `guestend`
	INTO offmax, dynstart, dynend
	FROM `nets_def`
	WHERE `netid` = net;
	SELECT `startoffset`, IF(`endoffset` > offmax, 0, offmax - `endoffset`) INTO offmin, offmax
	FROM `hosts_groups`
	WHERE `hgid` = hg;
	IF done = 1 OR offmax = 0 OR offmin > offmax THEN
		RETURN NULL;
	END IF;
	SET fo := offmin + 1;
	OPEN cur;
	cfx: REPEAT
		IF fo >= offmax THEN
			LEAVE cfx;
		END IF;
		FETCH cur INTO tmp;
		IF tmp <= offmin THEN
			SET fo := offmin;
		ELSEIF tmp <> fo THEN
			IF dynstart > 0 AND dynend > 0 AND fo BETWEEN dynstart AND dynend THEN
				SET fo := tmp;
			ELSE
				SET found := 1;
				LEAVE cfx;
			END IF;
		END IF;
		SET fo := fo + 1;
	UNTIL done END REPEAT;
	CLOSE cur;
	IF found = 0 THEN
		IF fo = offmin + 1 THEN
			RETURN fo;
		ELSE
			RETURN NULL;
		END IF;
	END IF;
	RETURN fo;
</%block>
