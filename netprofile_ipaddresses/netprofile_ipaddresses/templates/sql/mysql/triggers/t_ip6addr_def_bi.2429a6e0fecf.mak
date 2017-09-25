## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on ip6addr_def (before insert)
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
	DECLARE hg INT UNSIGNED DEFAULT 0;

	IF NEW.offset = 0 THEN
		SELECT `hgid`
		INTO hg
		FROM `hosts_def`
		WHERE `hostid` = NEW.hostid;
		SET NEW.offset := ip6addr_get_offset_hg(NEW.netid, hg);
	END IF;
</%block>
