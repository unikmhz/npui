## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: acct_rate_filter
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
	DECLARE f_id, done INT UNSIGNED DEFAULT 0;
	DECLARE f_porttype, f_servicetype, f_frproto, f_tuntype, f_tunmedium INT UNSIGNED DEFAULT NULL;
	DECLARE fcur CURSOR FOR
		SELECT `fid`, `porttype`, `servicetype`, `frproto`, `tuntype`, `tunmedium`
		FROM `filters_def`
		WHERE `fsid` = fsid;
	DECLARE CONTINUE HANDLER FOR SQLSTATE '02000'
		SET done := 1;

	SET filterid := NULL;
	OPEN fcur;
	REPEAT
		FETCH fcur INTO f_id, f_porttype, f_servicetype, f_frproto, f_tuntype, f_tunmedium;
		IF f_id > 0 THEN
			IF (f_porttype IS NOT NULL) AND (r_porttype IS NOT NULL) AND (f_porttype <> r_porttype) THEN
				SET f_id := NULL;
			ELSEIF (f_servicetype IS NOT NULL) AND (r_servicetype IS NOT NULL) AND (f_servicetype <> r_servicetype) THEN
				SET f_id := NULL;
			ELSEIF (f_frproto IS NOT NULL) AND (r_frproto IS NOT NULL) AND (f_frproto <> r_frproto) THEN
				SET f_id := NULL;
			ELSEIF (f_tuntype IS NOT NULL) AND (r_tuntype IS NOT NULL) AND (f_tuntype <> r_tuntype) THEN
				SET f_id := NULL;
			ELSEIF (f_tunmedium IS NOT NULL) AND (r_tunmedium IS NOT NULL) AND (f_tunmedium <> r_tunmedium) THEN
				SET f_id := NULL;
			END IF;
		END IF;
		IF (f_id IS NOT NULL) AND (f_id > 0) THEN
			SET filterid := f_id;
			SET done := 2;
		END IF;
	UNTIL done END REPEAT;
	CLOSE fcur;
</%block>
