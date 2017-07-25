## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on tickets_def (after update)
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
	INSERT INTO `tickets_changes_def` (`ticketid`, `ttrid`, `uid`, `ts`, `show_client`, `comments`)
	VALUES (NEW.ticketid, @ttrid, IF(@accessuid > 0, @accessuid, NULL), NOW(), IF(@show_client = 'Y', 'Y', 'N'), @comments);
	SET @tcid := LAST_INSERT_ID();
	IF OLD.entityid <> NEW.entityid THEN
		INSERT INTO `tickets_changes_bits` (`tcid`, `tcfid`, `old`, `new`)
		VALUES (@tcid, 5, OLD.entityid, NEW.entityid);
	END IF;
	IF (OLD.assigned_uid <> NEW.assigned_uid) OR (NOT OLD.assigned_uid <=> NEW.assigned_uid) THEN
		INSERT INTO `tickets_changes_bits` (`tcid`, `tcfid`, `old`, `new`)
		VALUES (@tcid, 1, OLD.assigned_uid, NEW.assigned_uid);
	END IF;
	IF (OLD.assigned_gid <> NEW.assigned_gid) OR (NOT OLD.assigned_gid <=> NEW.assigned_gid) THEN
		INSERT INTO `tickets_changes_bits` (`tcid`, `tcfid`, `old`, `new`)
		VALUES (@tcid, 2, OLD.assigned_gid, NEW.assigned_gid);
	END IF;
	IF (OLD.assigned_time <> NEW.assigned_time) OR (NOT OLD.assigned_time <=> NEW.assigned_time) THEN
		INSERT INTO `tickets_changes_bits` (`tcid`, `tcfid`, `old`, `new`)
		VALUES (@tcid, 3, OLD.assigned_time, NEW.assigned_time);
	END IF;
	IF OLD.archived <> NEW.archived THEN
		INSERT INTO `tickets_changes_bits` (`tcid`, `tcfid`, `old`, `new`)
		VALUES (@tcid, 4, OLD.archived, NEW.archived);
	END IF;
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 3, 2, CONCAT_WS(" ",
		"Modified ticket",
		CONCAT("[ID ", NEW.ticketid, "]"),
		CONCAT("[TCID ", @tcid, "]")
	));
</%block>
