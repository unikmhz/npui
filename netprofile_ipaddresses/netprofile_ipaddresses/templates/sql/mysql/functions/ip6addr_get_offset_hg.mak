## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: ip6addr_get_offset_hg
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
	DECLARE fo DECIMAL(39,0) UNSIGNED DEFAULT 1;
	DECLARE tmp, offmin, offmax, dynstart, dynend DECIMAL(39,0) UNSIGNED DEFAULT 0;
	DECLARE done, found INT UNSIGNED DEFAULT 0;
	DECLARE cur CURSOR FOR
		SELECT `offset`
		FROM `ip6addr_def`
		WHERE `netid` = net
		ORDER BY `offset` ASC;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;

	SELECT POW(2, 128 - `cidr6`) - 1, `gueststart6`, `guestend6`
	INTO offmax, dynstart, dynend
	FROM `nets_def`
	WHERE `netid` = net;
	SELECT `startoffset6`, IF(`endoffset6` > offmax, 0, offmax - `endoffset6`) INTO offmin, offmax
	FROM `hosts_groups`
	WHERE `hgid` = hg;
	IF done = 1 OR offmax = 0 OR offmin > offmax THEN
		RETURN NULL;
	END IF;
	SET fo := offmin + 1;
	OPEN cur;
	cfx: REPEAT
		IF fo >= offmax THEN
			LEAVE cfx;
		END IF;
		FETCH cur INTO tmp;
		IF tmp <= offmin THEN
			SET fo := offmin;
		ELSEIF tmp <> fo THEN
			IF dynstart > 0 AND dynend > 0 AND fo BETWEEN dynstart AND dynend THEN
				SET fo := tmp;
			ELSE
				SET found := 1;
				LEAVE cfx;
			END IF;
		END IF;
		SET fo := fo + 1;
	UNTIL done END REPEAT;
	CLOSE cur;
	IF found = 0 THEN
		IF fo = offmin + 1 THEN
			RETURN fo;
		ELSE
			RETURN NULL;
		END IF;
	END IF;
	RETURN fo;
</%block>
