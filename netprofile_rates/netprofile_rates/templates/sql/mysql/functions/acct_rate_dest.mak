## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: acct_rate_dest
## Copyright © 2014-2017 Alex Unigovsky
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
	DECLARE dest_id, done INT UNSIGNED DEFAULT 0;
	DECLARE dest_type enum('normal','noquota','onlyquota','reject') CHARACTER SET ascii DEFAULT 'normal';
	DECLARE dest_mt enum('exact','prefix','suffix','regex') CHARACTER SET ascii DEFAULT 'prefix';
	DECLARE dest_match, dest_cb_acct varchar(255) CHARACTER SET ascii DEFAULT NULL;
	DECLARE dest_oqsum_sec, dest_oqmul_sec DECIMAL(20,8) DEFAULT NULL;
	DECLARE dcur CURSOR FOR
		SELECT `destid`, `type`, `mt`, `match`, `oqsum_sec`, `oqmul_sec`, `cb_acct`
		FROM `dest_def`
		WHERE `dsid` = dsid
		AND `active` = 'Y'
		ORDER BY `l_ord` ASC;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;

	IF destid IS NOT NULL THEN
		SELECT `type`, `mt`, `match`, `oqsum_sec`, `oqmul_sec`, `cb_acct`
		INTO dest_type, dest_mt, dest_match, dest_oqsum_sec, dest_oqmul_sec, dest_cb_acct
		FROM `dest_def`
		WHERE `destid` = destid
		AND `active` = 'Y';
		IF (done = 1) OR (dest_id = 0) THEN
			LEAVE ardfunc;
		END IF;
		CASE dest_mt
			WHEN 'exact' THEN
				IF called = dest_match THEN
					SET done := 2;
				END IF;
			WHEN 'prefix' THEN
				IF LEFT(called, CHAR_LENGTH(dest_match)) = dest_match THEN
					SET done := 2;
				END IF;
			WHEN 'suffix' THEN
				IF RIGHT(called, CHAR_LENGTH(dest_match)) = dest_match THEN
					SET done := 2;
				END IF;
			WHEN 'regex' THEN
				IF called REGEXP dest_match THEN
					SET done := 2;
				END IF;
		END CASE;
	ELSE
		OPEN dcur;
		REPEAT
			FETCH dcur INTO dest_id, dest_type, dest_mt, dest_match, dest_oqsum_sec, dest_oqmul_sec, dest_cb_acct;
			IF dest_id > 0 THEN
				CASE dest_mt
					WHEN 'exact' THEN
						IF called = dest_match THEN
							SET done := 2;
						END IF;
					WHEN 'prefix' THEN
						IF LEFT(called, CHAR_LENGTH(dest_match)) = dest_match THEN
							SET done := 2;
						END IF;
					WHEN 'suffix' THEN
						IF RIGHT(called, CHAR_LENGTH(dest_match)) = dest_match THEN
							SET done := 2;
						END IF;
					WHEN 'regex' THEN
						IF called REGEXP dest_match THEN
							SET done := 2;
						END IF;
				END CASE;
			END IF;
		UNTIL done END REPEAT;
		CLOSE dcur;
		SET destid := dest_id;
	END IF;
	IF done = 2 THEN
		SET dtype := dest_type;
		IF dest_oqsum_sec IS NOT NULL THEN
			SET oqsum_sec := dest_oqsum_sec;
		ELSEIF dest_oqmul_sec IS NOT NULL THEN
			SET oqsum_sec := oqsum_sec * dest_oqmul_sec;
		END IF;
	END IF;
</%block>
