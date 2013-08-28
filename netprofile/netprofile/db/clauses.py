#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from sqlalchemy import DateTime
from sqlalchemy.sql.expression import (
	ClauseElement,
	Executable,
	FunctionElement
)
from sqlalchemy.ext.compiler import compiles

class SetVariable(Executable, ClauseElement):
	def __init__(self, name, value):
		self.name = name
		self.value = value

@compiles(SetVariable, 'mysql')
def visit_set_variable_mysql(element, compiler, *kw):
	if isinstance(element.value, ClauseElement):
		rvalue = compiler.process(element.value)
	else:
		rvalue = compiler.render_literal_value(element.value, None)
	return 'SET @%s := %s' % (element.name, rvalue)

@compiles(SetVariable, 'pgsql')
def visit_set_variable_pgsql(element, compiler, *kw):
	if isinstance(element.value, ClauseElement):
		rvalue = compiler.process(element.value)
	else:
		rvalue = compiler.render_literal_value(element.value, None)
	return 'SET npvar.%s = %s' % (element.name, rvalue)

@compiles(SetVariable)
def visit_set_variable_pgsql(element, compiler, *kw):
	if isinstance(element.value, ClauseElement):
		rvalue = compiler.process(element.value)
	else:
		rvalue = compiler.render_literal_value(element.value, None)
	return 'SET %s = %s' % (element.name, rvalue)

class IntervalSeconds(FunctionElement):
	type = DateTime()
	name = 'intervalseconds'

@compiles(IntervalSeconds, 'mysql')
def visit_interval_seconds_mysql(element, compiler, **kw):
	return '%s + INTERVAL %s SECOND' % (
		compiler.process(element.clauses.clauses[0]),
		compiler.process(element.clauses.clauses[1])
	)

