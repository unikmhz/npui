## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.diff := OLD.diff;
	SET NEW.stashid := OLD.stashid;
	SET NEW.mby := IF(@accessuid > 0, @accessuid, NULL);
	IF OLD.state = 'P' THEN
		SET NEW.state := 'P';
		SET NEW.ptime := OLD.ptime;
	ELSEIF OLD.state = 'C' THEN
		SET NEW.state := 'C';
		SET NEW.ptime := OLD.ptime;
	ELSE
		UPDATE `stashes_def`
		SET `credit` = `credit` - NEW.diff
		WHERE `stashid` = NEW.stashid;
	END IF;
</%block>
