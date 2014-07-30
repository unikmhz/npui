## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `sessions_history` (`name`, `stationid`, `entityid`, `ipaddrid`, `ip6addrid`, `destid`, `nasid`, `csid`, `called`, `startts`, `endts`, `ut_ingress`, `ut_egress`, `pol_ingress`, `pol_egress`)
	VALUES (OLD.name, OLD.stationid, OLD.entityid, OLD.ipaddrid, OLD.ip6addrid, OLD.destid, OLD.nasid, OLD.csid, OLD.called, OLD.startts, OLD.updatets, OLD.ut_ingress, OLD.ut_egress, OLD.pol_ingress, OLD.pol_egress);
</%block>
