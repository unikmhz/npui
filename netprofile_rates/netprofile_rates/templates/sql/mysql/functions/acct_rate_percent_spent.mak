## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE qplength, qpspent INT UNSIGNED DEFAULT 0;

	SET qplength := acct_rate_qplength(qpa, qpu, endtime);
	SET qpspent := acct_rate_qpspent(qpa, qpu, time, endtime);
	RETURN CAST((qpspent / qplength) AS DECIMAL(11,10));
</%block>
