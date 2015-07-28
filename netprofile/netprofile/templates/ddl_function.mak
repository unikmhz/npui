## -*- coding: utf-8 -*-
<%namespace name="ddl" module="netprofile.db.ddl" import="ddl_fmt" inheritable="True"/>
% if dialect.name == 'mysql':
% if function.is_procedure:
CREATE PROCEDURE ${function}(
% for arg in function.args:
	${arg}${raw('' if loop.last else ',')}
% endfor
)
% else:
CREATE FUNCTION ${function}(
% for arg in function.args:
	${arg}${raw('' if loop.last else ',')}
% endfor
) RETURNS ${function.returns}
% endif
% if function.reads_sql or function.writes_sql:
NOT DETERMINISTIC
% if function.writes_sql:
MODIFIES SQL DATA
% else:
READS SQL DATA
% endif
% else:
DETERMINISTIC
NO SQL
% endif
SQL SECURITY INVOKER
% if function.comment:
COMMENT ${function.comment}
% endif
% if function.label:
${raw(function.label)}: BEGIN
% else:
BEGIN
% endif
% elif dialect.name == 'postgresql':
	XXX TODO XXX
% endif
<%block name="sql"/>\
% if dialect.name == 'mysql':
END
% elif dialect.name == 'postgresql':
	XXX TODO XXX
% endif
