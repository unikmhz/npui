## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE qplength, qprem INT UNSIGNED DEFAULT 0;

	SET qplength := acct_rate_qplength(qpa, qpu, endtime);
	SET qprem := UNIX_TIMESTAMP(endtime) - UNIX_TIMESTAMP(time);
	RETURN CAST((qprem / qplength) AS DECIMAL(11,10));
</%block>
