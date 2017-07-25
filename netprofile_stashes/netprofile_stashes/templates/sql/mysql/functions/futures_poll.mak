## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: futures_poll
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
	DECLARE done, f_id, f_stashid INT UNSIGNED DEFAULT 0;
	DECLARE f_diff, xpsum DECIMAL(20,8) DEFAULT 0.0;
	DECLARE f_ctime, f_ptime DATETIME;
	DECLARE cur CURSOR FOR
		SELECT `futureid`, `stashid`, `diff`, `ctime`, `ptime`
		FROM `futures_def`
		WHERE `state` = 'A'
		AND `ptime` < NOW()
		FOR UPDATE;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;

	START TRANSACTION;

	OPEN cur;
	REPEAT
		SET f_id := 0;
		FETCH cur INTO f_id, f_stashid, f_diff, f_ctime, f_ptime;
		IF f_id > 0 THEN
			SET xpsum := 0.0;
			SELECT SUM(`diff`)
			INTO xpsum
			FROM `stashes_io_def`
			WHERE (`stashid` = f_stashid)
			AND (`ts` BETWEEN f_ctime AND f_ptime)
			AND `siotypeid` IN(SELECT `siotypeid` FROM `stashes_io_types` WHERE `pays_futures` = 'Y');
			IF xpsum >= f_diff THEN
				UPDATE `futures_def`
				SET `state` = 'P'
				WHERE `futureid` = f_id;
			ELSE
				UPDATE `futures_def`
				SET `state` = 'C'
				WHERE `futureid` = f_id;
				UPDATE `entities_access`
				SET `state` = 1
				WHERE `stashid` = f_stashid;
			END IF;
		END IF;
	UNTIL done END REPEAT;
	CLOSE cur;

	COMMIT;
</%block>
