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

from alembic.operations import (
	MigrateOperation,
	Operations
)

@Operations.register_operation('create_trigger')
class CreateTriggerOp(MigrateOperation):
	"""
	Create a trigger on a table.
	"""
	def __init__(self, module, table, when, action):
		self.module = module
		self.table = table
		self.when = when
		self.action = action
		self.name = 't_%s_%s%s' % (table, when[0].lower(), action[0].lower())

	def reverse(self):
		return DropTriggerOp(self.module, self.table, self.when, self.action)

	@classmethod
	def create_trigger(cls, operations, module, table, when, action, **kwargs):
		"""
		Issue "CREATE TRIGGER" DDL command.
		"""
		op = CreateTriggerOp(module, table, when, action, **kwargs)
		return operations.invoke(op)

@Operations.register_operation('drop_trigger')
class DropTriggerOp(MigrateOperation):
	"""
	Drop table trigger.
	"""
	def __init__(self, module, table, when, action):
		self.module = module
		self.table = table
		self.when = when
		self.action = action
		self.name = 't_%s_%s%s' % (table, when[0].lower(), action[0].lower())

	def reverse(self):
		return CreateTriggerOp(self.module, self.table, self.when, self.action)

	@classmethod
	def drop_trigger(cls, operations, module, table, when, action, **kwargs):
		"""
		Issue "DROP TRIGGER" DDL command.
		"""
		op = DropTriggerOp(module, table, when, action, **kwargs)
		return operations.invoke(op)

@Operations.implementation_for(CreateTriggerOp)
def create_trigger(operations, op):
	pass

@Operations.implementation_for(DropTriggerOp)
def drop_trigger(operations, op):
	pass

