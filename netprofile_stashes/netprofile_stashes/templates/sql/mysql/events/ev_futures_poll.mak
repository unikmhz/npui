## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_event.mak"/>\
<%block name="sql">\
	SET @accessuid := 0;
	SET @accessgid := 0;
	SET @accesslogin := '[EV:FUTURES_POLL]';
	CALL futures_poll();
</%block>
