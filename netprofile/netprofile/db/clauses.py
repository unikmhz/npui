#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Custom clauses for SQLAlchemy
# Copyright © 2013-2017 Alex Unigovsky
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

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

from sqlalchemy import (
    DateTime,
    Numeric
)
from sqlalchemy.sql.expression import (
    ClauseElement,
    Executable,
    FunctionElement
)
from sqlalchemy.sql.elements import literal
from sqlalchemy.ext.compiler import compiles


class SetVariable(Executable, ClauseElement):
    def __init__(self, name, value):
        self.name = name
        self.value = value


@compiles(SetVariable, 'mysql')
def visit_set_variable_mysql(element, compiler, **kw):
    val = element.value
    if not isinstance(val, ClauseElement):
        val = literal(val)
    rvalue = compiler.process(val)
    return 'SET @%s := %s' % (element.name, rvalue)


@compiles(SetVariable, 'postgresql')
def visit_set_variable_pgsql(element, compiler, **kw):
    val = element.value
    if not isinstance(val, ClauseElement):
        val = literal(val)
    rvalue = compiler.process(val)
    return 'SET npvar.%s = %s' % (element.name, rvalue)


@compiles(SetVariable)
def visit_set_variable(element, compiler, **kw):
    val = element.value
    if not isinstance(val, ClauseElement):
        val = literal(val)
    rvalue = compiler.process(val)
    return 'SET %s = %s' % (element.name, rvalue)


class SetVariables(Executable, ClauseElement):
    def __init__(self, **kwargs):
        self.values = kwargs


@compiles(SetVariables, 'mysql')
def visit_set_variables_mysql(element, compiler, **kw):
    clauses = []
    for name, rvalue in element.values.items():
        if not isinstance(rvalue, ClauseElement):
            rvalue = literal(rvalue)
        rvalue = compiler.process(rvalue)
        clauses.append('@%s := %s' % (name, rvalue))
    return 'SET ' + ', '.join(clauses)


@compiles(SetVariables)
def visit_set_variables(element, compiler, **kw):
    raise NotImplementedError


class IntervalSeconds(FunctionElement):
    type = DateTime()
    name = 'intervalseconds'


@compiles(IntervalSeconds, 'mysql')
def visit_interval_seconds_mysql(element, compiler, **kw):
    return '%s + INTERVAL %s SECOND' % (
        compiler.process(element.clauses.clauses[0]),
        compiler.process(element.clauses.clauses[1]))


class Binary16ToDecimal(FunctionElement):
    type = Numeric(40, 0)
    name = 'binary16todecimal'


@compiles(Binary16ToDecimal, 'mysql')
def visit_binary16_to_decimal(element, compiler, **kw):
    proc = compiler.process(element.clauses.clauses[0])
    return ('CAST(CONV(SUBSTRING(%s FROM 1 FOR 16), 16, 10) '
            'AS DECIMAL(40)) '
            '* 18446744073709551616 '
            '+ CAST(CONV(SUBSTRING(%s FROM 17 FOR 16), 16, 10) '
            'AS DECIMAL(40))' % (proc, proc))
