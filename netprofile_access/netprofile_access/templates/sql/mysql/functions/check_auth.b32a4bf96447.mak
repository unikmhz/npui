## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: check_auth
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
	DECLARE entid INT UNSIGNED DEFAULT 0;
	DECLARE ealiasid INT UNSIGNED DEFAULT NULL;
	DECLARE EXIT HANDLER FOR NOT FOUND RETURN FALSE;
	SELECT `entityid`, `aliasid`
	INTO entid, ealiasid
	FROM `entities_access`
	LEFT JOIN `entities_def`
	USING(`entityid`)
	WHERE `nick` = name AND `pwd_plain` = pass AND `state` = 0;
	IF ealiasid IS NOT NULL THEN
		REPEAT
			SELECT `entityid`, `aliasid`
			INTO entid, ealiasid
			FROM `entities_access`
			LEFT JOIN `entities_def`
			USING(`entityid`)
			WHERE `entityid` = ealiasid;
		UNTIL ealiasid IS NULL END REPEAT;
	END IF;
	RETURN TRUE;
</%block>
