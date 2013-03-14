from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

class RootFactory(object):
	"""
	Generic Pyramid root factory.
	"""
	__parent__ = None
	__name__ = None

	@property
	def __acl__(self):
		return getattr(self.req, 'acls', [])

	def __init__(self, request):
		self.req = request

