#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: NPDML parser
# © Copyright 2017 Alex 'Unik' Unigovsky
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

__all__ = (
	'NPDMLContext',
	'NPDMLBlock',
	'NPDMLDocumentContext',
	'NPDMLPageContext',
	'NPDMLTitleContext',
	'NPDMLHeadingContext',
	'NPDMLSectionContext',
	'NPDMLParagraphContext',
	'NPDMLTableContext',
	'NPDMLTableCaptionContext',
	'NPDMLTableHeaderContext',
	'NPDMLTableRowContext',
	'NPDMLTableCellContext',
	'NPDMLAnchorContext',
	'NPDMLBoldContext',
	'NPDMLItalicContext',
	'NPDMLUnderlineContext',
	'NPDMLStrikethroughContext',
	'NPDMLSuperscriptContext',
	'NPDMLSubscriptContext',
	'NPDMLFontContext',
	'NPDMLParseTarget'
)

from lxml import etree

from netprofile.tpl import TemplateObject

class NPDMLContext(dict):
	def __init__(self, *args, **kwargs):
		dict.__init__(self, *args, **kwargs)
		self.data = []
		self.counter = 0

	def get_data(self):
		return ''.join(self.data)

	def get_counter(self):
		self.counter += 1
		return self.counter

class NPDMLBlock(object):
	pass

class NPDMLDocumentContext(NPDMLContext):
	pass

class NPDMLPageContext(NPDMLContext):
	pass

class NPDMLTitleContext(NPDMLContext):
	pass

class NPDMLHeadingContext(NPDMLContext):
	pass

class NPDMLSectionContext(NPDMLContext, NPDMLBlock):
	pass

class NPDMLParagraphContext(NPDMLContext, NPDMLBlock):
	pass

class NPDMLTableContext(NPDMLContext, NPDMLBlock):
	def __init__(self, *args, **kwargs):
		NPDMLContext.__init__(self, *args, **kwargs)
		self.rows = []
		self.widths = None
		self.caption = None

class NPDMLTableCaptionContext(NPDMLContext):
	pass

class NPDMLTableRowContext(NPDMLContext):
	def __init__(self, *args, **kwargs):
		NPDMLContext.__init__(self, *args, **kwargs)
		self.cells = []
		self.widths = []

class NPDMLTableHeaderContext(NPDMLTableRowContext):
	pass

class NPDMLTableCellContext(NPDMLContext):
	pass

class NPDMLAnchorContext(NPDMLContext):
	pass

class NPDMLBoldContext(NPDMLContext):
	pass

class NPDMLItalicContext(NPDMLContext):
	pass

class NPDMLUnderlineContext(NPDMLContext):
	pass

class NPDMLStrikethroughContext(NPDMLContext):
	pass

class NPDMLSuperscriptContext(NPDMLContext):
	pass

class NPDMLSubscriptContext(NPDMLContext):
	pass

class NPDMLFontContext(NPDMLContext):
	pass

_NPDML_CLASS_MAP = {
	'{http://netprofile.ru/schemas/npdml/1.0}document' : NPDMLDocumentContext,
	'{http://netprofile.ru/schemas/npdml/1.0}page'     : NPDMLPageContext,
	'{http://netprofile.ru/schemas/npdml/1.0}title'    : NPDMLTitleContext,
	'{http://netprofile.ru/schemas/npdml/1.0}heading'  : NPDMLHeadingContext,
	'{http://netprofile.ru/schemas/npdml/1.0}section'  : NPDMLSectionContext,
	'{http://netprofile.ru/schemas/npdml/1.0}para'     : NPDMLParagraphContext,
	'{http://netprofile.ru/schemas/npdml/1.0}table'    : NPDMLTableContext,
	'{http://netprofile.ru/schemas/npdml/1.0}caption'  : NPDMLTableCaptionContext,
	'{http://netprofile.ru/schemas/npdml/1.0}hrow'     : NPDMLTableHeaderContext,
	'{http://netprofile.ru/schemas/npdml/1.0}row'      : NPDMLTableRowContext,
	'{http://netprofile.ru/schemas/npdml/1.0}cell'     : NPDMLTableCellContext,
	'{http://netprofile.ru/schemas/npdml/1.0}a'        : NPDMLAnchorContext,
	'{http://netprofile.ru/schemas/npdml/1.0}b'        : NPDMLBoldContext,
	'{http://netprofile.ru/schemas/npdml/1.0}i'        : NPDMLItalicContext,
	'{http://netprofile.ru/schemas/npdml/1.0}u'        : NPDMLUnderlineContext,
	'{http://netprofile.ru/schemas/npdml/1.0}strike'   : NPDMLStrikethroughContext,
	'{http://netprofile.ru/schemas/npdml/1.0}super'    : NPDMLSuperscriptContext,
	'{http://netprofile.ru/schemas/npdml/1.0}sub'      : NPDMLSubscriptContext,
	'{http://netprofile.ru/schemas/npdml/1.0}font'     : NPDMLFontContext
}

class NPDMLParseTarget(object):
	def __init__(self):
		self.ctx = []

	def start(self, tag, attrs):
		newctx = _NPDML_CLASS_MAP[tag](attrs)
		self.ctx.append(newctx)
		return newctx

	def end(self, tag):
		return self.ctx.pop()

	def data(self, data):
		self.parent.data.append(data)

	def comment(self, text):
		pass

	def close(self):
		pass

	@property
	def parent(self):
		try:
			return self.ctx[-1]
		except IndexError:
			return None

