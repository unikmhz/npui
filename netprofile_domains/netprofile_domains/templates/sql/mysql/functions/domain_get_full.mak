## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE domstr, tmp VARCHAR(255) DEFAULT '';
	DECLARE parent INT UNSIGNED DEFAULT NULL;
	SELECT `parentid`, `name` INTO parent, domstr
	FROM `domains_def`
	WHERE `domainid` = did;
	IF parent IS NULL THEN
		RETURN domstr;
	END IF;
	REPEAT
		SELECT `parentid`, `name` INTO parent, tmp
		FROM `domains_def`
		WHERE `domainid` = parent;
		SET domstr := CONCAT(domstr, '.', tmp);
	UNTIL parent IS NULL END REPEAT;
	RETURN domstr;
</%block>
