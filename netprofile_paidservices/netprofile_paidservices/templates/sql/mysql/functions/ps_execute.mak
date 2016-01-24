## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE ps_entityid, ps_aeid, ps_hostid, ps_stashid, ps_paidid INT UNSIGNED DEFAULT 0;
	DECLARE stash_currid INT UNSIGNED DEFAULT NULL;
	DECLARE ps_active, is_initial ENUM('Y', 'N') CHARACTER SET ascii DEFAULT 'N';
	DECLARE curr_credit ENUM('Y', 'N') CHARACTER SET ascii DEFAULT 'Y';
	DECLARE ps_qpend DATETIME DEFAULT NULL;
	DECLARE stash_amount, stash_credit, pay, pt_isum, pt_qsum DECIMAL(20,8) DEFAULT 0.0;
	DECLARE curr_xrate DECIMAL(20,8) DEFAULT 1.0;
	DECLARE pt_spa, pt_qpa SMALLINT UNSIGNED DEFAULT 1;
	DECLARE pt_qpu ENUM('a_hour', 'a_day', 'a_week', 'a_month', 'c_hour', 'c_day', 'c_month', 'f_hour', 'f_day', 'f_week', 'f_month') CHARACTER SET ascii DEFAULT 'c_month';
	DECLARE pt_qpt ENUM('I', 'L', 'O') DEFAULT 'I';
	DECLARE pt_name, pt_cb_before, pt_cb_success, pt_cb_failure VARCHAR(255) DEFAULT NULL;
	DECLARE EXIT HANDLER FOR NOT FOUND
	BEGIN
		ROLLBACK;
	END;

	START TRANSACTION;

	SELECT `entityid`, `aeid`, `hostid`, `stashid`, `paidid`, `active`, `qpend`
	INTO ps_entityid, ps_aeid, ps_hostid, ps_stashid, ps_paidid, ps_active, ps_qpend
	FROM `paid_def`
	WHERE `epid` = xepid
	FOR UPDATE;

	IF (ps_active = 'N') THEN
		ROLLBACK;
		LEAVE psefunc;
	END IF;
	IF (ps_qpend IS NOT NULL) AND (ts <= ps_qpend) THEN
		ROLLBACK;
		LEAVE psefunc;
	END IF;

	SELECT `name`, `isum`, `qsum`, `qp_type`, `sp_amount`, `qp_amount`, `qp_unit`, `cb_before`, `cb_success`, `cb_failure`
	INTO pt_name, pt_isum, pt_qsum, pt_qpt, pt_spa, pt_qpa, pt_qpu, pt_cb_before, pt_cb_success, pt_cb_failure
	FROM `paid_types`
	WHERE `paidid` = ps_paidid
	LOCK IN SHARE MODE;

	IF(pt_qpt <> 'I') THEN
		ROLLBACK;
		LEAVE psefunc;
	END IF;

	SELECT `currid`, `amount`, `credit`
	INTO stash_currid, stash_amount, stash_credit
	FROM `stashes_def`
	WHERE `stashid` = ps_stashid
	FOR UPDATE;

	IF stash_currid IS NOT NULL THEN
		SELECT `xchange_rate`, `allow_credit`
		INTO curr_xrate, curr_credit
		FROM `currencies_def`
		WHERE `currid` = stash_currid;

		SET pt_isum := pt_isum / curr_xrate;
		SET pt_qsum := pt_qsum / curr_xrate;

		IF curr_credit = 'N' THEN
			SET stash_credit := 0.0;
		END IF;
	END IF;

	IF ps_qpend IS NULL THEN
		SET is_initial := 'Y';
		SET pay := pt_isum;
		SET ps_qpend := FROM_UNIXTIME(UNIX_TIMESTAMP(ts) + acct_rate_qpnew(pt_spa + pt_qpa, pt_qpu, ts));
	ELSE
		SET is_initial := 'N';
		SET pay := pt_qsum;
		SET ps_qpend := FROM_UNIXTIME(UNIX_TIMESTAMP(ts) + acct_rate_qpnew(pt_qpa, pt_qpu, ts));
	END IF;

	IF pt_cb_before IS NOT NULL THEN
		CALL ps_callback(pt_cb_before, xepid, ts, ps_aeid, ps_hostid, ps_paidid, ps_entityid, ps_stashid, ps_qpend, pay);
	END IF;

	IF (pay > 0) AND ((stash_amount + stash_credit) < pay) THEN
		IF pt_cb_failure IS NOT NULL THEN
			CALL ps_callback(pt_cb_failure, xepid, ts, ps_aeid, ps_hostid, ps_paidid, ps_entityid, ps_stashid, ps_qpend, pay);
		END IF;
	ELSE
		IF pt_cb_success IS NOT NULL THEN
			CALL ps_callback(pt_cb_success, xepid, ts, ps_aeid, ps_hostid, ps_paidid, ps_entityid, ps_stashid, ps_qpend, pay);
		END IF;

		IF (pay > 0) THEN
			INSERT INTO `stashes_io_def` (`siotypeid`, `stashid`, `currid`, `entityid`, `ts`, `diff`, `descr`)
			VALUES (
				(SELECT `siotypeid` FROM `stashes_io_types` WHERE `ftype` = IF(is_initial = 'Y', 'ps_isum', 'ps_qsum')),
				ps_stashid, stash_currid, IF(ps_aeid IS NULL, ps_entityid, ps_aeid), ts, -pay, pt_name
			);

			UPDATE `stashes_def`
			SET `amount` = `amount` - pay
			WHERE `stashid` = ps_stashid;
		END IF;

		UPDATE `paid_def`
		SET `qpend` = ps_qpend
		WHERE `epid` = xepid;
	END IF;

	COMMIT;
</%block>

