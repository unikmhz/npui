#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: DB migrations support code
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

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import os
import sys

from alembic.config import Config
from alembic.operations import (
	MigrateOperation,
	Operations
)
from alembic.autogenerate import (
	comparators,
	renderers
)

from netprofile.db.fields import (
	_is_mysql,
	render_variants
)
from netprofile.db.ddl import (
	CreateEvent,
	CreateFunction,
	CreateTrigger,
	CreateView,

	DropEvent,
	DropFunction,
	DropTrigger,
	DropView,

	SetTableComment,

	Trigger
)
from netprofile.tpl.util import (
	diff_sqltpl,
	get_sqltpl_revisions,
	new_sqltpl_revision
)

def _get_new_rev(context):
	rctx = context.opts.get('revision_context')
	if rctx and (len(rctx.generated_revisions) == 1):
		return rctx.generated_revisions[0].rev_id

def _find_newest_rev(script, moddef, revs):
	for insp in script.walk_revisions(head=moddef + '@head', base=moddef + '@base'):
		rev_id = insp.revision
		if rev_id in revs:
			return rev_id

def get_alembic_config(mm, ini_file=None, ini_section='migrations', stdout=sys.stdout):
	appcfg = mm.cfg.get_settings()
	cfg = Config(file_=ini_file, ini_section=ini_section, stdout=stdout)

	if cfg.get_main_option('script_location') is None:
		cfg.set_main_option('script_location', 'netprofile:alembic')
	if cfg.get_main_option('sqlalchemy.url') is None:
		cfg.set_main_option('sqlalchemy.url', appcfg.get('sqlalchemy.url'))
	if cfg.get_main_option('output_encoding') is None:
		cfg.set_main_option('output_encoding', 'utf-8')
	migration_paths = []
	for mod in mm.modules.values():
		if mod.dist and mod.dist.location:
			path = os.path.join(mod.dist.location, 'migrations')
			if os.path.isdir(path):
				migration_paths.append(path)
	if len(migration_paths) > 0:
		cfg.set_main_option('version_locations', ' '.join(migration_paths))

	cfg.attributes['mm'] = mm
	return cfg

@Operations.register_operation('set_table_comment')
class SetTableCommentOp(MigrateOperation):
	"""
	Create comment on a table.
	"""
	def __init__(self, table, comment):
		self.table = table
		self.comment = comment

	@classmethod
	def set_table_comment(cls, operations, table, comment):
		"""
		Create comment on a table.
		"""
		op = SetTableCommentOp(table, comment)
		return operations.invoke(op)

@Operations.register_operation('create_trigger')
class CreateTriggerOp(MigrateOperation):
	"""
	Create a trigger on a table.
	"""
	def __init__(self, module, table, when, action, migration=None):
		self.module = module
		self.table = table
		self.when = when
		self.action = action
		self.migration = migration
		self.name = 't_%s_%s%s' % (table, when[0].lower(), action[0].lower())

	def reverse(self):
		return DropTriggerOp(self.module, self.table, self.when, self.action, self.migration)

	@classmethod
	def create_trigger(cls, operations, module, table, when, action, migration=None, **kwargs):
		"""
		Issue "CREATE TRIGGER" DDL command.
		"""
		op = CreateTriggerOp(module, table, when, action, migration, **kwargs)
		return operations.invoke(op)

@Operations.register_operation('drop_trigger')
class DropTriggerOp(MigrateOperation):
	"""
	Drop table trigger.
	"""
	def __init__(self, module, table, when, action, migration=None):
		self.module = module
		self.table = table
		self.when = when
		self.action = action
		self.migration = migration
		self.name = 't_%s_%s%s' % (table, when[0].lower(), action[0].lower())

	def reverse(self):
		return CreateTriggerOp(self.module, self.table, self.when, self.action, self.migration)

	@classmethod
	def drop_trigger(cls, operations, module, table, when, action, migration=None, **kwargs):
		"""
		Issue "DROP TRIGGER" DDL command.
		"""
		op = DropTriggerOp(module, table, when, action, migration, **kwargs)
		return operations.invoke(op)

