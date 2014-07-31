## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_event.mak"/>\
<%block name="sql">\
	SET @accessuid := 0;
	SET @accessgid := 0;
	SET @accesslogin := '[EV:ACCT_POLL]';
	CALL acct_poll(NOW());
</%block>
