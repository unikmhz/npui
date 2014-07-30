## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE pt_qpt ENUM('I', 'L', 'O') DEFAULT 'I';

	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 14, 1, CONCAT_WS(" ",
		"New paid service",
		CONCAT("[ID ", NEW.epid, "]"),
		CONCAT("[ENTITYID ", NEW.entityid, "]"),
		CONCAT("[STASHID ", NEW.stashid, "]"),
		CONCAT("[PAIDID ", NEW.paidid, "]")
	));

	IF (NEW.aeid IS NOT NULL) AND (NEW.active = 'Y') THEN
		SELECT `qp_type`
		INTO pt_qpt
		FROM `paid_types`
		WHERE `paidid` = NEW.paidid;
		IF (pt_qpt = 'L') THEN
			UPDATE `entities_access`
			SET `pcheck` = 'Y'
			WHERE `entityid` = NEW.aeid;
		END IF;
	END IF;
</%block>
