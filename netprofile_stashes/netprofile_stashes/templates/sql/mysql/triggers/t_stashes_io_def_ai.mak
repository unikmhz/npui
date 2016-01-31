## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	IF (@stashio_ignore IS NULL) OR (@stashio_ignore <> 1) THEN
		INSERT INTO `stashes_ops` (`stashid`, `type`, `ts`, `operator`, `diff`, `comments`)
		VALUES (NEW.stashid, 'oper', NEW.ts, NEW.uid, NEW.diff, CONCAT('sio:', NEW.sioid, '|'));
	END IF;
</%block>
