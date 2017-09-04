## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: acct_pcheck
## Copyright © 2016-2017 Alex Unigovsky
##
## This file is part of NetProfile.
## NetProfile is free software: you can redistribute it and/or
## modify it under the terms of the GNU Affero General Public
## License as published by the Free Software Foundation, either
## version 3 of the License, or (at your option) any later
## version.
##
## NetProfile is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General
## Public License along with NetProfile. If not, see
## <http://www.gnu.org/licenses/>.
##
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE done, ps_epid, ps_entityid, ps_hostid, ps_paidid INT UNSIGNED DEFAULT 0;
	DECLARE ps_qpend DATETIME DEFAULT NULL;
	DECLARE pt_name, pt_cb_before, pt_cb_success, pt_cb_failure VARCHAR(255) DEFAULT NULL;
	DECLARE pt_isum, pt_qsum DECIMAL(20,8) DEFAULT 0.0;
	DECLARE pt_spa, pt_qpa SMALLINT(5) UNSIGNED DEFAULT 1;
	DECLARE pt_qpu ENUM('a_hour', 'a_day', 'a_week', 'a_month', 'a_year', 'c_hour', 'c_day', 'c_month', 'c_year', 'f_hour', 'f_day', 'f_week', 'f_month', 'f_year') CHARACTER SET ascii DEFAULT 'c_month';
	DECLARE pcur CURSOR FOR
		SELECT
			`pd`.`epid`, `pd`.`entityid`, `pd`.`hostid`,
			`pd`.`paidid`, `pd`.`qpend`, `pt`.`name`,
			`pt`.`isum`, `pt`.`qsum`, `pt`.`sp_amount`,
			`pt`.`qp_amount`, `pt`.`qp_unit`, `pt`.`cb_before`,
			`pt`.`cb_success`, `pt`.`cb_failure`
		FROM `paid_def` `pd`
		LEFT JOIN `paid_types` `pt`
		USING(`paidid`)
		WHERE `pd`.`aeid` = aeid
		AND `pd`.`active` = 'Y'
		AND `pt`.`qp_type` = 'L'
		ORDER BY `pt`.`qp_order` ASC;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;

	SELECT SUM(`pt`.`qsum`)
	INTO pt_qsum
	FROM `paid_def` `pd`
	LEFT JOIN `paid_types` `pt`
	USING(`paidid`)
	WHERE `pd`.`aeid` = aeid
	AND `pd`.`active` = 'Y'
	AND `pt`.`qp_type` = 'L';
	IF done = 1 THEN
		LEAVE aapfunc;
	END IF;
	SET pt_qsum := pt_qsum / xrate;

	OPEN pcur;
	IF ((stash_amount + stash_credit) < (pt_qsum + pay)) AND (isok = 'N') THEN
		REPEAT
			FETCH pcur INTO
				ps_epid, ps_entityid, ps_hostid,
				ps_paidid, ps_qpend, pt_name,
				pt_isum, pt_qsum, pt_spa,
				pt_qpa, pt_qpu, pt_cb_before,
				pt_cb_success, pt_cb_failure;
			IF ps_epid > 0 THEN
				SET pt_isum := pt_isum / xrate;
				SET pt_qsum := pt_qsum / xrate;
				IF pt_cb_before IS NOT NULL THEN
					CALL ps_callback(pt_cb_before, ps_epid, ts, aeid, ps_hostid, ps_paidid, ps_entityid, user_stashid, user_qpend, pt_qsum);
				END IF;
				IF pt_cb_failure IS NOT NULL THEN
					CALL ps_callback(pt_cb_failure, ps_epid, ts, aeid, ps_hostid, ps_paidid, ps_entityid, user_stashid, user_qpend, pt_qsum);
				END IF;
			END IF;
		UNTIL done END REPEAT;
	ELSE
		REPEAT
			FETCH pcur INTO
				ps_epid, ps_entityid, ps_hostid,
				ps_paidid, ps_qpend, pt_name,
				pt_isum, pt_qsum, pt_spa,
				pt_qpa, pt_qpu, pt_cb_before,
				pt_cb_success, pt_cb_failure;
			IF ps_epid > 0 THEN
				SET pt_isum := pt_isum / xrate;
				SET pt_qsum := pt_qsum / xrate;
				IF pt_cb_before IS NOT NULL THEN
					CALL ps_callback(pt_cb_before, ps_epid, ts, aeid, ps_hostid, ps_paidid, ps_entityid, user_stashid, user_qpend, pt_qsum);
				END IF;
				INSERT INTO `stashes_io_def` (`siotypeid`, `stashid`, `currid`, `entityid`, `ts`, `diff`, `descr`)
				VALUES (
					(SELECT `siotypeid` FROM `stashes_io_types` WHERE `ftype` = 'ps_qsum'),
					user_stashid, xcurrid, aeid, ts, -pt_qsum, pt_name
				);
				SET stash_amount := stash_amount - pt_qsum;
				IF pt_cb_success IS NOT NULL THEN
					CALL ps_callback(pt_cb_success, ps_epid, ts, aeid, ps_hostid, ps_paidid, ps_entityid, user_stashid, user_qpend, pt_qsum);
				END IF;
			END IF;
		UNTIL done END REPEAT;
		SET isok := 'Y';
	END IF;
	CLOSE pcur;
</%block>

