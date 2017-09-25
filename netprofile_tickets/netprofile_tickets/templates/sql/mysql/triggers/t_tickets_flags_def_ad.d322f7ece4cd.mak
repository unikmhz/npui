## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on tickets_flags_def (after delete)
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
	IF @tcid IS NULL THEN
		INSERT INTO `tickets_changes_def` (`ticketid`, `uid`, `ts`, `comments`)
		VALUES (@ticketid, IF(@accessuid > 0, @accessuid, NULL), NOW(), @comments);
		SET @tcid := LAST_INSERT_ID();
	END IF;
	INSERT INTO `tickets_changes_flagmod` (`tcid`, `tftid`, `newstate`)
	VALUES (@tcid, OLD.tftid, 'N');
</%block>
