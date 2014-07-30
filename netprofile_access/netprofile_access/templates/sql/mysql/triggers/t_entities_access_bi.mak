## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	DECLARE xowned ENUM('Y', 'N') DEFAULT 'N';

	SET NEW.ut_ingress := 0;
	SET NEW.ut_egress := 0;
	SET NEW.qpend := NULL;

	IF NEW.ipaddrid IS NOT NULL THEN
		SELECT `owned` INTO xowned
		FROM `ipaddr_def`
		WHERE `ipaddrid` = NEW.ipaddrid;

		IF xowned = 'Y' THEN
			SET NEW.ipaddrid := NULL;
		ELSE
			UPDATE `ipaddr_def`
			SET `owned` = 'Y'
			WHERE `ipaddrid` = NEW.ipaddrid;
		END IF;
	END IF;

	IF NEW.ip6addrid IS NOT NULL THEN
		SELECT `owned` INTO xowned
		FROM `ip6addr_def`
		WHERE `ip6addrid` = NEW.ip6addrid;

		IF xowned = 'Y' THEN
			SET NEW.ip6addrid := NULL;
		ELSE
			UPDATE `ip6addr_def`
			SET `owned` = 'Y'
			WHERE `ip6addrid` = NEW.ip6addrid;
		END IF;
	END IF;
</%block>
