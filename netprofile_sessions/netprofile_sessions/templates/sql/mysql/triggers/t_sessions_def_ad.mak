## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on sessions_def (after delete)
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
	INSERT INTO `sessions_history` (`name`, `stationid`, `entityid`, `ipaddrid`, `ip6addrid`, `destid`, `nasid`, `csid`, `called`, `startts`, `endts`, `ut_ingress`, `ut_egress`, `pol_ingress`, `pol_egress`)
	VALUES (OLD.name, OLD.stationid, OLD.entityid, OLD.ipaddrid, OLD.ip6addrid, OLD.destid, OLD.nasid, OLD.csid, OLD.called, OLD.startts, OLD.updatets, OLD.ut_ingress, OLD.ut_egress, OLD.pol_ingress, OLD.pol_egress);
</%block>
