## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE x_bsid, cser, uid INT UNSIGNED DEFAULT NULL;
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;


	IF @accessuid > 0 THEN
		SET uid := @accessuid;
	END IF;
	SET NEW.ctime := NOW();
	SET NEW.ptime := NULL;
	SET NEW.cby := uid;
	SET NEW.mby := uid;
	SET NEW.pby := NULL;

	SELECT `bsid`
	INTO x_bsid
	FROM `bills_types`
	WHERE `btypeid` = NEW.btypeid;
	IF x_bsid IS NOT NULL THEN
		SELECT `value`
		INTO cser
		FROM `bills_serials`
		WHERE `bsid` = x_bsid
		FOR UPDATE;

		UPDATE `bills_serials`
		SET `value` = cser + 1
		WHERE `bsid` = x_bsid;

		SET NEW.serial := cser;
	ELSE
		SET NEW.serial := NULL;
	END IF;
</%block>
