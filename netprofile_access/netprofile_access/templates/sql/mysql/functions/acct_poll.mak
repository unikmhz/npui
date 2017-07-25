## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: acct_poll
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
	DECLARE done, aeid INT UNSIGNED DEFAULT 0;
	DECLARE nick VARCHAR(255) DEFAULT NULL;
	DECLARE cur CURSOR FOR
		SELECT `ea`.`entityid` `entityid`, `ed`.`nick` `nick`
		FROM `entities_access` `ea`
		LEFT JOIN `entities_def` `ed`
		USING(`entityid`)
		WHERE `ea`.`state` <> 2
		AND `ea`.`aliasid` IS NULL
		AND `ea`.`rateid` IN(SELECT `rateid` FROM `rates_def` WHERE `polled` = 'Y');
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;
	OPEN cur;
	REPEAT
		FETCH cur INTO aeid, nick;
		IF aeid > 0 THEN
			CALL acct_add(aeid, nick, 0, 0, ts);
		END IF;
	UNTIL done END REPEAT;
	CLOSE cur;
</%block>
