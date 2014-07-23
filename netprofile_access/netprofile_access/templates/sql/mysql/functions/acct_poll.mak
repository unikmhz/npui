## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE done, aeid INT UNSIGNED DEFAULT 0;
	DECLARE nick VARCHAR(255) DEFAULT NULL;
	DECLARE cur CURSOR FOR
		SELECT `ea`.`entityid` `entityid`, `ed`.`nick` `nick`
		FROM `entities_access` `ea`
		LEFT JOIN `entities_def` `ed`
		USING(`entityid`)
		WHERE `ea`.`state` <> 2
		AND `ea`.`aliasid` IS NULL
		AND `ea`.`rateid` IN(SELECT `rateid` FROM `rates_def` WHERE `polled` = 'Y');
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;
	OPEN cur;
	REPEAT
		FETCH cur INTO aeid, nick;
		IF aeid > 0 THEN
			CALL acct_add(aeid, nick, 0, 0, ts);
		END IF;
	UNTIL done END REPEAT;
	CLOSE cur;
</%block>
