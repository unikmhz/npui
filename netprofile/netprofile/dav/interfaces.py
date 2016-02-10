#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: WebDAV-related interfaces
# © Copyright 2013-2015 Alex 'Unik' Unigovsky
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

__all__ = [
	'IDAVNode',
	'IDAVCollection',
	'IDAVFile',
	'IDAVPrincipal',
	'IDAVAddressBook',
	'IDAVCard',
	'IDAVDirectory',
	'IDAVCalendar',
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

class IDAVAddressBook(IDAVNode):
	"""
	CardDAV address book collection interface.
	"""
	pass

class IDAVCard(IDAVNode):
	"""
	CardDAV address object interface.
	"""
	pass

class IDAVDirectory(IDAVNode):
	"""
	CardDAV directory extension interface.
	"""
	pass

class IDAVCalendar(IDAVNode):
	"""
	CalDAV calendar collection interface.
	"""
	pass

class IDAVManager(Interface):
	"""
	DAV management utility class.
	"""
	pass

