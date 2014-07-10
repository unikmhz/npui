## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	INSERT INTO `hosts_def` (`hgid`, `entityid`, `domainid`, `name`, `aliasid`, `ctime`, `cby`, `mby`)
	SELECT `hgid`, `entityid`, did, aname, hid, NOW(), @accessuid, @accessuid
	FROM `hosts_def`
	WHERE `hostid` = hid;
</%block>
