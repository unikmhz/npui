## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE pt_qpt ENUM('I', 'L', 'O') DEFAULT 'I';
	DECLARE xcnt INT UNSIGNED DEFAULT 0;

	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 14, 2, CONCAT_WS(" ",
		"Modified paid service",
		CONCAT("[ID ", NEW.epid, "]")
	));

	IF (NEW.aeid IS NOT NULL) THEN
		SELECT `qp_type`
		INTO pt_qpt
		FROM `paid_types`
		WHERE `paidid` = NEW.paidid;
		IF (pt_qpt = 'L') THEN
			IF (OLD.active = 'N') AND (NEW.active = 'Y') THEN
				UPDATE `entities_access`
				SET `pcheck` = 'Y'
				WHERE `entityid` = NEW.aeid;
			END IF;
			IF (OLD.active = 'Y') AND (NEW.active = 'N') THEN
				SELECT COUNT(*)
				INTO xcnt
				FROM `paid_def` `pd`
				LEFT JOIN `paid_types` `pt`
				USING (`paidid`)
				WHERE `pd`.`aeid` = NEW.aeid
				AND `pd`.`active` = 'Y'
				AND `pt`.`qp_type` = 'L';
				IF (xcnt = 0) THEN
					UPDATE `entities_access`
					SET `pcheck` = 'N'
					WHERE `entityid` = NEW.aeid;
				END IF;
			END IF;
		END IF;
	END IF;
</%block>
