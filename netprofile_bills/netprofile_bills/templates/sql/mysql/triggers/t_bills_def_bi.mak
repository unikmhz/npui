## -*- coding: utf-8 -*-
##
## NetProfile: SQL trigger on bills_def (before insert)
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
	DECLARE sio INT UNSIGNED DEFAULT 0;
	DECLARE x_bsid, cser, uid, stash_currid INT UNSIGNED DEFAULT NULL;
	DECLARE bill_sum DECIMAL(20,8) DEFAULT 0.0;
	DECLARE xrate_from, xrate_to DECIMAL(20,8) DEFAULT 1.0;
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;

	IF @accessuid > 0 THEN
		SET uid := @accessuid;
	END IF;
	SET NEW.ctime := NOW();
	SET NEW.ptime := NULL;
	SET NEW.cby := uid;
	SET NEW.mby := uid;
	SET NEW.pby := NULL;

	SELECT `bsid`
	INTO x_bsid
	FROM `bills_types`
	WHERE `btypeid` = NEW.btypeid;
	IF x_bsid IS NOT NULL THEN
		SELECT `value`
		INTO cser
		FROM `bills_serials`
		WHERE `bsid` = x_bsid
		FOR UPDATE;

		UPDATE `bills_serials`
		SET `value` = cser + 1
		WHERE `bsid` = x_bsid;

		SET NEW.serial := cser;
	ELSE
		SET NEW.serial := NULL;
	END IF;

	IF NEW.state = 'P' THEN
		SELECT `siotypeid` INTO sio
		FROM `bills_types`
		WHERE `btypeid` = NEW.btypeid;

		IF sio > 0 THEN
			SET bill_sum := NEW.sum;

			SELECT `currid` INTO stash_currid
			FROM `stashes_def`
			WHERE `stashid` = NEW.stashid
			FOR UPDATE;

			INSERT INTO `stashes_io_def` (`siotypeid`, `stashid`, `currid`, `uid`, `ts`, `diff`)
			VALUES (sio, NEW.stashid, NEW.currid, uid, NEW.ptime, NEW.sum);

			IF NOT (NEW.currid <=> stash_currid) THEN
				IF NEW.currid IS NOT NULL THEN
					SELECT `xchange_rate` INTO xrate_from
					FROM `currencies_def`
					WHERE `currid` = NEW.currid;
					SET bill_sum := bill_sum * xrate_from;
				END IF;
				IF stash_currid IS NOT NULL THEN
					SELECT `xchange_rate` INTO xrate_to
					FROM `currencies_def`
					WHERE `currid` = stash_currid;
					SET bill_sum := bill_sum / xrate_to;
				END IF;
			END IF;

			UPDATE `stashes_def`
			SET `amount` = `amount` + bill_sum
			WHERE `stashid` = NEW.stashid;
		END IF;
	END IF;
</%block>
