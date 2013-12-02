#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Pickler classes for backwards-compatibility
# © Copyright 2013 Alex 'Unik' Unigovsky
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

import phpserialize as _phpsa
from sqlalchemy.util import pickle

class PHPPickler(object):

	@classmethod
	def dumps(cls, data, proto, *, fix_imports=True):
		return _phpsa.dumps(data)

	@classmethod
	def loads(cls, data):
		return _phpsa.loads(data)

class HybridPickler(PHPPickler):
	@classmethod
	def dumps(cls, data, proto=2, *, fix_imports=True):
		return pickle.dumps(data, proto, fix_imports=fix_imports)

	@classmethod
	def loads(cls, data):
		try:
			if isinstance(data, str):
				data = data.encode()
			return _phpsa.loads(data, decode_strings=True)
		except:
			return pickle.loads(data)

