#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Custom DDL constructs for SQLAlchemy
# © Copyright 2013 Alex 'Unik' Unigovsky
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

from sqlalchemy.schema import (
	Column,
	DDLElement,
	SchemaItem,
	Table
)
from sqlalchemy import event
from sqlalchemy.ext.compiler import compiles

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
		compiler.sql_compiler.render_literal_value(element.text, None)
	)

@compiles(SetColumnComment, 'postgresql')
@compiles(SetColumnComment, 'oracle')
def visit_set_column_comment_pgsql(element, compiler, *kw):
	return 'COMMENT ON COLUMN %s IS %s' % (
		compiler.sql_compiler.process(element.column),
		compiler.sql_compiler.render_literal_value(element.text, None)
	)

@compiles(SetColumnComment)
def visit_set_column_comment(element, compiler, *kw):
	pass

@compiles(SetTableComment, 'mysql')
def visit_set_table_comment_mysql(element, compiler, *kw):
	return 'ALTER TABLE %s COMMENT=%s' % (
		compiler.sql_compiler.preparer.format_table(element.table),
		compiler.sql_compiler.render_literal_value(element.text, None)
	)

@compiles(SetTableComment, 'postgresql')
@compiles(SetTableComment, 'oracle')
def visit_set_table_comment_pgsql(element, compiler, *kw):
	return 'COMMENT ON TABLE %s IS %s' % (
		compiler.sql_compiler.preparer.format_table(element.table),
		compiler.sql_compiler.render_literal_value(element.text, None)
	)

@compiles(SetTableComment)
def visit_set_table_comment(element, compiler, *kw):
	pass

def ddl_fmt(obj):
	pass

