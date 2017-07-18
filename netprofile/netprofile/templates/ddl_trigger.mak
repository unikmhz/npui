## -*- coding: utf-8 -*-
##
## NetProfile: Template for SQL TRIGGER DDL
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
CREATE TRIGGER ${trigger}
${raw(trigger.when.upper())} ${raw(trigger.event.upper())}
ON ${table}
FOR EACH ROW
BEGIN
% elif dialect.name == 'postgresql':
CREATE FUNCTION ${raw(trigger.name + '_func()')}
RETURNS TRIGGER AS $$
BEGIN
% endif
<%block name="sql"/>\
% if dialect.name == 'mysql':
END
% elif dialect.name == 'postgresql':
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER ${trigger}
${raw(trigger.when.upper())} ${raw(trigger.event.upper())}
ON ${table}
FOR EACH ROW
EXECUTE PROCEDURE
${raw(trigger.name + '_func()')};
% endif
