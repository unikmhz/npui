## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE rmt_id, done INT UNSIGNED DEFAULT 0;
	DECLARE rmt_oqsum_ingress_mul, rmt_oqsum_egress_mul, rmt_oqsum_sec_mul DECIMAL(20,8) DEFAULT NULL;
	DECLARE rmt_ow_ingress, rmt_ow_egress, is_ok ENUM('Y', 'N') CHARACTER SET ascii DEFAULT 'N';
	DECLARE rmt_pol_ingress, rmt_pol_egress VARCHAR(255) CHARACTER SET ascii DEFAULT NULL;
	DECLARE bp_s_month, bp_s_mday, bp_s_wday, bp_s_hour, bp_s_minute, bp_e_month, bp_e_mday, bp_e_wday, bp_e_hour, bp_e_minute TINYINT UNSIGNED DEFAULT NULL;
	DECLARE rmcur_global CURSOR FOR
		SELECT
			`rm`.`rmtid`,
			`rmt`.`oqsum_ingress_mul`,
			`rmt`.`oqsum_egress_mul`,
			`rmt`.`oqsum_sec_mul`,
			`rmt`.`ow_ingress`,
			`rmt`.`ow_egress`,
			`rmt`.`pol_ingress`,
			`rmt`.`pol_egress`,
			`bp`.`start_month`,
			`bp`.`start_mday`,
			`bp`.`start_wday`,
			`bp`.`start_hour`,
			`bp`.`start_minute`,
			`bp`.`end_month`,
			`bp`.`end_mday`,
			`bp`.`end_wday`,
			`bp`.`end_hour`,
			`bp`.`end_minute`
		FROM `rates_mods_global` `rm`
		LEFT JOIN `rates_mods_types` `rmt`
		USING(`rmtid`)
		LEFT JOIN `bperiods_def` `bp`
		ON(`rmt`.`bperiodid` = `bp`.`bperiodid`)
		WHERE `rm`.`rateid` = rateid
		AND `rm`.`enabled` = 'Y'
		ORDER BY `l_ord` ASC;
	DECLARE rmcur_peruser CURSOR FOR
		SELECT
			`rm`.`rmtid`,
			`rmt`.`oqsum_ingress_mul`,
			`rmt`.`oqsum_egress_mul`,
			`rmt`.`oqsum_sec_mul`,
			`rmt`.`ow_ingress`,
			`rmt`.`ow_egress`,
			`rmt`.`pol_ingress`,
			`rmt`.`pol_egress`,
			`bp`.`start_month`,
			`bp`.`start_mday`,
			`bp`.`start_wday`,
			`bp`.`start_hour`,
			`bp`.`start_minute`,
			`bp`.`end_month`,
			`bp`.`end_mday`,
			`bp`.`end_wday`,
			`bp`.`end_hour`,
			`bp`.`end_minute`
		FROM `rates_mods_peruser` `rm`
		LEFT JOIN `rates_mods_types` `rmt`
		USING(`rmtid`)
		LEFT JOIN `bperiods_def` `bp`
		ON(`rmt`.`bperiodid` = `bp`.`bperiodid`)
		WHERE `rm`.`entityid` = entityid
		AND `rm`.`enabled` = 'Y'
		AND ((`rm`.`rateid` IS NULL) OR (`rm`.`rateid` = rateid))
		ORDER BY `l_ord` ASC;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;

	OPEN rmcur_global;
	REPEAT
		FETCH
			rmcur_global
		INTO
			rmt_id,
			rmt_oqsum_ingress_mul, rmt_oqsum_egress_mul, rmt_oqsum_sec_mul,
			rmt_ow_ingress, rmt_ow_egress,
			rmt_pol_ingress, rmt_pol_egress,
			bp_s_month, bp_s_mday, bp_s_wday, bp_s_hour, bp_s_minute, bp_e_month, bp_e_mday, bp_e_wday, bp_e_hour, bp_e_minute;
		IF rmt_id > 0 THEN
			SET is_ok := 'Y';

			IF (bp_s_minute IS NOT NULL) AND (bp_e_minute IS NOT NULL) AND (bp_s_minute <= bp_e_minute) THEN
				IF NOT (MINUTE(ts) BETWEEN bp_s_minute AND bp_e_minute) THEN
					SET is_ok := 'N';
				END IF;
			END IF;
			IF (bp_s_hour IS NOT NULL) AND (bp_e_hour IS NOT NULL) AND (bp_s_hour <= bp_e_hour) THEN
				IF NOT (HOUR(ts) BETWEEN bp_s_hour AND bp_e_hour) THEN
					SET is_ok := 'N';
				END IF;
			END IF;
			IF (bp_s_wday IS NOT NULL) AND (bp_e_wday IS NOT NULL) AND (bp_s_wday <= bp_e_wday) THEN
				IF NOT ((WEEKDAY(ts) + 1) BETWEEN bp_s_wday AND bp_e_wday) THEN
					SET is_ok := 'N';
				END IF;
			END IF;
			IF (bp_s_mday IS NOT NULL) AND (bp_e_mday IS NOT NULL) AND (bp_s_mday <= bp_e_mday) THEN
				IF NOT (DAYOFMONTH(ts) BETWEEN bp_s_mday AND bp_e_mday) THEN
					SET is_ok := 'N';
				END IF;
			END IF;
			IF (bp_s_month IS NOT NULL) AND (bp_e_month IS NOT NULL) AND (bp_s_month <= bp_e_month) THEN
				IF NOT (MONTH(ts) BETWEEN bp_s_month AND bp_e_month) THEN
					SET is_ok := 'N';
				END IF;
			END IF;

			IF is_ok = 'Y' THEN
				IF rmt_oqsum_ingress_mul IS NOT NULL THEN
					SET oqsum_in := oqsum_in * rmt_oqsum_ingress_mul;
				END IF;
				IF rmt_oqsum_egress_mul IS NOT NULL THEN
					SET oqsum_eg := oqsum_eg * rmt_oqsum_egress_mul;
				END IF;
				IF rmt_oqsum_sec_mul IS NOT NULL THEN
					SET oqsum_sec := oqsum_sec * rmt_oqsum_sec_mul;
				END IF;
				IF rmt_pol_ingress IS NOT NULL THEN
					IF rmt_ow_ingress = 'Y' THEN
						SET pol_in := rmt_pol_ingress;
					ELSE
						SET pol_in := CONCAT_WS(' ', pol_in, rmt_pol_ingress);
					END IF;
				END IF;
				IF rmt_pol_egress IS NOT NULL THEN
					IF rmt_ow_egress = 'Y' THEN
						SET pol_eg := rmt_pol_egress;
					ELSE
						SET pol_eg := CONCAT_WS(' ', pol_eg, rmt_pol_egress);
					END IF;
				END IF;
			END IF;
		END IF;
	UNTIL done END REPEAT;
	CLOSE rmcur_global;

	SET done := 0;

	OPEN rmcur_peruser;
	REPEAT
		FETCH
			rmcur_peruser
		INTO
			rmt_id,
			rmt_oqsum_ingress_mul, rmt_oqsum_egress_mul, rmt_oqsum_sec_mul,
			rmt_ow_ingress, rmt_ow_egress,
			rmt_pol_ingress, rmt_pol_egress,
			bp_s_month, bp_s_mday, bp_s_wday, bp_s_hour, bp_s_minute, bp_e_month, bp_e_mday, bp_e_wday, bp_e_hour, bp_e_minute;
		IF rmt_id > 0 THEN
			SET is_ok := 'Y';

			IF (bp_s_minute IS NOT NULL) AND (bp_e_minute IS NOT NULL) AND (bp_s_minute <= bp_e_minute) THEN
				IF NOT (MINUTE(ts) BETWEEN bp_s_minute AND bp_e_minute) THEN
					SET is_ok := 'N';
				END IF;
			END IF;
			IF (bp_s_hour IS NOT NULL) AND (bp_e_hour IS NOT NULL) AND (bp_s_hour <= bp_e_hour) THEN
				IF NOT (HOUR(ts) BETWEEN bp_s_hour AND bp_e_hour) THEN
					SET is_ok := 'N';
				END IF;
			END IF;
			IF (bp_s_wday IS NOT NULL) AND (bp_e_wday IS NOT NULL) AND (bp_s_wday <= bp_e_wday) THEN
				IF NOT ((WEEKDAY(ts) + 1) BETWEEN bp_s_wday AND bp_e_wday) THEN
					SET is_ok := 'N';
				END IF;
			END IF;
			IF (bp_s_mday IS NOT NULL) AND (bp_e_mday IS NOT NULL) AND (bp_s_mday <= bp_e_mday) THEN
				IF NOT (DAYOFMONTH(ts) BETWEEN bp_s_mday AND bp_e_mday) THEN
					SET is_ok := 'N';
				END IF;
			END IF;
			IF (bp_s_month IS NOT NULL) AND (bp_e_month IS NOT NULL) AND (bp_s_month <= bp_e_month) THEN
				IF NOT (MONTH(ts) BETWEEN bp_s_month AND bp_e_month) THEN
					SET is_ok := 'N';
				END IF;
			END IF;

			IF is_ok = 'Y' THEN
				IF rmt_oqsum_ingress_mul IS NOT NULL THEN
					SET oqsum_in := oqsum_in * rmt_oqsum_ingress_mul;
				END IF;
				IF rmt_oqsum_egress_mul IS NOT NULL THEN
					SET oqsum_eg := oqsum_eg * rmt_oqsum_egress_mul;
				END IF;
				IF rmt_oqsum_sec_mul IS NOT NULL THEN
					SET oqsum_sec := oqsum_sec * rmt_oqsum_sec_mul;
				END IF;
				IF rmt_pol_ingress IS NOT NULL THEN
					IF rmt_ow_ingress = 'Y' THEN
						SET pol_in := rmt_pol_ingress;
					ELSE
						SET pol_in := CONCAT_WS(' ', pol_in, rmt_pol_ingress);
					END IF;
				END IF;
				IF rmt_pol_egress IS NOT NULL THEN
					IF rmt_ow_egress = 'Y' THEN
						SET pol_eg := rmt_pol_egress;
					ELSE
						SET pol_eg := CONCAT_WS(' ', pol_eg, rmt_pol_egress);
					END IF;
				END IF;
			END IF;
		END IF;
	UNTIL done END REPEAT;
	CLOSE rmcur_peruser;
</%block>
