## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: host_create_alias
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
	INSERT INTO `hosts_def` (`hgid`, `entityid`, `domainid`, `name`, `aliasid`, `ctime`, `cby`, `mby`)
	SELECT `hgid`, `entityid`, did, aname, hid, NOW(), @accessuid, @accessuid
	FROM `hosts_def`
	WHERE `hostid` = hid;
</%block>
