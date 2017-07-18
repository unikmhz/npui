## -*- coding: utf-8 -*-
##
## NetProfile: Template for SQL FUNCTION/PROCEDURE DDL
## Copyright © 2014-2017 Alex Unigovsky
##
## This file is part of NetProfile.
## NetProfile is free software: you can redistribute it and/or
## modify it under the terms of the GNU Affero General Public
## License as published by the Free Software Foundation, either
## version 3 of the License, or (at your option) any later
## version.
##
## NetProfile is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General
## Public License along with NetProfile. If not, see
## <http://www.gnu.org/licenses/>.
##
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
