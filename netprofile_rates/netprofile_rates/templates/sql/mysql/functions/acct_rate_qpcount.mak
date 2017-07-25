## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: acct_rate_qpcount
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
	DECLARE n INT UNSIGNED DEFAULT 0;

	CASE qpu
		WHEN 'a_hour' THEN SET n := FLOOR((UNIX_TIMESTAMP(dto) - UNIX_TIMESTAMP(dfrom)) / (3600 * qpa));
		WHEN 'a_day' THEN SET n := FLOOR((UNIX_TIMESTAMP(dto) - UNIX_TIMESTAMP(dfrom)) / (86400 * qpa));
		WHEN 'a_week' THEN SET n := FLOOR((UNIX_TIMESTAMP(dto) - UNIX_TIMESTAMP(dfrom)) / (604800 * qpa));
		WHEN 'a_month' THEN SET n := FLOOR((UNIX_TIMESTAMP(dto) - UNIX_TIMESTAMP(dfrom)) / (2592000 * qpa));
		WHEN 'c_hour' THEN SET n := FLOOR(TIMESTAMPDIFF(HOUR, dfrom, dto) / qpa);
		WHEN 'c_day' THEN SET n := FLOOR(DATEDIFF(dto, dfrom) / qpa);
		WHEN 'c_month' THEN SET n := FLOOR(TIMESTAMPDIFF(MONTH, dfrom, dto) / qpa);
	END CASE;
	RETURN n;
</%block>
