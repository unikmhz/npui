#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

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

	def json_repr(self):
		return self.value

# FIXME: fix symbol order
class EnumMeta(type):
	"""
	Generate new DeclEnum classes.
	"""
	def __init__(cls, classname, bases, dict_):
		cls._reg = reg = cls._reg.copy()

		for k, v in dict_.items():
			if isinstance(v, tuple):
				sym = reg[v[0]] = EnumSymbol(cls, k, *v)
				setattr(cls, k, sym)
		return type.__init__(cls, classname, bases, dict_)

	def __iter__(cls):
		return iter(cls._reg.values())

class DeclEnum(object, metaclass=EnumMeta):
	"""
	Declarative enumeration.
	"""
	_reg = {}

	@classmethod
	def from_string(cls, value):
		try:
			return cls._reg[value]
		except KeyError:
			raise ValueError(
				'Invalid value for %r: %r' %
				(cls.__name__, value)
			)

	@classmethod
	def values(cls):
		return sorted(cls._reg, key=lambda k: cls._reg[k].order)

	@classmethod
	def db_type(cls):
		from netprofile.db.fields import DeclEnumType
		return DeclEnumType(cls)

