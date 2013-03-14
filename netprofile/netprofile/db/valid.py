from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

from sqlalchemy.orm import (
	EXT_PASS,
	MapperExtension
)

class Validator(MapperExtension):
	def __init__(self, *args):
		MapperExtension.__init__(self)

	def before_insert(self, mapper, connection, instance):
		self.validate(instance)
		return EXT_PASS

	def validate(self, instance):
		pass

	before_update = before_insert

