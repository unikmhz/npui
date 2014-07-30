## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	SET NEW.entityid := OLD.entityid;
	SET NEW.startts := OLD.startts;
	IF NEW.endts > OLD.endts THEN
		SET NEW.endts := OLD.endts;
	END IF;

	IF (OLD.bstate = 'expired') THEN
		SET NEW.bstate := 'expired';
	ELSEIF (NEW.bstate = 'expired') THEN
		SET NEW.endts := NOW();
	END IF;
</%block>
