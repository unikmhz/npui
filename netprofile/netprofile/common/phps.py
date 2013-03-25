#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (
	unicode_literals,
	print_function,
	absolute_import,
	division
)

import phpserialize as _phpsa
from sqlalchemy.util import pickle

class PHPPickler(object):

	@classmethod
	def dumps(cls, data):
		return _phpsa.dumps(data)

	@classmethod
	def loads(cls, data):
		return _phpsa.loads(data)

class HybridPickler(PHPPickler):
	@classmethod
	def dumps(cls, data):
		return pickle.dumps(data)

	@classmethod
	def loads(cls, data):
		try:
			if isinstance(data, str):
				data = data.encode()
			return _phpsa.loads(data, decode_strings=True)
		except:
			return pickle.loads(data)

