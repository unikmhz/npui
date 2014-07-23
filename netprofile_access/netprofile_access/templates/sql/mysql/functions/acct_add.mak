## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE user_stashid, user_rateid, user_aliasid INT UNSIGNED DEFAULT 0;
	DECLARE user_nextrateid INT UNSIGNED DEFAULT NULL;
	DECLARE user_uin, user_ueg, rate_qti, rate_qte DECIMAL(16,0) UNSIGNED DEFAULT 0;
	DECLARE user_qpend, user_qporig DATETIME DEFAULT NULL;
	DECLARE user_state TINYINT UNSIGNED DEFAULT 0;
	DECLARE user_bcheck, user_pcheck, rate_abf ENUM('Y', 'N') CHARACTER SET ascii DEFAULT 'N';
	DECLARE isok, rate_oqi, rate_oqe ENUM('Y', 'N') CHARACTER SET ascii DEFAULT 'Y';
	DECLARE stash_amount, stash_amorig, stash_credit, rate_qsum, rate_oqsum_in, rate_oqsum_eg, rate_oqsum_sec, payq, payin, payout DECIMAL(20,8) DEFAULT 0.0;
	DECLARE rate_auxsum DECIMAL(20,8) DEFAULT NULL;
	DECLARE rate_type ENUM('prepaid', 'prepaid_cont', 'postpaid', 'free');
	DECLARE rate_qpa SMALLINT UNSIGNED DEFAULT 1;
	DECLARE rate_qpu ENUM('a_hour', 'a_day', 'a_week', 'a_month', 'c_hour', 'c_day', 'c_month', 'f_hour', 'f_day', 'f_week', 'f_month') CHARACTER SET ascii DEFAULT 'c_month';
	DECLARE stashop_type ENUM('sub_qin_qeg', 'sub_min_qeg', 'sub_oqin_qeg', 'sub_qin_meg', 'sub_qin_oqeg', 'sub_min_meg', 'sub_oqin_meg', 'sub_min_oqeg', 'sub_oqin_oqeg', 'add_cash', 'add_auto', 'oper');
	DECLARE st_in VARCHAR(5) DEFAULT 'qin';
	DECLARE st_eg VARCHAR(5) DEFAULT 'qeg';
	DECLARE newpol_in, newpol_eg VARCHAR(255) CHARACTER SET ascii DEFAULT NULL;
	DECLARE stashop_comments TEXT DEFAULT NULL;
	DECLARE EXIT HANDLER FOR NOT FOUND BEGIN
		SELECT
			NULL AS `diff`,
			99 AS `state`,
			NULL AS `policy_in`,
			NULL AS `policy_eg`;
		ROLLBACK;
	END;

	START TRANSACTION;

	SELECT `stashid`, `rateid`, `nextrateid`, `aliasid`, `ut_ingress`, `ut_egress`, `qpend`, `state`, `bcheck`, `pcheck`
	INTO user_stashid, user_rateid, user_nextrateid, user_aliasid, user_uin, user_ueg, user_qpend, user_state, user_bcheck, user_pcheck
	FROM `entities_access`
	WHERE `entityid` = aeid
	FOR UPDATE;

	IF (user_state = 2) OR (user_aliasid IS NOT NULL) THEN
		SELECT
			NULL AS `diff`,
			2 AS `state`,
			NULL AS `policy_in`,
			NULL AS `policy_eg`
		FROM DUAL;
		ROLLBACK;
		LEAVE aafunc;
	END IF;

	SET @acct_aeid := aeid;
	SELECT `type`, `abf`, `qp_amount`, `qp_unit`, `qt_ingress`, `qt_egress`, `qsum`, `auxsum`, `oqsum_ingress`, `oqsum_egress`, `oq_ingress`, `oq_egress`, `pol_ingress`, `pol_egress`
	INTO rate_type, rate_abf, rate_qpa, rate_qpu, rate_qti, rate_qte, rate_qsum, rate_auxsum, rate_oqsum_in, rate_oqsum_eg, rate_oqi, rate_oqe, newpol_in, newpol_eg
	FROM `rates_def`
	WHERE `rateid` = user_rateid;

	IF rate_abf = 'Y' THEN
		CALL acct_rate_mods(ts, user_rateid, aeid, rate_oqsum_in, rate_oqsum_eg, rate_oqsum_sec, newpol_in, newpol_eg);
	END IF;

	SELECT `amount`, `credit`
	INTO stash_amount, stash_credit
	FROM `stashes_def`
	WHERE `stashid` = user_stashid
	FOR UPDATE;

	SET user_qporig := user_qpend;
	SET stash_amorig := stash_amount;
	SET stashop_type := 'sub_qin_qeg';

	IF rate_type IN('prepaid', 'prepaid_cont') THEN
		IF (user_uin + tin) > rate_qti THEN
			IF user_uin < rate_qti THEN
				SET payin := (user_uin + tin - rate_qti) * rate_oqsum_in;
				SET st_in := 'min';
			ELSE
				SET payin := tin * rate_oqsum_in;
				SET st_in := 'oqin';
			END IF;
		END IF;
		IF (user_ueg + teg) > rate_qte THEN
			IF user_ueg < rate_qte THEN
				SET payout := (user_ueg + teg - rate_qte) * rate_oqsum_eg;
				SET st_eg := 'meg';
			ELSE
				SET payout := teg * rate_oqsum_eg;
				SET st_eg := 'oqeg';
			END IF;
		END IF;
	END IF;

	SET user_uin := user_uin + tin;
	SET user_ueg := user_ueg + teg;

	IF (user_qpend < ts) OR (user_qpend IS NULL) THEN
		IF (user_bcheck = 'Y') THEN
		BEGIN
			DECLARE ab_id INT UNSIGNED DEFAULT 0;
			DECLARE ab_state ENUM('planned', 'active', 'expired') DEFAULT 'expired';
			DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

			SELECT `abid`, `bstate` INTO ab_id, ab_state
			FROM `accessblock_def`
			WHERE `entityid` = aeid
			AND `bstate` IN('planned', 'active')
			AND ts BETWEEN `startts` AND `endts`
			LIMIT 1;

			IF ab_id > 0 THEN
				IF ab_state = 'planned' THEN
					UPDATE `accessblock_def`
					SET
						`bstate` = 'active',
						`oldstate` = user_state
					WHERE `abid` = ab_id;
				END IF;
				UPDATE `entities_access`
				SET
					`state` = 2,
					`bcheck` = 'N'
				WHERE `entityid` = aeid;
				COMMIT;
				LEAVE aafunc;
			END IF;
		END;
		END IF;
		SET payq := rate_qsum;
		IF (rate_type = 'postpaid') AND (user_qpend IS NOT NULL) THEN
			IF user_uin > rate_qti THEN
				SET payin := (user_uin - rate_qti) * rate_oqsum_in;
				SET st_in := 'min';
			END IF;
			IF user_ueg > rate_qte THEN
				SET payout := (user_ueg - rate_qte) * rate_oqsum_eg;
				SET st_eg := 'meg';
			END IF;
			IF (user_pcheck = 'Y') THEN
				SET isok := 'Y';
				CALL acct_pcheck(aeid, ts, rate_type, isok, user_stashid, user_qpend, stash_amount, stash_credit, payq, payin, payout);
			END IF;
			SET stash_amount := stash_amount - payq - payin - payout;
			IF (stash_amount + stash_credit) < 0 THEN
				SET user_state := 1;
			ELSE
				SET user_state := 0;
			END IF;
		END IF;
		IF (user_nextrateid IS NOT NULL) AND (user_nextrateid <> user_rateid) THEN
			SET user_rateid := user_nextrateid;
			SET user_nextrateid := NULL;
			SELECT `type`, `abf`, `qp_amount`, `qp_unit`, `qt_ingress`, `qt_egress`, `qsum`, `auxsum`, `oqsum_ingress`, `oqsum_egress`, `oq_ingress`, `oq_egress`, `pol_ingress`, `pol_egress`
			INTO rate_type, rate_abf, rate_qpa, rate_qpu, rate_qti, rate_qte, rate_qsum, rate_auxsum, rate_oqsum_in, rate_oqsum_eg, rate_oqi, rate_oqe, newpol_in, newpol_eg
			FROM `rates_def`
			WHERE `rateid` = user_rateid;

			SET payq := rate_qsum;

			IF rate_abf = 'Y' THEN
				CALL acct_rate_mods(ts, user_rateid, aeid, rate_oqsum_in, rate_oqsum_eg, rate_oqsum_sec, newpol_in, newpol_eg);
			END IF;
		END IF;
		SET user_qpend := FROM_UNIXTIME(UNIX_TIMESTAMP(ts) + acct_rate_qpnew(rate_qpa, rate_qpu, ts));
		SET user_uin := 0;
		SET user_ueg := 0;
		IF (rate_type IN('prepaid', 'prepaid_cont')) AND (user_pcheck = 'Y') THEN
			SET isok := 'N';
			CALL acct_pcheck(aeid, ts, rate_type, isok, user_stashid, user_qpend, stash_amount, stash_credit, payq, payin, payout);
		END IF;
	END IF;

	IF (
		((user_uin > rate_qti) AND (rate_oqi = 'N'))
	OR
		((user_ueg > rate_qte) AND (rate_oqe = 'N'))
	) THEN
		UPDATE `entities_access`
		SET
			`ut_ingress` = user_uin,
			`ut_egress` = user_ueg,
			`state` = 1
		WHERE `entityid` = aeid;
		SELECT
			0 AS `diff`,
			1 AS `state`,
			NULL AS `policy_in`,
			NULL AS `policy_eg`
		FROM DUAL;
		COMMIT;
		LEAVE aafunc;
	END IF;

	SET stashop_type := CONCAT_WS('_', 'sub', st_in, st_eg);

	IF rate_type IN('prepaid', 'prepaid_cont') THEN
		IF ((stash_amount + stash_credit) < payq) AND (payq > 0) THEN
			SET user_state := 1;
			SET user_qpend := NULL;
			SET payq := 0;
		END IF;
		IF (user_pcheck = 'Y') AND (isok = 'N') THEN
			SET user_state := 1;
			SET user_qpend := NULL;
			SET payq := 0;
		END IF;
		IF (rate_type = 'prepaid_cont') AND (user_state = 1) AND ((stash_amount + stash_credit) < rate_auxsum) THEN
			SET user_qpend := user_qporig;
			SET payq := 0;
		ELSE
			SET stash_amount := stash_amount - payq - payin - payout;
			IF (stash_amount + stash_credit) < 0 THEN
				SET user_state := 1;
			ELSEIF user_qpend IS NOT NULL THEN
				SET user_state := 0;
			END IF;
		END IF;
	END IF;

	SET @ae_ignore := 1;
	UPDATE `entities_access` SET
		`rateid` = user_rateid,
		`nextrateid` = user_nextrateid,
		`ut_ingress` = user_uin,
		`ut_egress` = user_ueg,
		`qpend` = user_qpend,
		`state` = user_state
	WHERE `entityid` = aeid;
	SET @ae_ignore := NULL;

	UPDATE `stashes_def` SET
		`amount` = stash_amount
	WHERE `stashid` = user_stashid;

	IF (stash_amount <> stash_amorig) AND (payq > 0) THEN
		SET @stashio_ignore := 1;
		INSERT INTO `stashes_io_def` (`siotypeid`, `stashid`, `entityid`, `ts`, `diff`)
		VALUES (IF(rate_type = 'postpaid', 2, 1), user_stashid, aeid, ts, -payq);
		SET @stashio_ignore := NULL;
	END IF;
	IF (@npa_all_traffic IS NULL) OR (@npa_all_traffic <> 1) THEN
		IF rate_oqsum_in = 0.0 THEN
			SET tin := 0;
		END IF;
		IF rate_oqsum_eg = 0.0 THEN
			SET teg := 0;
		END IF;
	END IF;
	IF (stash_amount <> stash_amorig) OR (tin > 0) OR (teg > 0) THEN
		INSERT INTO `stashes_ops` (`stashid`, `type`, `ts`, `entityid`, `diff`, `acct_ingress`, `acct_egress`)
		VALUES (user_stashid, stashop_type, ts, aeid, stash_amount - stash_amorig, tin, teg);
	END IF;

	SET @acct_aeid := NULL;
	SELECT
		(stash_amount - stash_amorig) AS `diff`,
		user_state AS `state`,
		NULL AS `policy_in`,
		NULL AS `policy_eg`
	FROM DUAL;

	COMMIT;
</%block>

