## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	DECLARE fulladdr VARCHAR(255) DEFAULT NULL;
	DECLARE CONTINUE HANDLER FOR NOT FOUND BEGIN END;
	SELECT addr_format(
		`s`.`name`,
		`s`.`prefix`,
		`s`.`suffix`,
		`h`.`number`,
		`h`.`num_slash`,
		`h`.`num_suffix`,
		`h`.`building`,
		NULL
	) INTO fulladdr
	FROM `addr_houses` AS `h`
	LEFT JOIN `addr_streets` AS `s`
	USING(`streetid`)
	WHERE `h`.`houseid` = hid;
	RETURN fulladdr;
</%block>
