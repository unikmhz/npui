## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: ps_callback
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
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	SET @pass_xepid := xepid;
	SET @pass_ts := ts;
	SET @pass_aeid := ps_aeid;
	SET @pass_hostid := ps_hostid;
	SET @pass_paidid := ps_paidid;
	SET @pass_entityid := ps_entityid;
	SET @pass_stashid := ps_stashid;
	SET @pass_qpend := ps_qpend;
	SET @pass_pay := pay;
	SET @cb_query := CONCAT('CALL ', cbname, '(?, ?, ?, ?, ?, @pass_entityid, @pass_stashid, @pass_qpend, @pass_pay)');
	PREPARE cbx FROM @cb_query;
	EXECUTE cbx USING @pass_xepid, @pass_ts, @pass_aeid, @pass_hostid, @pass_paidid;
	DEALLOCATE PREPARE cbx;
	SET ps_entityid := @pass_entityid;
	SET ps_stashid := @pass_stashid;
	SET ps_qpend := @pass_qpend;
	SET pay := @pass_pay;
</%block>

