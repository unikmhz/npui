## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_event.mak"/>\
<%block name="sql">\
	SET @accessuid := 0;
	SET @accessgid := 0;
	SET @accesslogin := '[EV:PS_POLL]';
	CALL ps_poll(NOW());
</%block>