@Operations.register_operation('create_function')
class CreateFunctionOp(MigrateOperation):
	"""
	Create SQL function or procedure.
	"""
	def __init__(self, module, func, migration=None):
		self.module = module
		self.func = func
		self.migration = migration

	def reverse(self):
		return DropFunctionOp(self.module, self.func, self.migration)

	@classmethod
	def create_function(cls, operations, module, func, migration=None):
		"""
		Issue "CREATE FUNCTION" or "CREATE PROCEDURE" DDL command.
		"""
		op = CreateFunctionOp(module, func, migration)
		return operations.invoke(op)

@Operations.register_operation('drop_function')
class DropFunctionOp(MigrateOperation):
	"""
	Drop SQL function or procedure.
	"""
	def __init__(self, module, func, migration=None):
		self.module = module
		self.func = func
		self.migration = migration

	def reverse(self):
		return CreateFunctionOp(self.module, self.func, self.migration)

	@classmethod
	def drop_function(cls, operations, module, func, migration=None):
		"""
		Issue "DROP FUNCTION" or "DROP PROCEDURE" DDL command.
		"""
		op = DropFunctionOp(module, func, migration)
		return operations.invoke(op)

@Operations.register_operation('create_event')
class CreateEventOp(MigrateOperation):
	"""
	Create SQL periodically run routine.
	"""
	def __init__(self, module, evt, migration=None):
		self.module = module
		self.event = evt
		self.migration = migration

	def reverse(self):
		return DropEventOp(self.module, self.event, self.migration)

	@classmethod
	def create_event(cls, operations, module, evt, migration=None):
		"""
		Issue "CREATE EVENT" or similar DDL command.
		"""
		op = CreateEventOp(module, evt, migration)
		return operations.invoke(op)

@Operations.register_operation('drop_event')
class DropEventOp(MigrateOperation):
	"""
	Drop SQL periodically run routine.
	"""
	def __init__(self, module, evt, migration=None):
		self.module = module
		self.event = evt
		self.migration = migration

	def reverse(self):
		return CreateEventOp(self.module, self.event, self.migration)

	@classmethod
	def drop_event(cls, operations, module, evt, migration=None):
		"""
		Issue "DROP EVENT" or similar DDL command.
		"""
		op = DropEventOp(module, evt, migration)
		return operations.invoke(op)

@Operations.register_operation('create_view')
class CreateViewOp(MigrateOperation):
	"""
	Create SQL view.
	"""
	def __init__(self, name, select, check_option=False):
		self.name = name
		self.select = select
		self.check_option = check_option

	def reverse(self):
		return DropViewOp(self.name, self.select, self.check_option)

	@classmethod
	def create_view(cls, operations, name, select, check_option=False):
		"""
		Issue "CREATE VIEW" DDL command.
		"""
		op = CreateViewOp(name, select, check_option)
		return operations.invoke(op)

@Operations.register_operation('drop_view')
class DropViewOp(MigrateOperation):
	"""
	Drop SQL view.
	"""
	def __init__(self, name, select, check_option=False):
		self.name = name
		self.select = select
		self.check_option = check_option

	def reverse(self):
		return CreateViewOp(self.name, self.select, self.check_option)

	@classmethod
	def drop_view(cls, operations, name, select, check_option=False):
		"""
		Issue "DROP VIEW" DDL command.
		"""
		op = DropViewOp(name, select, check_option)
		return operations.invoke(op)

@Operations.implementation_for(SetTableCommentOp)
def _set_table_comment(operations, op):
	operations.execute(SetTableComment(op.table, op.comment))

@renderers.dispatch_for(SetTableCommentOp)
def _render_set_table_comment(context, op):
	return 'op.set_table_comment(%r, %r)' % (op.table, op.comment)

@Operations.implementation_for(CreateTriggerOp)
def _create_trigger(operations, op):
	operations.execute(CreateTrigger(
		op.table,
		Trigger(op.when, op.action, op.name),
		module=op.module,
		migration=op.migration
	))

