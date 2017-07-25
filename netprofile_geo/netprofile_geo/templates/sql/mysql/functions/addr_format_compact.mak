## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: addr_format_compact
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
	RETURN CONCAT_WS(' ',
		IF(streetname IS NULL OR streetname = '',
			NULL,
			streetname
		),
		IF(num = 0,
			CONCAT(
				bld,
				IF(num_suffix IS NULL OR num_suffix = '', '', num_suffix),
				IF(num_slash IS NULL OR num_slash = 0, '', CONCAT('/', num_slash))
			),
			CONCAT(
				num,
				IF(num_suffix IS NULL OR num_suffix = '', '', num_suffix),
				IF(num_slash IS NULL OR num_slash = 0, '', CONCAT('/', num_slash))
			)
		),
		IF(bld IS NULL OR bld = 0,
			NULL,
			CONCAT('bld.', bld)
		),
		IF(fl IS NULL OR fl = 0,
			NULL,
			CONCAT('app.', fl)
		)
	);
</%block>
