#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Enum column implementation for Python 2
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

from weakref import WeakSet
from sqlalchemy.sql import expression


class EnumSymbol(expression.ClauseElement):
    """
    Define a fixed symbol tied to a parent class.
    """
    def __init__(self, cls_, name, value, description, order=0):
        self.cls_ = cls_
        self.name = name
        self.value = value
        self.description = description
        self.order = order

    def __reduce__(self):
        """
        Allow unpickling to return the symbol linked to the DeclEnum class.
        """
        return getattr, (self.cls_, self.name)

    def __iter__(self):
        return iter([self.value, self.description])

    def __repr__(self):
        return '<%s>' % self.name

    def __json__(self, req=None):
        return self.value


# FIXME: fix symbol order
class EnumMeta(type):
    """
    Generate new DeclEnum classes.
    """
    def __init__(cls, classname, bases, dict_):
        cls._reg = reg = cls._reg.copy()
        cls._dbf = cls._dbf.copy()

        for k, v in dict_.items():
            if isinstance(v, tuple):
                sym = reg[v[0]] = EnumSymbol(cls, k, *v)
                setattr(cls, k, sym)
        return type.__init__(cls, classname, bases, dict_)

    def __iter__(cls):
        return iter(cls._reg.values())

    def add_symbol(cls, k, v):
        if isinstance(v, tuple):
            sym = cls._reg[v[0]] = EnumSymbol(cls, k, *v)
            setattr(cls, k, sym)
            for dbt in cls._dbf:
                dbt.update_impl()


class DeclEnum(object):
    """
    Declarative enumeration.
    """
    __metaclass__ = EnumMeta
    _reg = {}
    _dbf = WeakSet()

    @classmethod
    def from_string(cls, value):
        try:
            return cls._reg[value]
        except KeyError:
            raise ValueError('Invalid value for %r: %r' %
                             (cls.__name__, value))

    @classmethod
    def values(cls):
        return sorted(cls._reg, key=lambda k: cls._reg[k].order)

    @classmethod
    def db_type(cls):
        from netprofile.db.fields import DeclEnumType
        t = DeclEnumType(cls)
        cls._dbf.add(t)
        return t
