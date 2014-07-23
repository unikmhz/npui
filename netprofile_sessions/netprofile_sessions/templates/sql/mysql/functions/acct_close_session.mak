## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE xsessid BIGINT UNSIGNED DEFAULT 0;

	START TRANSACTION;

	SELECT `sessid` INTO xsessid
	FROM `sessions_def`
	WHERE `stationid` = stid AND `name` = sid
	FOR UPDATE;

	IF xsessid > 0 THEN
		DELETE FROM `sessions_def`
		WHERE `sessid` = xsessid;
		COMMIT;
	ELSE
		ROLLBACK;
	END IF;
</%block>

