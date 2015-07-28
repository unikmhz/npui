## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	IF @ticketid IS NOT NULL THEN
		IF @tcid IS NULL THEN
			INSERT INTO `tickets_changes_def` (`ticketid`, `uid`, `ts`, `comments`)
			VALUES (@ticketid, @accessuid, NOW(), @comments);
			SET @tcid := LAST_INSERT_ID();
		END IF;
		INSERT INTO `tickets_changes_flagmod` (`tcid`, `tftid`, `newstate`)
		VALUES (@tcid, NEW.tftid, 'Y');
	END IF;
</%block>
