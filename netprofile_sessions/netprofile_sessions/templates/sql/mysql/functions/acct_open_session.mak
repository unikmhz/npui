## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE aeid, erateid INT UNSIGNED DEFAULT 0;
	DECLARE ealiasid, xdsid, xdestid INT UNSIGNED DEFAULT NULL;
	DECLARE xdtype ENUM('normal','noquota','onlyquota','reject') CHARACTER SET ascii DEFAULT 'normal';
	DECLARE xpol_in, xpol_eg VARCHAR(255) CHARACTER SET ascii DEFAULT NULL;
	DECLARE rate_oqsum_in, rate_oqsum_eg, rate_oqsum_sec DECIMAL(20,8) DEFAULT 0.0;
	DECLARE rate_abf ENUM('Y', 'N') CHARACTER SET ascii DEFAULT 'N';
	DECLARE EXIT HANDLER FOR NOT FOUND BEGIN
		SELECT 0 AS `snum`;
		ROLLBACK;
	END;

	IF fip = 0 THEN
		SET fip := NULL;
	END IF;
	IF fip6 = 0 THEN
		SET fip6 := NULL;
	END IF;
	IF xnasid = 0 THEN
		SET xnasid := NULL;
	END IF;
	IF csid = "" THEN
		SET csid := NULL;
	END IF;
	IF called = "" THEN
		SET called := NULL;
	END IF;
	IF pol_in = "" THEN
		SET pol_in := NULL;
	END IF;
	IF pol_eg = "" THEN
		SET pol_eg := NULL;
	END IF;

	START TRANSACTION;

	SELECT `entityid`, `rateid`, `aliasid`
	INTO aeid, erateid, ealiasid
	FROM `entities_access`
	LEFT JOIN `entities_def`
	USING(`entityid`)
	WHERE `nick` = name;
	IF ealiasid IS NOT NULL THEN
		REPEAT
			SELECT `entityid`, `rateid`, `aliasid`
			INTO aeid, erateid, ealiasid
			FROM `entities_access`
			LEFT JOIN `entities_def`
			USING(`entityid`)
			WHERE `entityid` = ealiasid;
		UNTIL ealiasid IS NULL END REPEAT;
	END IF;

	IF (erateid IS NULL) OR (erateid = 0) THEN
		SELECT 0 AS `snum`;
		ROLLBACK;
		LEAVE aosfunc;
	END IF;

	SELECT `abf`, `dsid`, `oqsum_ingress`, `oqsum_egress`, `oqsum_sec`, `pol_ingress`, `pol_egress`
	INTO rate_abf, xdsid, rate_oqsum_in, rate_oqsum_eg, rate_oqsum_sec, xpol_in, xpol_eg
	FROM `rates_def`
	WHERE `rateid` = erateid;

	IF rate_abf = 'Y' THEN
		CALL acct_rate_mods(ts, erateid, aeid, rate_oqsum_in, rate_oqsum_eg, rate_oqsum_sec, xpol_in, xpol_eg);
	END IF;

	IF pol_in IS NULL THEN
		SET pol_in := xpol_in;
	END IF;
	IF pol_eg IS NULL THEN
		SET pol_eg := xpol_eg;
	END IF;

	IF (xdsid IS NOT NULL) AND (called IS NOT NULL) THEN
		CALL acct_rate_dest(ts, erateid, xdsid, called, xdestid, xdtype, rate_oqsum_sec);
		IF xdtype = 'reject' THEN
			SELECT 0 AS `snum`;
			ROLLBACK;
			LEAVE aosfunc;
		END IF;
	END IF;

	INSERT INTO `sessions_def` (`name`, `stationid`, `entityid`, `ipaddrid`, `ip6addrid`, `destid`, `nasid`, `csid`, `called`, `startts`, `updatets`, `ut_ingress`, `ut_egress`, `pol_ingress`, `pol_egress`)
	VALUES (sid, stid, aeid, fip, fip6, xdestid, xnasid, csid, called, ts, ts, 0, 0, pol_in, pol_eg);
	SELECT LAST_INSERT_ID() AS `snum`;
	COMMIT;
</%block>

