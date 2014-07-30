## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	SELECT
		`h`.`houseid` AS `houseid`,
		`h`.`streetid` AS `streetid`,
		`h`.`number` AS `number`,
		`h`.`num_slash` AS `num_slash`,
		`h`.`num_suffix` AS `num_suffix`,
		`h`.`building` AS `building`,
		`s`.`name` AS `streetname`,
		addr_format(
			`s`.`name`,
			`s`.`prefix`,
			`s`.`suffix`,
			`h`.`number`,
			`h`.`num_slash`,
			`h`.`num_suffix`,
			`h`.`building`,
			NULL
		) AS `fullname`
	FROM `addr_houses` AS `h`
	LEFT JOIN `addr_streets` AS `s`
	USING(`streetid`)
	WHERE `h`.`entrnum` >= minentr
	ORDER BY `s`.`name`, `h`.`number`, `h`.`num_slash`, `h`.`building`;
</%block>
