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

from sqlalchemy.schema import (
	Column,
	DefaultClause,
	DDLElement,
	SchemaItem,
	Table
)
from sqlalchemy import event
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql.expression import ClauseElement
from sqlalchemy.sql.functions import FunctionElement
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import DeclarativeMeta

from pyramid.renderers import render

from netprofile.ext.data import _table_to_class
from .connection import Base

class CurrentTimestampDefaultItem(ClauseElement):
	def __init__(self, on_update=False):
		self.on_update = on_update

@compiles(CurrentTimestampDefaultItem, 'mysql')
def visit_timestamp_default_mysql(element, compiler, *kw):
	ddl = 'CURRENT_TIMESTAMP'
	if element.on_update:
		ddl += ' ON UPDATE CURRENT_TIMESTAMP'
	return ddl

@compiles(CurrentTimestampDefaultItem)
def visit_timestamp_default(element, compiler, *kw):
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
def visit_set_column_comment_mysql(element, compiler, *kw):
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
def visit_set_column_comment_pgsql(element, compiler, *kw):
	return 'COMMENT ON COLUMN %s IS %s' % (
		compiler.sql_compiler.process(element.column),
		compiler.sql_compiler.render_literal_value(element.text, sqltypes.STRINGTYPE)
	)

@compiles(SetColumnComment)
def visit_set_column_comment(element, compiler, *kw):
	pass

@compiles(SetTableComment, 'mysql')
def visit_set_table_comment_mysql(element, compiler, *kw):
	return 'ALTER TABLE %s COMMENT=%s' % (
		compiler.sql_compiler.preparer.format_table(element.table),
		compiler.sql_compiler.render_literal_value(element.text, sqltypes.STRINGTYPE)
	)

@compiles(SetTableComment, 'postgresql')
@compiles(SetTableComment, 'oracle')
def visit_set_table_comment_pgsql(element, compiler, *kw):
	return 'COMMENT ON TABLE %s IS %s' % (
		compiler.sql_compiler.preparer.format_table(element.table),
		compiler.sql_compiler.render_literal_value(element.text, sqltypes.STRINGTYPE)
	)

@compiles(SetTableComment)
def visit_set_table_comment(element, compiler, *kw):
	pass

def ddl_fmt(ctx, obj):
	compiler = ctx['compiler']
	if isinstance(obj, Trigger):
		return compiler.sql_compiler.preparer.quote(obj.name)
	if isinstance(obj, Table):
		return compiler.sql_compiler.preparer.format_table(obj)
	if isinstance(obj, DeclarativeMeta):
		return compiler.sql_compiler.preparer.format_table(obj.__table__)
	if isinstance(obj, DDLElement):
		return compiler.process(obj)
	if isinstance(obj, (FunctionElement, ClauseElement)):
		return compiler.sql_compiler.process(obj)
	return str(obj)

class CreateTrigger(DDLElement):
	def __init__(self, table, trigger):
		self.table = table
		self.trigger = trigger

class DropTrigger(DDLElement):
	def __init__(self, table, trigger):
		self.table = table
		self.trigger = trigger

@compiles(CreateTrigger)
def visit_create_trigger(element, compiler, *kw):
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
		'trigger'  : trigger
	}
	tpldef.update(Base._decl_class_registry.items())

	tplname = '%s:templates/sql/%s/triggers/%s.mak' % (
		module,
		compiler.dialect.name,
		trigger.name
	)
	return render(tplname, tpldef, package=sys.modules[module])

@compiles(DropTrigger, 'mysql')
def visit_drop_trigger_mysql(element, compiler, *kw):
	return 'DROP TRIGGER %s' % (
		compiler.sql_compiler.preparer.quote(element.trigger.name),
	)

@compiles(DropTrigger, 'postgresql')
def visit_drop_trigger_mysql(element, compiler, *kw):
	return 'DROP TRIGGER %s ON %s' % (
		compiler.sql_compiler.preparer.quote(element.trigger.name),
		compiler.sql_compiler.preparer.format_table(element.parent)
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

