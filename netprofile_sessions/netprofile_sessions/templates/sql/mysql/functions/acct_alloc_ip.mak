## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: acct_alloc_ip
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
	DECLARE ipid, pid, entid, rid, xnasid INT UNSIGNED DEFAULT 0;
	DECLARE sid BIGINT UNSIGNED DEFAULT 0;
	DECLARE EXIT HANDLER FOR NOT FOUND BEGIN
		SELECT 0 AS `ipstr`, 0 AS `nasid`;
		ROLLBACK;
	END;

	START TRANSACTION;

	SELECT `entityid`
	INTO entid
	FROM `entities_def`
	WHERE `nick` = ename AND `etypeid` = 5;

	SELECT `ipaddrid`, `rateid`
	INTO ipid, rid
	FROM `entities_access`
	WHERE `entityid` = entid;

	SELECT `nasid`
	INTO xnasid
	FROM `nas_def`
	WHERE `idstr` LIKE nid;

	IF ipid IS NULL THEN
		SELECT `poolid`
		INTO pid
		FROM `rates_def`
		WHERE `rateid` = rid;

		IF pid IS NULL THEN
			SELECT `poolid`
			INTO pid
			FROM `nas_pools`
			WHERE `nasid` = xnasid
			ORDER BY RAND()
			LIMIT 1;
		ELSE
			SELECT `poolid`
			INTO pid
			FROM `nas_pools`
			WHERE `nasid` = xnasid
			AND `poolid` = pid
			LIMIT 1;
		END IF;

		SELECT `ipaddrid`
		INTO ipid
		FROM `ipaddr_def`
		WHERE `inuse` = 'N' AND `poolid` = pid
		LIMIT 1
		FOR UPDATE;
	ELSE
		BEGIN
			DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

			SELECT `sessid`
			INTO sid
			FROM `sessions_def`
			WHERE `ipaddrid` = ipid;

			IF sid > 0 THEN
				DELETE FROM `sessions_def`
				WHERE `sessid` = sid;
			END IF;
		END;

		SELECT `ipaddrid`
		INTO ipid
		FROM `ipaddr_def`
		WHERE `ipaddrid` = ipid
		FOR UPDATE;
	END IF;

	UPDATE `ipaddr_def` SET
		`inuse` = 'Y'
	WHERE `ipaddrid` = ipid;

	SELECT ipid AS `ipstr`, xnasid AS `nasid`;
	COMMIT;
</%block>

