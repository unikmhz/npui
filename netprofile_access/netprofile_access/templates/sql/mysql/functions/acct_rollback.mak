## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE done INT UNSIGNED DEFAULT 0;
	DECLARE xqsum DECIMAL(20,8) DEFAULT 0.0;
	DECLARE startts DATETIME;
	DECLARE qpa SMALLINT UNSIGNED;
	DECLARE qpu ENUM('a_hour', 'a_day', 'a_week', 'a_month', 'c_hour', 'c_day', 'c_month', 'f_hour', 'f_day', 'f_week', 'f_month') CHARACTER SET ascii;
	DECLARE CONTINUE HANDLER FOR NOT FOUND
		SET done := 1;

	SELECT `qp_amount`, `qp_unit`, `qsum`
	INTO qpa, qpu, xqsum
	FROM `rates_def`
	WHERE `rateid` = xrateid_old;
	IF done = 1 THEN
		LEAVE rbfunc;
	END IF;

	SET xdiff := 0.0;

	IF @npa_rollback_type = 'none' THEN
		SET uti := 0;
		SET ute := 0;
		SET xqpend := NULL;
		IF xstate < 2 THEN
			SET xstate := 0;
		END IF;
		LEAVE rbfunc;
	ELSEIF xqpend IS NULL THEN
		SET uti := 0;
		SET ute := 0;
		IF xstate < 2 THEN
			SET xstate := 0;
		END IF;
	ELSE
		CASE @npa_rollback_type
			WHEN 'full' THEN
				SET uti := 0;
				SET ute := 0;
				SET xdiff := xqsum;
				SET xqpend := NULL;
				IF xstate < 2 THEN
					SET xstate := 0;
				END IF;
			WHEN 'accounted' THEN
				SET startts := ts - INTERVAL acct_rate_qpspent(qpa, qpu, ts, xqpend) SECOND;
				SELECT SUM(`diff`), SUM(`acct_ingress`), SUM(`acct_egress`)
				INTO xdiff, uti, ute
				FROM `stashes_ops`
				WHERE `entityid` = aeid
				AND `ts` BETWEEN startts AND xqpend;
				SET xqpend := NULL;
				IF xstate < 2 THEN
					SET xstate := 0;
				END IF;
			ELSE
				SET uti := 0;
				SET ute := 0;
				SET xdiff := xqsum * acct_rate_percent_remaining(qpa, qpu, ts, xqpend);
				SET xqpend := NULL;
				IF xstate < 2 THEN
					SET xstate := 0;
				END IF;
		END CASE;
	END IF;
</%block>

