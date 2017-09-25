## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on entities_access (after update)
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
	DECLARE xuid INT(10) UNSIGNED DEFAULT NULL;

	IF @accessuid > 0 THEN
		SET xuid := @accessuid;
	END IF;
	IF (OLD.state <> NEW.state) OR (OLD.pwd_hashed <> NEW.pwd_hashed) OR (OLD.rateid <> NEW.rateid) THEN
		UPDATE `entities_def`
		SET `mby` = xuid, `mtime` = NOW()
		WHERE `entityid` IN (OLD.entityid, NEW.entityid);

		INSERT INTO `entities_access_changes` (`entityid`, `uid`, `ts`, `pwchanged`, `state_old`, `state_new`, `rateid_old`, `rateid_new`, `descr`)
		VALUES (NEW.entityid, xuid, NOW(), IF(OLD.pwd_hashed <> NEW.pwd_hashed, 'Y', 'N'), OLD.state, NEW.state, OLD.rateid, NEW.rateid, @comments);
	END IF;
</%block>
