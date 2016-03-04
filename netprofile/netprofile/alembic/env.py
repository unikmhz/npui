#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: DB migrations environment for Alembic
# © Copyright 2016 Alex 'Unik' Unigovsky
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

from __future__ import with_statement
import decimal
import os
from alembic import context
from alembic.operations import ops
from alembic.autogenerate import rewriter
from alembic.autogenerate.render import (
	_ident,
	_render_server_default,
	_repr_type
)
from sqlalchemy import (
	DefaultClause,
	engine_from_config,
	pool,
	types
)
from sqlalchemy.sql.elements import TextClause
from netprofile.db import ddl as npd
from netprofile.db import fields as npf
from netprofile.db import migrations as npm
from netprofile.db.connection import DBMeta
from netprofile.ext.data import (
	_INTEGER_SET,
	_FLOAT_SET,
	_DECIMAL_SET,
	_DATE_SET,

	_table_to_class
)


_NULL_DATES = (
	'0000-00-00',
	'0000-00-00 00:00',
	'0000-00-00 00:00:00'
)
config = context.config
moddef_filter = config.attributes.get('module', None)
writer = rewriter.Rewriter()


@writer.rewrites(ops.CreateTableOp)
def _create_table(context, revision, op):
	new_rev_id = npm._get_new_rev(context)
	train = [op]
	table = op.to_table(context)
	if hasattr(table, 'comment'):
		train.append(npm.SetTableCommentOp(op.table_name, table.comment))
	if hasattr(table, 'triggers'):
		for trigger in table.triggers:
			train.append(npm.CreateTriggerOp(
				trigger.module,
				op.table_name,
				trigger.when,
				trigger.event,
				new_rev_id
			))
	if len(train) > 1:
		return train
	return op


def _include_object(obj, name, type_, reflected, compare_to):
	if moddef_filter:
		if type_ == 'table':
			if reflected:
				return False
			cls = _table_to_class(obj.name)
			if cls.__moddef__ != moddef_filter:
				return False
	return True


def _compare_default(context, insp_col, meta_col, insp_default, meta_default, rendered_meta_default):
	if isinstance(meta_col.type, _DATE_SET):
		if isinstance(insp_default, str):
			insp_default = insp_default.strip('\'')
		if (meta_default is None) and (insp_default in _NULL_DATES):
			return False

	if isinstance(meta_default, npd.CurrentTimestampDefault):
		on_update = meta_default.on_update
		if npf._is_mysql(context.dialect):
			compare_to = 'CURRENT_TIMESTAMP'
			if on_update:
				compare_to += ' ON UPDATE CURRENT_TIMESTAMP'
			return compare_to != insp_default
		# TODO: compare for other dialects
		return False
	elif isinstance(meta_default, DefaultClause):
		meta_arg = meta_default.arg
		if isinstance(meta_arg, npf.npbool):
			proc = meta_col.type.result_processor(context.dialect, types.Unicode)
			insp_default = insp_default.strip('\'')
			if proc:
				insp_default = proc(insp_default)
			return meta_arg.val != insp_default
		elif isinstance(meta_arg, TextClause):
			meta_text = meta_arg.text

			if (meta_text.upper() == 'NULL') and (insp_default is None):
				return False

			meta_text = meta_text.strip('\'')
			if isinstance(insp_default, str):
				insp_default = insp_default.strip('\'')

			if isinstance(meta_col.type, _INTEGER_SET):
				meta_text = int(meta_text)
				insp_default = int(insp_default) if isinstance(insp_default, str) else None
			elif isinstance(meta_col.type, _FLOAT_SET + _DECIMAL_SET):
				meta_text = decimal.Decimal(meta_text)
				insp_default = decimal.Decimal(insp_default) if isinstance(insp_default, str) else None

			return meta_text != insp_default
	return None


def render_item(type_, obj, autogen_context):
	if type_ == 'type':
		if isinstance(obj, npf.DeclEnumType):
			if obj.enum:
				return 'npf.DeclEnumType(name=%r, values=%r)' % (obj.enum.__name__, list(obj.enum.values()))
		if obj.__module__ == 'netprofile.db.fields':
			autogen_context.imports.add('from netprofile.db import fields as npf')
			return 'npf.%r' % (obj,)
	elif type_ == 'column' and hasattr(obj, 'comment'):
		autogen_context.imports.add('from netprofile.db import ddl as npd')
		# Copied from alembic.autogenerate.render:_render_column
		opts = []
		if obj.server_default:
			rendered = _render_server_default(obj.server_default, autogen_context)
			if rendered:
				opts.append(('server_default', rendered))
		if not obj.autoincrement:
			opts.append(('autoincrement', obj.autoincrement))
		if obj.nullable is not None:
			opts.append(('nullable', obj.nullable))

		return 'sa.Column(%(name)r, %(type)s, npd.Comment(%(comment)r), %(kw)s)' % {
			'name'    : _ident(obj.name),
			'type'    : _repr_type(obj.type, autogen_context),
			'comment' : obj.comment,
			'kw'      : ', '.join(['%s=%s' % (kwname, val) for kwname, val in opts])
		}
	elif type_ == 'server_default':
		if isinstance(obj, npd.CurrentTimestampDefault):
			autogen_context.imports.add('from netprofile.db import ddl as npd')
			return 'npd.CurrentTimestampDefault(on_update=%r)' % (obj.on_update,)
		if isinstance(obj, DefaultClause):
			if isinstance(obj.arg, npf.npbool):
				autogen_context.imports.add('from netprofile.db import fields as npf')
				return 'npf.npbool(%r)' % (obj.arg.val,)
	return False


def run_migrations_offline():
	"""Run migrations in 'offline' mode.

	This configures the context with just a URL
	and not an Engine, though an Engine is acceptable
	here as well.  By skipping the Engine creation
	we don't even need a DBAPI to be available.

	Calls to context.execute() here emit the given string to the
	script output.

	"""
	url = config.get_main_option("sqlalchemy.url")
	context.configure(
		url=url,
		target_metadata=DBMeta,
		literal_binds=True,
		process_revision_directives=writer
	)

	with context.begin_transaction():
		context.run_migrations()


def run_migrations_online():
	"""Run migrations in 'online' mode.

	In this scenario we need to create an Engine
	and associate a connection with the context.

	"""
	connectable = engine_from_config(
		config.get_section(config.config_ini_section),
		prefix='sqlalchemy.',
		poolclass=pool.NullPool
	)

	with connectable.connect() as connection:
		context.configure(
			connection=connection,
			target_metadata=DBMeta,
			include_object=_include_object,
			render_item=render_item,
			compare_type=True,
			compare_server_default=_compare_default,
			process_revision_directives=writer
		)

		with context.begin_transaction():
			context.run_migrations()


if context.is_offline_mode():
	run_migrations_offline()
else:
	run_migrations_online()

