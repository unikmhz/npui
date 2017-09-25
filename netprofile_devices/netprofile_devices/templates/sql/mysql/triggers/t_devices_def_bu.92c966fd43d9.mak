## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on devices_def (before update)
## Copyright © 2015-2017 Alex Unigovsky
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
	SET NEW.mby := IF(@accessuid > 0, @accessuid, NULL);
	IF OLD.placeid <> NEW.placeid THEN
		SET NEW.itime := NOW();
		SET NEW.iby := NEW.mby;
	END IF;
</%block>
