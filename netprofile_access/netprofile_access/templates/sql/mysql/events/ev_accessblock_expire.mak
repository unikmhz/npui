## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_event.mak"/>\
<%block name="sql">\
	DECLARE done, ab_id INT UNSIGNED DEFAULT 0;
	DECLARE cur CURSOR FOR
		SELECT `abid`
		FROM `accessblock_def`
		WHERE `bstate` = 'active'
		AND `endts` < NOW();
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;

	SET @accessuid := 0;
	SET @accessgid := 0;
	SET @accesslogin := '[EV:ACCESSBLOCK_EXPIRE]';
	OPEN cur;
	REPEAT
		START TRANSACTION;

		SET ab_id := 0;
		FETCH cur INTO ab_id;
		IF ab_id > 0 THEN
			UPDATE `accessblock_def`
			SET `bstate` = 'expired'
			WHERE `abid` = ab_id;
		END IF;

		COMMIT;
	UNTIL done END REPEAT;
	CLOSE cur;
</%block>
