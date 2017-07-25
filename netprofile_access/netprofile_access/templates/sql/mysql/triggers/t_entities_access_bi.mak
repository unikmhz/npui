## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on entities_access (before insert)
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
	DECLARE xowned ENUM('Y', 'N') DEFAULT 'N';

	SET NEW.ut_ingress := 0;
	SET NEW.ut_egress := 0;
	SET NEW.qpend := NULL;

	IF NEW.ipaddrid IS NOT NULL THEN
		SELECT `owned` INTO xowned
		FROM `ipaddr_def`
		WHERE `ipaddrid` = NEW.ipaddrid;

		IF xowned = 'Y' THEN
			SET NEW.ipaddrid := NULL;
		ELSE
			UPDATE `ipaddr_def`
			SET `owned` = 'Y'
			WHERE `ipaddrid` = NEW.ipaddrid;
		END IF;
	END IF;

	IF NEW.ip6addrid IS NOT NULL THEN
		SELECT `owned` INTO xowned
		FROM `ip6addr_def`
		WHERE `ip6addrid` = NEW.ip6addrid;

		IF xowned = 'Y' THEN
			SET NEW.ip6addrid := NULL;
		ELSE
			UPDATE `ip6addr_def`
			SET `owned` = 'Y'
			WHERE `ip6addrid` = NEW.ip6addrid;
		END IF;
	END IF;
</%block>
