## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE nf BOOLEAN DEFAULT FALSE;
	DECLARE entid, user_rateid, user_nextrateid, sessnum, poolid INT UNSIGNED DEFAULT 0;
	DECLARE ealiasid, rate_fsid, filterid INT UNSIGNED DEFAULT NULL;
	DECLARE user_password, userpol_in, userpol_eg VARCHAR(255) DEFAULT NULL;
	DECLARE user_state TINYINT UNSIGNED DEFAULT 0;
	DECLARE ts, user_qpend DATETIME DEFAULT NULL;
	DECLARE user_sim SMALLINT(6) DEFAULT 0;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET nf := TRUE;

	IF r_porttype = -1 THEN
		SET r_porttype := NULL;
	END IF;
	IF r_servicetype = -1 THEN
		SET r_servicetype := NULL;
	END IF;
	IF r_frproto = -1 THEN
		SET r_frproto := NULL;
	END IF;
	IF r_tuntype = -1 THEN
		SET r_tuntype := NULL;
	END IF;
	IF r_tunmedium = -1 THEN
		SET r_tunmedium := NULL;
	END IF;

	SELECT `entityid`, `aliasid`, `password`, `rateid`, `nextrateid`, `state`, `qpend`
	INTO entid, ealiasid, user_password, user_rateid, user_nextrateid, user_state, user_qpend
	FROM `entities_access`
	LEFT JOIN `entities_def`
	USING(`entityid`)
	WHERE `nick` = name;
	IF nf = TRUE THEN
		SELECT
			NULL AS `entityid`,
			NULL AS `username`,
			NULL AS `password`,
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
				NULL AS `password`,
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
	SELECT `fsid`, `sim`, `pol_ingress`, `pol_egress`
	INTO rate_fsid, user_sim, userpol_in, userpol_eg
	FROM `rates_def`
	WHERE `rateid` = user_rateid;
	IF user_sim > 0 THEN
		SELECT COUNT(*)
		INTO sessnum
		FROM `sessions_def`
		WHERE `entityid` = entid;
		IF sessnum >= user_sim THEN
			SELECT
				NULL AS `entityid`,
				NULL AS `username`,
				NULL AS `password`,
				NULL AS `policy_in`,
				NULL AS `policy_eg`,
				3 AS `state`;
			LEAVE authzfunc;
		END IF;
	END IF;
	IF rate_fsid IS NOT NULL THEN
		CALL acct_rate_filter(rate_fsid, r_porttype, r_servicetype, r_frproto, r_tuntype, r_tunmedium, filterid);
		IF filterid IS NULL THEN
			SELECT
				NULL AS `entityid`,
				NULL AS `username`,
				NULL AS `password`,
				NULL AS `policy_in`,
				NULL AS `policy_eg`,
				4 AS `state`;
			LEAVE authzfunc;
		END IF;
	END IF;
	SELECT
		entid AS `entityid`,
		name AS `username`,
		user_password AS `password`,
		userpol_in AS `policy_in`,
		userpol_eg AS `policy_eg`,
		user_state AS `state`;
</%block>

