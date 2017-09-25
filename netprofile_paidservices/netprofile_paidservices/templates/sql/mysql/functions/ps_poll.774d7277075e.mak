## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: ps_poll
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
	DECLARE done, psid INT UNSIGNED DEFAULT 0;
	DECLARE cur CURSOR FOR
		SELECT `pd`.`epid`
		FROM `paid_def` `pd`
		LEFT JOIN `paid_types` `pt`
		USING (`paidid`)
		WHERE ((`pd`.`qpend` < ts) OR (`pd`.`qpend` IS NULL))
		AND `pd`.`active` = 'Y'
		AND `pt`.`qp_type` = 'I';
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;
	OPEN cur;
	REPEAT
		FETCH cur INTO psid;
		IF psid > 0 THEN
			CALL ps_execute(psid, ts);
		END IF;
	UNTIL done END REPEAT;
	CLOSE cur;
</%block>

