## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	SET @pass_xepid := xepid;
	SET @pass_ts := ts;
	SET @pass_aeid := ps_aeid;
	SET @pass_hostid := ps_hostid;
	SET @pass_paidid := ps_paidid;
	SET @pass_entityid := ps_entityid;
	SET @pass_stashid := ps_stashid;
	SET @pass_qpend := ps_qpend;
	SET @pass_pay := pay;
	SET @cb_query := CONCAT('CALL ', cbname, '(?, ?, ?, ?, ?, @pass_entityid, @pass_stashid, @pass_qpend, @pass_pay)');
	PREPARE cbx FROM @cb_query;
	EXECUTE cbx USING @pass_xepid, @pass_ts, @pass_aeid, @pass_hostid, @pass_paidid;
	DEALLOCATE PREPARE cbx;
	SET ps_entityid := @pass_entityid;
	SET ps_stashid := @pass_stashid;
	SET ps_qpend := @pass_qpend;
	SET pay := @pass_pay;
</%block>

