## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on accessblock_def (before insert)
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
	DECLARE curts DATETIME DEFAULT NULL;
	DECLARE ost TINYINT DEFAULT -1;
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

	IF (NEW.startts > NEW.endts) THEN
		SET curts := NEW.startts;
		SET NEW.startts := NEW.endts;
		SET NEW.endts := curts;
	END IF;
	SET curts := NOW();
	IF (curts >= NEW.startts) THEN
		IF (curts <= NEW.endts) THEN
			SET NEW.bstate := 'active';
		ELSE
			SET NEW.bstate := 'expired';
		END IF;
	ELSE
		SET NEW.bstate := 'planned';
	END IF;

	IF (NEW.entityid > 0) THEN
		SELECT `state`
		INTO ost
		FROM `entities_access`
		WHERE `entityid` = NEW.entityid;
		IF (ost >= 0) THEN
			SET NEW.oldstate := ost;
		END IF;
	END IF;
</%block>
