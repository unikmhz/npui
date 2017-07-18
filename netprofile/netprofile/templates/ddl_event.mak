## -*- coding: utf-8 -*-
##
## NetProfile: Template for SQL EVENT DDL
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
CREATE EVENT ${event}
ON SCHEDULE EVERY ${event.sched_interval} ${raw(event.sched_unit.upper())}
% if event.starts:
STARTS ${event.starts}
% endif
% if event.preserve:
ON COMPLETION PRESERVE
% else:
ON COMPLETION NOT PRESERVE
% endif
% if event.enabled:
ENABLE
% else:
DISABLE
% endif
% if event.comment:
COMMENT ${event.comment}
% endif
DO
BEGIN
% elif dialect.name == 'postgresql':
XXX TODO XXX
% endif
<%block name="sql"/>\
% if dialect.name == 'mysql':
END
% elif dialect.name == 'postgresql':
XXX TODO XXX
% endif
