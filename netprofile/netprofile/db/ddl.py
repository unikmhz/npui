#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Custom DDL constructs for SQLAlchemy
# © Copyright 2013-2014 Alex 'Unik' Unigovsky
#
# This file is part of NetProfile.
# NetProfile is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later
# version.
#
# NetProfile is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General
# Public License along with NetProfile. If not, see
# <http://www.gnu.org/licenses/>.

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import sys
import datetime as dt

from sqlalchemy.schema import (
	Column,
	DefaultClause,
	DDLElement,
	SchemaItem,
	Table
)
from sqlalchemy import (
	event,
	text
)
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql.expression import ClauseElement
from sqlalchemy.sql.functions import FunctionElement
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Query

from pyramid.renderers import render

from netprofile.ext.data import _table_to_class
from .connection import Base

class CurrentTimestampDefaultItem(ClauseElement):
	def __init__(self, on_update=False):
		self.on_update = on_update

@compiles(CurrentTimestampDefaultItem, 'mysql')
def visit_timestamp_default_mysql(element, compiler, **kw):
	ddl = 'CURRENT_TIMESTAMP'
	if element.on_update:
		ddl += ' ON UPDATE CURRENT_TIMESTAMP'
	return ddl

@compiles(CurrentTimestampDefaultItem)
def visit_timestamp_default(element, compiler, **kw):
	return 'CURRENT_TIMESTAMP'

class CurrentTimestampDefault(DefaultClause):
	def __init__(self, on_update=False):
		self.on_update = on_update
		super(CurrentTimestampDefault, self).__init__(
			CurrentTimestampDefaultItem(on_update),
			for_update=on_update
		)

	def _set_parent(self, column):
		self.column = column
		self.column.server_default = self
		if self.on_update:
			self.column.server_onupdate = self

class SQLFunctionArgument(DDLElement):
	def __init__(self, name, arg_type, arg_dir=None):
		self.name = name
		self.type = arg_type
		self.dir = arg_dir

class InArgument(SQLFunctionArgument):
	def __init__(self, name, arg_type):
		super(InArgument, self).__init__(name, arg_type, 'IN')

class OutArgument(SQLFunctionArgument):
	def __init__(self, name, arg_type):
		super(OutArgument, self).__init__(name, arg_type, 'OUT')

class InOutArgument(SQLFunctionArgument):
	def __init__(self, name, arg_type):
		super(InOutArgument, self).__init__(name, arg_type, 'INOUT')

@compiles(SQLFunctionArgument, 'mysql')
def visit_sql_function_arg(element, compiler, **kw):
	return '%s %s %s' % (
		element.dir if element.dir else '',
		compiler.sql_compiler.preparer.quote(element.name),
		compiler.dialect.type_compiler.process(element.type)
	)

class AlterTableAlterColumn(DDLElement):
	def __init__(self, table, column):
		self.table = table
		self.column = column

@compiles(AlterTableAlterColumn, 'mysql')
def visit_alter_table_alter_column_mysql(element, compiler, **kw):
	table = element.table
	col = element.column
	spec = compiler.get_column_specification(col, first_pk=col.primary_key)
	const = " ".join(compiler.process(constraint) \
			for constraint in col.constraints)
	if const:
		spec += " " + const
	if col.comment:
		spec += " COMMENT " + compiler.sql_compiler.render_literal_value(col.comment, sqltypes.STRINGTYPE)
	return 'ALTER TABLE %s CHANGE COLUMN %s %s' % (
		compiler.sql_compiler.preparer.format_table(table),
		compiler.sql_compiler.preparer.format_column(col),
		spec
	)

class SetTableComment(DDLElement):
	def __init__(self, table, comment):
		self.table = table
		self.text = comment

class SetColumnComment(DDLElement):
	def __init__(self, column, comment):
		self.column = column
		self.text = comment

class Comment(SchemaItem):
	"""
	Represents a table comment DDL.
	"""
	def __init__(self, ctext):
		self.text = ctext

	def _set_parent(self, parent):
		self.parent = parent
		parent.comment = self.text
		if isinstance(parent, Table):
			SetTableComment(parent, self.text).execute_at('after_create', parent)
		elif isinstance(parent, Column):
			text = self.text
			if not parent.doc:
				parent.doc = text
			def _set_col_comment(column, meta):
				SetColumnComment(column, text).execute_at('after_create', column.table)

			event.listen(
				parent,
				'after_parent_attach',
				_set_col_comment
			)

@compiles(SetColumnComment, 'mysql')
def visit_set_column_comment_mysql(element, compiler, **kw):
	spec = compiler.get_column_specification(element.column, first_pk=element.column.primary_key)
	const = " ".join(compiler.process(constraint) \
			for constraint in element.column.constraints)
	if const:
		spec += " " + const

	return 'ALTER TABLE %s MODIFY COLUMN %s COMMENT %s' % (
		compiler.sql_compiler.preparer.format_table(element.column.table),
		spec,
		compiler.sql_compiler.render_literal_value(element.text, sqltypes.STRINGTYPE)
	)

