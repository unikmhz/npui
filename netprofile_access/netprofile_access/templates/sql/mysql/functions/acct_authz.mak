## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE nf BOOLEAN DEFAULT FALSE;
	DECLARE entid, user_rateid, user_nextrateid INT UNSIGNED DEFAULT 0;
	DECLARE ealiasid INT UNSIGNED DEFAULT NULL;
	DECLARE userpass_crypt, userpass_plain, userpol_in, userpol_eg VARCHAR(255) DEFAULT NULL;
	DECLARE userpass_ntlm CHAR(32) CHARACTER SET ascii DEFAULT NULL;
	DECLARE user_state TINYINT UNSIGNED DEFAULT 0;
	DECLARE ts, user_qpend DATETIME DEFAULT NULL;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET nf := TRUE;

	SELECT `entityid`, `aliasid`, `pwd_ntlm`, `pwd_crypt`, `pwd_plain`, `rateid`, `nextrateid`, `state`, `qpend`
	INTO entid, ealiasid, userpass_ntlm, userpass_crypt, userpass_plain, user_rateid, user_nextrateid, user_state, user_qpend
	FROM `entities_access`
	LEFT JOIN `entities_def`
	USING(`entityid`)
	WHERE `nick` = name;
	IF nf = TRUE THEN
		SELECT
			NULL AS `entityid`,
			NULL AS `username`,
			NULL AS `pwd_ntlm`,
			NULL AS `pwd_crypt`,
			NULL AS `pwd_plain`,
			NULL AS `policy_in`,
			NULL AS `policy_eg`,
			99 AS `state`;
		LEAVE authzfunc;
	END IF;
	IF ealiasid IS NOT NULL THEN
		REPEAT
			SELECT `entityid`, `aliasid`, `rateid`, `nextrateid`, `qpend`
			INTO entid, ealiasid, user_rateid, user_nextrateid, user_qpend
			FROM `entities_access`
			WHERE `entityid` = ealiasid
			AND `state` = 0;
		UNTIL (ealiasid IS NULL) OR (nf = TRUE) END REPEAT;
		IF nf = TRUE THEN
			SELECT
				NULL AS `entityid`,
				NULL AS `username`,
				NULL AS `pwd_ntlm`,
				NULL AS `pwd_crypt`,
				NULL AS `pwd_plain`,
				NULL AS `policy_in`,
				NULL AS `policy_eg`,
				99 AS `state`;
			LEAVE authzfunc;
		END IF;
	END IF;
	IF (user_nextrateid IS NOT NULL) AND (user_nextrateid <> user_rateid) THEN
		SET ts := NOW();
		IF (user_qpend IS NULL) OR (user_qpend < ts) THEN
			SET user_rateid := user_nextrateid;
		END IF;
	END IF;
	SELECT `pol_ingress`, `pol_egress`
	INTO userpol_in, userpol_eg
	FROM `rates_def`
	WHERE `rateid` = user_rateid;
	SELECT
		entid AS `entityid`,
		name AS `username`,
		userpass_ntlm AS `pwd_ntlm`,
		userpass_crypt AS `pwd_crypt`,
		userpass_plain AS `pwd_plain`,
		userpol_in AS `policy_in`,
		userpol_eg AS `policy_eg`,
		user_state AS `state`;
</%block>

