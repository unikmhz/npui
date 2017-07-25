## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on ip6addr_def (after insert)
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
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE xdate, cdate DATE DEFAULT NULL;
	DECLARE xrev TINYINT UNSIGNED DEFAULT 0;
	DECLARE ipm BINARY(16) DEFAULT NULL;
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

	SET cdate := CURDATE();

	SELECT `ip6addr` INTO ipm
	FROM `nets_def`
	WHERE `netid` = NEW.netid;

	SET ipm := UNHEX(RPAD(SUBSTRING(HEX(ipm) FROM 1 FOR 16), 32, '0'));

	SELECT `date`, `rev`
	INTO xdate, xrev
	FROM `revzone_serials6`
	WHERE `ip6addr` = ipm
	AND `date` = cdate;

	IF xdate IS NULL THEN
		REPLACE INTO `revzone_serials6` (`ip6addr`, `date`, `rev`)
		VALUES (ipm, cdate, 1);
	ELSE
		UPDATE `revzone_serials6`
		SET `rev` = xrev + 1
		WHERE `ip6addr` = ipm;
	END IF;

	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 19, 1, CONCAT_WS(" ",
		"New IPv6 address",
		CONCAT("[ID ", NEW.ip6addrid, "]"),
		CONCAT("[HOSTID ", NEW.hostid, "]"),
		CONCAT("[NETID ", NEW.netid, "]"),
		CONCAT("[OFFSET ", NEW.offset, "]")
	));
</%block>
