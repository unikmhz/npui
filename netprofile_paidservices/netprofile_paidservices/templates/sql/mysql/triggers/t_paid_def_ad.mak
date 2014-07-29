## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE pt_qpt ENUM('I', 'L', 'O') DEFAULT 'I';
	DECLARE xcnt INT UNSIGNED DEFAULT 0;

	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 14, 3, CONCAT_WS(" ",
		"Deleted paid service",
		CONCAT("[ID ", OLD.epid, "]")
	));

	IF (OLD.aeid IS NOT NULL) THEN
		SELECT `qp_type`
		INTO pt_qpt
		FROM `paid_types`
		WHERE `paidid` = OLD.paidid;
		IF (pt_qpt = 'L') THEN
			SELECT COUNT(*)
			INTO xcnt
			FROM `paid_def` `pd`
			LEFT JOIN `paid_types` `pt`
			USING (`paidid`)
			WHERE `pd`.`aeid` = OLD.aeid
			AND `pd`.`active` = 'Y'
			AND `pt`.`qp_type` = 'L';
			IF (xcnt = 0) THEN
				UPDATE `entities_access`
				SET `pcheck` = 'N'
				WHERE `entityid` = OLD.aeid;
			END IF;
		END IF;
	END IF;
</%block>