@renderers.dispatch_for(CreateTriggerOp)
def _render_create_trigger(context, op):
	if op.migration:
		attrs = context.migration_context.config.attributes
		new_rev_id = _get_new_rev(context)
		if new_rev_id:
			new_sqltpl_revision(
				attrs.get('mm'),
				context.dialect,
				op.module,
				'triggers',
				op.name,
				op.migration
			)
	return 'op.create_trigger(%r, %r, %r, %r, %r)' % (
		op.module,
		op.table,
		op.when,
		op.action,
		op.migration
	)

@Operations.implementation_for(DropTriggerOp)
def _drop_trigger(operations, op):
	operations.execute(DropTrigger(
		op.table,
		Trigger(op.when, op.action, op.name),
		module=op.module
	))

@renderers.dispatch_for(DropTriggerOp)
def _render_drop_trigger(context, op):
	return 'op.drop_trigger(%r, %r, %r, %r, %r)' % (
		op.module,
		op.table,
		op.when,
		op.action,
		op.migration
	)

@Operations.implementation_for(CreateFunctionOp)
def _create_function(operations, op):
	operations.execute(CreateFunction(
		op.func,
		op.module,
		migration=op.migration
	))

@renderers.dispatch_for(CreateFunctionOp)
def _render_create_function(context, op):
	context.imports.add('from netprofile.db import ddl as npd')
	if op.migration:
		attrs = context.migration_context.config.attributes
		new_rev_id = _get_new_rev(context)
		if new_rev_id:
			new_sqltpl_revision(
				attrs.get('mm'),
				context.dialect,
				op.module,
				'functions',
				op.func.name,
				op.migration
			)
	return 'op.create_function(%r, %s, %r)' % (
		op.module,
		op.func._autogen_repr(context),
		op.migration
	)

@Operations.implementation_for(DropFunctionOp)
def _drop_function(operations, op):
	operations.execute(DropFunction(op.func))

@renderers.dispatch_for(DropFunctionOp)
def _render_drop_function(context, op):
	context.imports.add('from netprofile.db import ddl as npd')
	return 'op.drop_function(%r, %s, %r)' % (
		op.module,
		op.func._autogen_repr(context),
		op.migration
	)

@Operations.implementation_for(CreateEventOp)
def _create_event(operations, op):
	operations.execute(CreateEvent(op.event, op.module))

@renderers.dispatch_for(CreateEventOp)
def _render_create_event(context, op):
	context.imports.add('from netprofile.db import ddl as npd')
	if op.migration:
		attrs = context.migration_context.config.attributes
		new_rev_id = _get_new_rev(context)
		if new_rev_id:
			new_sqltpl_revision(
				attrs.get('mm'),
				context.dialect,
				op.module,
				'events',
				op.event.name,
				op.migration
			)
	return 'op.create_event(%r, npd.%r, %r)' % (
		op.module,
		op.event,
		op.migration
	)

@Operations.implementation_for(DropEventOp)
def _drop_event(operations, op):
	operations.execute(DropEvent(op.event))

@renderers.dispatch_for(DropEventOp)
def _render_drop_event(context, op):
	context.imports.add('from netprofile.db import ddl as npd')
	return 'op.drop_event(%r, npd.%r, %r)' % (
		op.module,
		op.event,
		op.migration
	)

@Operations.implementation_for(CreateViewOp)
def _create_view(operations, op):
	operations.execute(CreateView(op.name, op.select, op.check_option))

@renderers.dispatch_for(CreateViewOp)
def _render_create_view(context, op):
	return 'op.create_view(%r, %r, check_option=%r)' % (
		op.name,
		render_variants(op.select),
		op.check_option
	)

@Operations.implementation_for(DropViewOp)
def _drop_view(operations, op):
	operations.execute(DropView(op.name))

@renderers.dispatch_for(DropViewOp)
def _render_drop_view(context, op):
	return 'op.drop_view(%r, %r, check_option=%r)' % (
		op.name,
		render_variants(op.select),
		op.check_option
	)

