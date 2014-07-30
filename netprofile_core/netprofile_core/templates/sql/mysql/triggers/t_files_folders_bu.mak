## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.ctime := OLD.ctime;
	IF (NOT (OLD.parentid <=> NEW.parentid)
	OR NOT (OLD.uid <=> NEW.uid)
	OR NOT (OLD.gid <=> NEW.gid)
	OR (OLD.rights <> NEW.rights)
	OR (OLD.name <> NEW.name)
	OR NOT (OLD.descr <=> NEW.descr))
	THEN
		SET NEW.mtime := NOW();
	ELSE
		SET NEW.mtime := OLD.mtime;
	END IF;
</%block>
