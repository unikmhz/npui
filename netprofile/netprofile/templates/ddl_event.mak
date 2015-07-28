## -*- coding: utf-8 -*-
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
