## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on tv_subscriptions_def (before insert)
## Copyright © 2017 Alex Unigovsky
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
	DECLARE tvsubtype_paidid, ae_stashid INT UNSIGNED DEFAULT NULL;

	SELECT `paidid`
	INTO tvsubtype_paidid
	FROM `tv_subscriptions_types`
	WHERE `tvsubtid` = NEW.tvsubtid;

	IF tvsubtype_paidid IS NOT NULL THEN
		SELECT `stashid`
		INTO ae_stashid
		FROM `entities_access`
		WHERE `entityid` = NEW.aeid;

		INSERT INTO `paid_def` (`entityid`, `aeid`, `stashid`, `paidid`, `active`)
		VALUES (NEW.entityid, NEW.aeid, ae_stashid, tvsubtype_paidid, 'Y');

		SET NEW.epid := LAST_INSERT_ID();
	ELSE
		SET NEW.epid := NULL;
	END IF;
</%block>
