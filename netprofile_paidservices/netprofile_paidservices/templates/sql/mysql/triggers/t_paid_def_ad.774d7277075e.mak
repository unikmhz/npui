## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on paid_def (after delete)
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
	DECLARE xcnt INT UNSIGNED DEFAULT 0;

	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 14, 3, CONCAT_WS(" ",
		"Deleted paid service",
		CONCAT("[ID ", OLD.epid, "]")
	));

	IF (OLD.aeid IS NOT NULL) THEN
		SELECT `qp_type`
		INTO pt_qpt
		FROM `paid_types`
		WHERE `paidid` = OLD.paidid;
		IF (pt_qpt = 'L') THEN
			SELECT COUNT(*)
			INTO xcnt
			FROM `paid_def` `pd`
			LEFT JOIN `paid_types` `pt`
			USING (`paidid`)
			WHERE `pd`.`aeid` = OLD.aeid
			AND `pd`.`active` = 'Y'
			AND `pt`.`qp_type` = 'L';
			IF (xcnt = 0) THEN
				UPDATE `entities_access`
				SET `pcheck` = 'N'
				WHERE `entityid` = OLD.aeid;
			END IF;
		END IF;
	END IF;
</%block>
