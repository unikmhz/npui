## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: domain_get_full
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
	DECLARE domstr, tmp VARCHAR(255) DEFAULT '';
	DECLARE parent INT UNSIGNED DEFAULT NULL;
	SELECT `parentid`, `name` INTO parent, domstr
	FROM `domains_def`
	WHERE `domainid` = did;
	IF parent IS NULL THEN
		RETURN domstr;
	END IF;
	REPEAT
		SELECT `parentid`, `name` INTO parent, tmp
		FROM `domains_def`
		WHERE `domainid` = parent;
		SET domstr := CONCAT(domstr, '.', tmp);
	UNTIL parent IS NULL END REPEAT;
	RETURN domstr;
</%block>