@comparators.dispatch_for('schema')
def _compare_dbobjects(context, ops, schemas):
	# XXX: this will only add new routines/events to DB.
	#      Deletion, modification, renaming etc. is not detected.
	mctx = context.migration_context
	script = mctx.script
	attrs = mctx.config.attributes
	dialect = context.dialect
	mm = attrs.get('mm')
	moddef_filter = attrs.get('module')
	new_rev_id = _get_new_rev(context)

	meta_funcs = dict((func.name, func) for func in context.metadata.info.get('functions', set()))
	insp_funcs = set()

	meta_events = dict((evt.name, evt) for evt in context.metadata.info.get('events', set()))
	insp_events = set()

	meta_views = dict((view.name, view) for view in context.metadata.info.get('views', set()))
	insp_views = set()

	if _is_mysql(dialect):
		for sch in schemas:
			res = context.connection.execute(
				'SELECT ROUTINE_NAME'
				' FROM information_schema.ROUTINES'
				' WHERE ROUTINE_SCHEMA = %(schema_name)s',
				schema_name=dialect.default_schema_name if sch is None else sch
			)
			for row in res:
				insp_funcs.add(row[0])

			res = context.connection.execute(
				'SELECT EVENT_NAME'
				' FROM information_schema.EVENTS'
				' WHERE EVENT_SCHEMA = %(schema_name)s',
				schema_name=dialect.default_schema_name if sch is None else sch
			)
			for row in res:
				insp_events.add(row[0])

			res = context.connection.execute(
				'SELECT TABLE_NAME'
				' FROM information_schema.VIEWS'
				' WHERE TABLE_SCHEMA = %(schema_name)s',
				schema_name=dialect.default_schema_name if sch is None else sch
			)
			for row in res:
				insp_views.add(row[0])
	else:
		# Catch-all for unsupported dialects
		meta_funcs = dict()
		meta_events = dict()
		meta_views = dict()

	for fname in set(meta_funcs) - insp_funcs:
		func = meta_funcs[fname]
		if moddef_filter and (func.__moddef__ != moddef_filter):
			continue
		ops.ops.append(CreateFunctionOp(func.__moddef__, func, new_rev_id))

	for fname in set(meta_funcs).intersection(insp_funcs):
		func = meta_funcs[fname]
		moddef = func.__moddef__
		if moddef_filter and (moddef != moddef_filter):
			continue
		revs = get_sqltpl_revisions(mm, dialect, moddef, 'functions', fname)
		prev_rev_id = _find_newest_rev(script, moddef, revs)
		if prev_rev_id and diff_sqltpl(mm, dialect, moddef, 'functions', fname, prev_rev_id):
			ops.ops.extend((
				DropFunctionOp(func.__moddef__, func, prev_rev_id),
				CreateFunctionOp(func.__moddef__, func, new_rev_id)
			))

	for ename in set(meta_events) - insp_events:
		evt = meta_events[ename]
		if moddef_filter and (evt.__moddef__ != moddef_filter):
			continue
		ops.ops.append(CreateEventOp(evt.__moddef__, evt, new_rev_id))

	for ename in set(meta_events).intersection(insp_events):
		evt = meta_events[ename]
		moddef = evt.__moddef__
		if moddef_filter and (moddef != moddef_filter):
			continue
		revs = get_sqltpl_revisions(mm, dialect, moddef, 'events', ename)
		prev_rev_id = _find_newest_rev(script, moddef, revs)
		if prev_rev_id and diff_sqltpl(mm, dialect, moddef, 'events', ename, prev_rev_id):
			ops.ops.extend((
				DropEventOp(evt.__moddef__, evt, prev_rev_id),
				CreateEventOp(evt.__moddef__, evt, new_rev_id)
			))

	for vname in set(meta_views) - insp_views:
		view = meta_views[vname]
		if moddef_filter and (view.__moddef__ != moddef_filter):
			continue
		ops.ops.append(CreateViewOp(view.name, view.select, view.check))

