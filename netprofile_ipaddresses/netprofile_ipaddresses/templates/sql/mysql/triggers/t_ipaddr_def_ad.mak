## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on ipaddr_def (after delete)
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
	DECLARE ipm INT UNSIGNED DEFAULT 0;
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

	SET cdate := CURDATE();

	SELECT `ipaddr` INTO ipm
	FROM `nets_def`
	WHERE `netid` = OLD.netid;
	SET ipm := (ipm + OLD.offset) & 0xFFFFFF00;

	SELECT `date`, `rev`
	INTO xdate, xrev
	FROM `revzone_serials`
	WHERE `ipaddr` = ipm
	AND `date` = cdate
	FOR UPDATE;

	IF xdate IS NULL THEN
		REPLACE INTO `revzone_serials` (`ipaddr`, `date`, `rev`)
		VALUES (ipm, cdate, 1);
	ELSE
		UPDATE `revzone_serials`
		SET `rev` = xrev + 1
		WHERE `ipaddr` = ipm;
	END IF;

	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 8, 3, CONCAT_WS(" ",
		"Deleted IP address",
		CONCAT("[ID ", OLD.ipaddrid, "]")
	));
</%block>
