## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on tv_subscriptions_def (after delete)
## Copyright © 2017 Alex Unigovsky
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
	IF OLD.epid IS NOT NULL THEN
		DELETE FROM `paid_def` WHERE `epid` = OLD.epid;
	END IF;

	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 23, 3, CONCAT_WS(" ",
		"Deleted TV subscription",
		CONCAT("[ID ", OLD.tvsubid, "]")
	));
</%block>
