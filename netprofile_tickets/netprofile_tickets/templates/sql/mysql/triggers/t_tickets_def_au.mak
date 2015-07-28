## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `tickets_changes_def` (`ticketid`, `ttrid`, `uid`, `ts`, `show_client`, `comments`)
	VALUES (NEW.ticketid, @ttrid, @accessuid, NOW(), IF(@show_client, 'Y', 'N'), @comments);
	SET @tcid := LAST_INSERT_ID();
	IF OLD.entityid <> NEW.entityid THEN
		INSERT INTO `tickets_changes_bits` (`tcid`, `tcfid`, `old`, `new`)
		VALUES (@tcid, 5, OLD.entityid, NEW.entityid);
	END IF;
	IF (OLD.assigned_uid <> NEW.assigned_uid) OR (NOT OLD.assigned_uid <=> NEW.assigned_uid) THEN
		INSERT INTO `tickets_changes_bits` (`tcid`, `tcfid`, `old`, `new`)
		VALUES (@tcid, 1, OLD.assigned_uid, NEW.assigned_uid);
	END IF;
	IF (OLD.assigned_gid <> NEW.assigned_gid) OR (NOT OLD.assigned_gid <=> NEW.assigned_gid) THEN
		INSERT INTO `tickets_changes_bits` (`tcid`, `tcfid`, `old`, `new`)
		VALUES (@tcid, 2, OLD.assigned_gid, NEW.assigned_gid);
	END IF;
	IF (OLD.assigned_time <> NEW.assigned_time) OR (NOT OLD.assigned_time <=> NEW.assigned_time) THEN
		INSERT INTO `tickets_changes_bits` (`tcid`, `tcfid`, `old`, `new`)
		VALUES (@tcid, 3, OLD.assigned_time, NEW.assigned_time);
	END IF;
	IF OLD.archived <> NEW.archived THEN
		INSERT INTO `tickets_changes_bits` (`tcid`, `tcfid`, `old`, `new`)
		VALUES (@tcid, 4, OLD.archived, NEW.archived);
	END IF;
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 3, 2, CONCAT_WS(" ",
		"Modified ticket",
		CONCAT("[ID ", NEW.ticketid, "]"),
		CONCAT("[TCID ", @tcid, "]")
	));
</%block>
