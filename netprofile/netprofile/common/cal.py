#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Default root factory for Pyramid
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

import icalendar
from icalendar.cal import (
	Component,
	types_factory,
	component_factory
)

class Card(Component):
	name = 'VCARD'
	canonical_order = ('VERSION', 'FN', 'N', 'NICKNAME', 'EMAIL')
	required = ('VERSION', 'FN')
	singletons = ('VERSION', 'N')
	multiple = ('FN', 'EMAIL', 'NICKNAME')

component_factory['VCARD'] = Card

class vUnicode(icalendar.vText):
	def __new__(cls, value, encoding=icalendar.cal.DEFAULT_ENCODING):
		self = super(vUnicode, cls).__new__(cls, value, encoding)
		self.params['CHARSET'] = 'UTF-8'
		return self

	def __repr__(self):
		return "vUnicode('%s')" % self.to_ical()

class vEMail(icalendar.vText):
	def __new__(cls, value, encoding=icalendar.cal.DEFAULT_ENCODING):
		self = super(vEMail, cls).__new__(cls, value, encoding)
		self.params['TYPE'] = 'internet'
		return self

	def __repr__(self):
		return "vUnicode('%s')" % self.to_ical()

class vStructuredUnicode(object):
	def __init__(self, *args):
		self.struct = args
		self.params = icalendar.Parameters()
		self.params['CHARSET'] = 'UTF-8'

	def to_ical(self):
		return b';'.join(icalendar.vText(c).to_ical() for c in self.struct)

types_factory.all_types += (
	vEMail,
	vUnicode,
	vStructuredUnicode
)