@compiles(SetColumnComment, 'postgresql')
@compiles(SetColumnComment, 'oracle')
def visit_set_column_comment_pgsql(element, compiler, **kw):
	return 'COMMENT ON COLUMN %s IS %s' % (
		compiler.sql_compiler.process(element.column),
		compiler.sql_compiler.render_literal_value(element.text, sqltypes.STRINGTYPE)
	)

@compiles(SetColumnComment)
def visit_set_column_comment(element, compiler, **kw):
	pass

@compiles(SetTableComment, 'mysql')
def visit_set_table_comment_mysql(element, compiler, **kw):
	return 'ALTER TABLE %s COMMENT=%s' % (
		compiler.sql_compiler.preparer.format_table(element.table),
		compiler.sql_compiler.render_literal_value(element.text, sqltypes.STRINGTYPE)
	)

@compiles(SetTableComment, 'postgresql')
@compiles(SetTableComment, 'oracle')
def visit_set_table_comment_pgsql(element, compiler, **kw):
	return 'COMMENT ON TABLE %s IS %s' % (
		compiler.sql_compiler.preparer.format_table(element.table),
		compiler.sql_compiler.render_literal_value(element.text, sqltypes.STRINGTYPE)
	)

@compiles(SetTableComment)
def visit_set_table_comment(element, compiler, **kw):
	pass

def ddl_fmt(ctx, obj):
	compiler = ctx['compiler']
	if isinstance(obj, (Trigger, SQLFunction, SQLEvent)):
		return compiler.sql_compiler.preparer.quote(obj.name)
	if isinstance(obj, Table):
		return compiler.sql_compiler.preparer.format_table(obj)
	if isinstance(obj, DeclarativeMeta):
		return compiler.sql_compiler.preparer.format_table(obj.__table__)
	if isinstance(obj, DDLElement):
		return compiler.process(obj)
	if isinstance(obj, sqltypes.TypeEngine):
		return compiler.dialect.type_compiler.process(obj)
	if isinstance(obj, (FunctionElement, ClauseElement)):
		return compiler.sql_compiler.process(obj)
	if isinstance(obj, dt.datetime):
		dname = compiler.dialect.name
		date = obj
		if dname in ('mysql', 'postgresql', 'sqlite'):
			date = date.strftime('%Y-%m-%d %H:%M:%S')
		return compiler.sql_compiler.render_literal_value(date, sqltypes.STRINGTYPE)
	if isinstance(obj, str):
		return compiler.sql_compiler.render_literal_value(obj, sqltypes.STRINGTYPE)
	if isinstance(obj, int):
		return compiler.sql_compiler.render_literal_value(obj, sqltypes.INTEGERTYPE)
	raise ValueError('Unable to format value for DDL')

class CreateTrigger(DDLElement):
	def __init__(self, table, trigger):
		self.table = table
		self.trigger = trigger

class DropTrigger(DDLElement):
	def __init__(self, table, trigger):
		self.table = table
		self.trigger = trigger

@compiles(CreateTrigger)
def visit_create_trigger(element, compiler, **kw):
	table = element.table
	cls = _table_to_class(table.name)
	module = cls.__module__.split('.')[0]
	trigger = element.trigger
	tpldef = {
		'table'    : table,
		'class'    : cls,
		'module'   : module,
		'compiler' : compiler,
		'dialect'  : compiler.dialect,
		'trigger'  : trigger,
		'raw'      : text
	}
	tpldef.update(Base._decl_class_registry.items())

	tplname = '%s:templates/sql/%s/triggers/%s.mak' % (
		module,
		compiler.dialect.name,
		trigger.name
	)
	return render(tplname, tpldef, package=sys.modules[module])

@compiles(DropTrigger, 'postgresql')
def visit_drop_trigger_mysql(element, compiler, **kw):
	return 'DROP TRIGGER %s ON %s' % (
		compiler.sql_compiler.preparer.quote(element.trigger.name),
		compiler.sql_compiler.preparer.format_table(element.parent)
	)

@compiles(DropTrigger)
def visit_drop_trigger(element, compiler, **kw):
	return 'DROP TRIGGER %s' % (
		compiler.sql_compiler.preparer.quote(element.trigger.name),
	)

class Trigger(SchemaItem):
	"""
	Schema element that attaches a trigger template to an object.
	"""
	def __init__(self, when='before', event='insert', name=None):
		self.when = when
		self.event = event
		self.name = name

	def _set_parent(self, parent):
		if isinstance(parent, Table):
			self.parent = parent
			CreateTrigger(parent, self).execute_at('after_create', parent)
			DropTrigger(parent, self).execute_at('before_drop', parent)

class CreateFunction(DDLElement):
	"""
	SQL function template DDL object.
	"""
	def __init__(self, func, module):
		self.func = func
		self.module = module

@compiles(CreateFunction)
def visit_create_function(element, compiler, **kw):
	func = element.func
	name = func.name
	module = 'netprofile_' + element.module
	tpldef = {
		'function' : func,
		'name'     : name,
		'module'   : module,
		'compiler' : compiler,
		'dialect'  : compiler.dialect,
		'raw'      : text
	}
	tpldef.update(Base._decl_class_registry.items())

	tplname = '%s:templates/sql/%s/functions/%s.mak' % (
		module,
		compiler.dialect.name,
		name
	)
	return render(tplname, tpldef, package=sys.modules[module])

