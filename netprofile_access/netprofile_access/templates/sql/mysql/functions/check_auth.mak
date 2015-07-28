## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE entid INT UNSIGNED DEFAULT 0;
	DECLARE ealiasid INT UNSIGNED DEFAULT NULL;
	DECLARE EXIT HANDLER FOR NOT FOUND RETURN FALSE;
	SELECT `entityid`, `aliasid`
	INTO entid, ealiasid
	FROM `entities_access`
	LEFT JOIN `entities_def`
	USING(`entityid`)
	WHERE `nick` = name AND `password` = pass AND `state` = 0;
	IF ealiasid IS NOT NULL THEN
		REPEAT
			SELECT `entityid`, `aliasid`
			INTO entid, ealiasid
			FROM `entities_access`
			LEFT JOIN `entities_def`
			USING(`entityid`)
			WHERE `entityid` = ealiasid;
		UNTIL ealiasid IS NULL END REPEAT;
	END IF;
	RETURN TRUE;
</%block>
