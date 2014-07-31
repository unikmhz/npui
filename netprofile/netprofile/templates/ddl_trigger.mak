## -*- coding: utf-8 -*-
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