class DropFunction(DDLElement):
	"""
	SQL DROP FUNCTION DDL object.
	"""
	def __init__(self, func):
		self.func = func

@compiles(DropFunction, 'postgresql')
def visit_drop_function_pgsql(element, compiler, **kw):
	func = element.func
	name = func.name
	return 'DROP FUNCTION %s' % (
		compiler.sql_compiler.preparer.quote(name),
	)

@compiles(DropFunction)
def visit_drop_function(element, compiler, **kw):
	func = element.func
	name = func.name
	is_proc = func.is_procedure
	return 'DROP %s %s' % (
		'PROCEDURE' if is_proc else 'FUNCTION',
		compiler.sql_compiler.preparer.quote(name)
	)

class SQLFunction(object):
	"""
	Schema element that defines an SQL function or procedure.
	"""
	def __init__(self, name, args=(), returns=None, comment=None, reads_sql=True, writes_sql=True, is_procedure=False, label=None):
		self.name = name
		self.args = args
		self.returns = returns
		self.comment = comment
		self.reads_sql = reads_sql
		self.writes_sql = writes_sql
		self.is_procedure = is_procedure
		self.label = label

	def create(self, modname):
		return CreateFunction(self, modname)

	def drop(self):
		return DropFunction(self)

class CreateEvent(DDLElement):
	"""
	SQL event template DDL object.
	"""
	def __init__(self, evt, module):
		self.event = evt
		self.module = module

@compiles(CreateEvent, 'mysql')
def visit_create_event_mysql(element, compiler, **kw):
	evt = element.event
	name = evt.name
	module = 'netprofile_' + element.module
	tpldef = {
		'event'    : evt,
		'name'     : name,
		'module'   : module,
		'compiler' : compiler,
		'dialect'  : compiler.dialect,
		'raw'      : text
	}
	tpldef.update(Base._decl_class_registry.items())

	tplname = '%s:templates/sql/%s/events/%s.mak' % (
		module,
		compiler.dialect.name,
		name
	)
	return render(tplname, tpldef, package=sys.modules[module])

class DropEvent(DDLElement):
	"""
	SQL DROP EVENT DDL object.
	"""
	def __init__(self, evt):
		self.event = evt

@compiles(DropEvent, 'mysql')
def visit_drop_event_mysql(element, compiler, **kw):
	evt = element.event
	return 'DROP EVENT %s' % (
		compiler.sql_compiler.preparer.quote(evt.name),
	)

class SQLEvent(object):
	"""
	Schema element that defines some periodically executed SQL code.
	"""
	def __init__(self, name, sched_unit='month', sched_interval=1, starts=None, preserve=True, enabled=True, comment=None):
		self.name = name
		self.preserve = preserve
		self.enabled = enabled
		self.comment = comment
		self.sched_unit = sched_unit
		self.sched_interval = sched_interval
		self.starts = starts

	def create(self, modname):
		return CreateEvent(self, modname)

	def drop(self):
		return DropEvent(self)

class CreateView(DDLElement):
	"""
	SQL create view DDL object.
	"""
	def __init__(self, name, select, check_option=None):
		self.name = name
		self.select = select
		self.check = check_option

class DropView(DDLElement):
	"""
	SQL drop view DDL object.
	"""
	def __init__(self, name):
		self.name = name

@compiles(CreateView)
def visit_create_view(element, compiler, **kw):
	sel = element.select
	co = ''
	if callable(sel):
		sel = sel()
	if isinstance(sel, Query):
		ctx = sel._compile_context()
		ctx.statement.use_labels = True
		conn = sel.session.connection(mapper=sel._mapper_zero_or_none(), clause=ctx.statement)
		sel = ctx.statement.compile(conn, compile_kwargs={ 'literal_binds': True })
	else:
		sel = compiler.sql_compiler.process(sel, literal_binds=True)
	if element.check:
		if isinstance(element.check, str):
			co = ' WITH %s CHECK OPTION' % (element.check.upper(),)
		else:
			co = ' WITH CHECK OPTION'
	return 'CREATE VIEW %s AS %s%s' % (
		compiler.sql_compiler.preparer.quote(element.name),
		sel, co
	)

@compiles(DropView)
def visit_drop_view(element, compiler, **kw):
	return 'DROP VIEW %s' % (
		compiler.sql_compiler.preparer.quote(element.name),
	)

class View(SchemaItem):
	"""
	Schema element that attaches a view with a predefined query to an object.
	"""
	def __init__(self, name, select, check_option=None):
		self.name = name
		self.select = select
		self.check = check_option

	def _set_parent(self, parent):
		if isinstance(parent, Table):
			self.parent = parent
			CreateView(self.name, self.select, check_option=self.check).execute_at('after_create', parent)
			DropView(self.name).execute_at('before_drop', parent)

	def create(self):
		return CreateView(self.name, self.select, check_option=self.check)

	def drop(self):
		return DropView(self.name)

