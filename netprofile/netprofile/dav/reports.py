#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

__all__ = [
	'DAVReport',
	'DAVExpandPropertyReport'
]

from .errors import DAVNotImplementedError

class DAVReport(object):
	def __init__(self, rname, rreq):
		self.name = rname
		self.rreq = rreq

	def __call__(self, req):
		raise DAVNotImplementedError('Report %s not implemented.' % self.name)

class DAVExpandPropertyReport(DAVReport):
	pass

