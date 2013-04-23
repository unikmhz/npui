#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
	'IDAVNode',
	'IDAVCollection',
	'IDAVFile',
	'IDAVPrincipal',
	'IDAVManager'
]

from zope.interface import Interface

class IDAVNode(Interface):
	"""
	Generic DAV node interface.
	"""
	pass

class IDAVCollection(IDAVNode):
	"""
	DAV collection interface.
	"""
	pass

class IDAVFile(IDAVNode):
	"""
	DAV file object interface.
	"""
	pass

class IDAVPrincipal(IDAVNode):
	"""
	DAV principal object interface.
	"""
	pass

class IDAVManager(Interface):
	"""
	DAV management utility class.
	"""
	pass

