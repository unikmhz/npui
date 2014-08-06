#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Various helper functions
# © Copyright 2014 Alex 'Unik' Unigovsky
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

import re

_booleans = frozenset(('t', 'f', 'true', 'false', 'yes', 'no', 'on', 'off'))
_booleans_true = frozenset(('t', 'true', 'yes', 'on'))
_nulls = frozenset(('null', 'NULL', 'None'))

def value_from_config(v):
	if not isinstance(v, str):
		return v
	v = v.strip()
	if re.match(r'^[-+]?\d+$', v):
		return int(v)
	vl = v.lower()
	if vl in _booleans:
		return vl in _booleans_true
	if v in _nulls:
		return None
	return v

def make_config_dict(d, prefix='netprofile.'):
	res = dict()
	for key in d:
		if not key.startswith(prefix):
			continue
		nkey = key[len(prefix):]
		if not len(nkey):
			continue
		res[nkey] = value_from_config(d[key])
	return res

def as_dict(d):
	ret = dict()
	for key in d:
		key_first, key_rest = key.split('.', 1)
		if key_first not in ret:
			ret[key_first] = dict()
		ret[key_first][key_rest] = value_from_config(d[key])
	return ret

