## -*- coding: utf-8 -*-
##
## NetProfile: SQL function: acct_authz_session
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
	DECLARE nf BOOLEAN DEFAULT FALSE;
	DECLARE entid, user_rateid, user_nextrateid, sessnum, poolid INT UNSIGNED DEFAULT 0;
	DECLARE ealiasid, rate_fsid, filterid INT UNSIGNED DEFAULT NULL;
	DECLARE userpass_crypt, userpass_plain, userpol_in, userpol_eg VARCHAR(255) DEFAULT NULL;
	DECLARE userpass_ntlm CHAR(32) CHARACTER SET ascii DEFAULT NULL;
	DECLARE user_state TINYINT UNSIGNED DEFAULT 0;
	DECLARE ts, user_qpend DATETIME DEFAULT NULL;
	DECLARE user_sim SMALLINT(6) DEFAULT 0;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET nf := TRUE;

	IF r_porttype = -1 THEN
		SET r_porttype := NULL;
	END IF;
	IF r_servicetype = -1 THEN
		SET r_servicetype := NULL;
	END IF;
	IF r_frproto = -1 THEN
		SET r_frproto := NULL;
	END IF;
	IF r_tuntype = -1 THEN
		SET r_tuntype := NULL;
	END IF;
	IF r_tunmedium = -1 THEN
		SET r_tunmedium := NULL;
	END IF;

	SELECT `entityid`, `aliasid`, `pwd_ntlm`, `pwd_crypt`, `pwd_plain`, `rateid`, `nextrateid`, `state`, `qpend`
	INTO entid, ealiasid, userpass_ntlm, userpass_crypt, userpass_plain, user_rateid, user_nextrateid, user_state, user_qpend
	FROM `entities_access`
	LEFT JOIN `entities_def`
	USING(`entityid`)
	WHERE `nick` = name;
	IF nf = TRUE THEN
		SELECT
			NULL AS `entityid`,
			NULL AS `username`,
			NULL AS `pwd_ntlm`,
			NULL AS `pwd_crypt`,
			NULL AS `pwd_plain`,
			NULL AS `policy_in`,
			NULL AS `policy_eg`,
			99 AS `state`;
		LEAVE authzfunc;
	END IF;
	IF ealiasid IS NOT NULL THEN
		REPEAT
			SELECT `entityid`, `aliasid`, `rateid`, `nextrateid`, `qpend`
			INTO entid, ealiasid, user_rateid, user_nextrateid, user_qpend
			FROM `entities_access`
			WHERE `entityid` = ealiasid
			AND `state` = 0;
		UNTIL (ealiasid IS NULL) OR (nf = TRUE) END REPEAT;
		IF nf = TRUE THEN
			SELECT
				NULL AS `entityid`,
				NULL AS `username`,
				NULL AS `pwd_ntlm`,
				NULL AS `pwd_crypt`,
				NULL AS `pwd_plain`,
				NULL AS `policy_in`,
				NULL AS `policy_eg`,
				99 AS `state`;
			LEAVE authzfunc;
		END IF;
	END IF;
	IF (user_nextrateid IS NOT NULL) AND (user_nextrateid <> user_rateid) THEN
		SET ts := NOW();
		IF (user_qpend IS NULL) OR (user_qpend < ts) THEN
			SET user_rateid := user_nextrateid;
		END IF;
	END IF;
	SELECT `fsid`, `sim`, `pol_ingress`, `pol_egress`
	INTO rate_fsid, user_sim, userpol_in, userpol_eg
	FROM `rates_def`
	WHERE `rateid` = user_rateid;
	IF user_sim > 0 THEN
		SELECT COUNT(*)
		INTO sessnum
		FROM `sessions_def`
		WHERE `entityid` = entid;
		IF sessnum >= user_sim THEN
			SELECT
				NULL AS `entityid`,
				NULL AS `username`,
				NULL AS `pwd_ntlm`,
				NULL AS `pwd_crypt`,
				NULL AS `pwd_plain`,
				NULL AS `policy_in`,
				NULL AS `policy_eg`,
				3 AS `state`;
			LEAVE authzfunc;
		END IF;
	END IF;
	IF rate_fsid IS NOT NULL THEN
		CALL acct_rate_filter(rate_fsid, r_porttype, r_servicetype, r_frproto, r_tuntype, r_tunmedium, filterid);
		IF filterid IS NULL THEN
			SELECT
				NULL AS `entityid`,
				NULL AS `username`,
				NULL AS `pwd_ntlm`,
				NULL AS `pwd_crypt`,
				NULL AS `pwd_plain`,
				NULL AS `policy_in`,
				NULL AS `policy_eg`,
				4 AS `state`;
			LEAVE authzfunc;
		END IF;
	END IF;
	SELECT
		entid AS `entityid`,
		name AS `username`,
		userpass_ntlm AS `pwd_ntlm`,
		userpass_crypt AS `pwd_crypt`,
		userpass_plain AS `pwd_plain`,
		userpol_in AS `policy_in`,
		userpol_eg AS `policy_eg`,
		user_state AS `state`;
</%block>

