## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on paid_def (after insert)
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
	DECLARE pt_qpt ENUM('I', 'L', 'O') DEFAULT 'I';

	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 14, 1, CONCAT_WS(" ",
		"New paid service",
		CONCAT("[ID ", NEW.epid, "]"),
		CONCAT("[ENTITYID ", NEW.entityid, "]"),
		CONCAT("[STASHID ", NEW.stashid, "]"),
		CONCAT("[PAIDID ", NEW.paidid, "]")
	));

	IF (NEW.aeid IS NOT NULL) AND (NEW.active = 'Y') THEN
		SELECT `qp_type`
		INTO pt_qpt
		FROM `paid_types`
		WHERE `paidid` = NEW.paidid;
		IF (pt_qpt = 'L') THEN
			UPDATE `entities_access`
			SET `pcheck` = 'Y'
			WHERE `entityid` = NEW.aeid;
		END IF;
	END IF;
</%block>
