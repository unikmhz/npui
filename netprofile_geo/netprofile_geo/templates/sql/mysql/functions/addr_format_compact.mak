## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_function.mak"/>\
<%block name="sql">\
	RETURN CONCAT_WS(' ',
		IF(streetname IS NULL OR streetname = '',
			NULL,
			streetname
		),
		IF(num = 0,
			CONCAT(
				bld,
				IF(num_suffix IS NULL OR num_suffix = '', '', num_suffix),
				IF(num_slash IS NULL OR num_slash = 0, '', CONCAT('/', num_slash))
			),
			CONCAT(
				num,
				IF(num_suffix IS NULL OR num_suffix = '', '', num_suffix),
				IF(num_slash IS NULL OR num_slash = 0, '', CONCAT('/', num_slash))
			)
		),
		IF(bld IS NULL OR bld = 0,
			NULL,
			CONCAT('bld.', bld)
		),
		IF(fl IS NULL OR fl = 0,
			NULL,
			CONCAT('app.', fl)
		)
	);
</%block>
