## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: addr_get_full
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
	DECLARE fulladdr VARCHAR(255) DEFAULT NULL;
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;
	SELECT addr_format(
		`s`.`name`,
		`s`.`prefix`,
		`s`.`suffix`,
		`h`.`number`,
		`h`.`num_slash`,
		`h`.`num_suffix`,
		`h`.`building`,
		NULL
	) INTO fulladdr
	FROM `addr_houses` AS `h`
	LEFT JOIN `addr_streets` AS `s`
	USING(`streetid`)
	WHERE `h`.`houseid` = hid;
	RETURN fulladdr;
</%block>
