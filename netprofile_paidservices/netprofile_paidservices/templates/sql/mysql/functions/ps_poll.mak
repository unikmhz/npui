## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE done, psid INT UNSIGNED DEFAULT 0;
	DECLARE cur CURSOR FOR
		SELECT `pd`.`epid`
		FROM `paid_def` `pd`
		LEFT JOIN `paid_types` `pt`
		USING (`paidid`)
		WHERE ((`pd`.`qpend` < ts) OR (`pd`.`qpend` IS NULL))
		AND `pd`.`active` = 'Y'
		AND `pt`.`qp_type` = 'I';
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;
	OPEN cur;
	REPEAT
		FETCH cur INTO psid;
		IF psid > 0 THEN
			CALL ps_execute(psid, ts);
		END IF;
	UNTIL done END REPEAT;
	CLOSE cur;
</%block>

