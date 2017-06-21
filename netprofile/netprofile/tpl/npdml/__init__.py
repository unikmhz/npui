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
	'NPDMLMetadataContext',
	'NPDMLPageTemplateContext',
	'NPDMLPageContext',
	'NPDMLFrameContext',
	'NPDMLTitleContext',
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
	'NPDMLImageContext',
	'NPDMLCanvasContext',
	'NPDMLLabelContext',
	'NPDMLLineContext',
	'NPDMLRectangleContext',
	'NPDMLCircleContext',
	'NPDMLEllipseContext',
	'NPDMLParseTarget'
)

class NPDMLContext(dict):
	def __init__(self, *args, **kwargs):
		dict.__init__(self, *args, **kwargs)
		self.data = []

	def get_data(self):
		return ' '.join(self.data)

class NPDMLBlock(object):
	in_toc = False
	_depth = 0
	_own_counter = 0
	_counter = 0
	_indenter = None

	@property
	def is_numbered(self):
		if 'prefix' in self:
			return 1
		return 0

	@property
	def depth(self):
		return self._depth

	def get_counter(self):
		self._counter += 1
		return self._counter

class NPDMLDocumentContext(NPDMLContext, NPDMLBlock):
	is_numbered = False

class NPDMLMetadataContext(NPDMLContext):
	pass

class NPDMLPageTemplateContext(NPDMLContext):
	pass

class NPDMLFrameContext(NPDMLContext):
	pass

class NPDMLPageContext(NPDMLContext):
	pass

class NPDMLTitleContext(NPDMLContext):
	pass

class NPDMLSectionContext(NPDMLContext, NPDMLBlock):
	@property
	def in_toc(self):
		return self.get('toc') != 'ignore'

class NPDMLParagraphContext(NPDMLContext, NPDMLBlock):
	pass

class NPDMLTableContext(NPDMLContext, NPDMLBlock):
	def __init__(self, *args, **kwargs):
		NPDMLContext.__init__(self, *args, **kwargs)
		self.has_header = False
		self.rows = []
		self.widths = []
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

class NPDMLImageContext(NPDMLContext):
	pass

class NPDMLCanvasContext(NPDMLContext):
	pass

class NPDMLLabelContext(NPDMLContext):
	pass

class NPDMLLineContext(NPDMLContext):
	pass

class NPDMLRectangleContext(NPDMLContext):
	pass

class NPDMLCircleContext(NPDMLContext):
	pass

class NPDMLEllipseContext(NPDMLContext):
	pass

def _tag(name):
	return '{http://netprofile.ru/schemas/npdml/1.0}' + name

_NPDML_CLASS_MAP = {
	_tag('document'): NPDMLDocumentContext,
	_tag('meta'): NPDMLMetadataContext,
	_tag('pageTemplates'): NPDMLPageTemplateContext,
	_tag('page'): NPDMLPageContext,
	_tag('frame'): NPDMLFrameContext,
	_tag('title'): NPDMLTitleContext,
	_tag('section'): NPDMLSectionContext,
	_tag('para'): NPDMLParagraphContext,
	_tag('table'): NPDMLTableContext,
	_tag('caption'): NPDMLTableCaptionContext,
	_tag('hrow'): NPDMLTableHeaderContext,
	_tag('row'): NPDMLTableRowContext,
	_tag('cell'): NPDMLTableCellContext,
	_tag('a'): NPDMLAnchorContext,
	_tag('b'): NPDMLBoldContext,
	_tag('i'): NPDMLItalicContext,
	_tag('u'): NPDMLUnderlineContext,
	_tag('strike'): NPDMLStrikethroughContext,
	_tag('super'): NPDMLSuperscriptContext,
	_tag('sub'): NPDMLSubscriptContext,
	_tag('font'): NPDMLFontContext,
	_tag('image'): NPDMLImageContext,
	_tag('canvas'): NPDMLCanvasContext,
	_tag('label'): NPDMLLabelContext,
	_tag('line'): NPDMLLineContext,
	_tag('rect'): NPDMLRectangleContext,
	_tag('circle'): NPDMLCircleContext,
	_tag('ellipse'): NPDMLEllipseContext
}

class NPDMLParseTarget(object):
	def __init__(self):
		self.ctx = []

	def start(self, tag, attrs):
		newctx = _NPDML_CLASS_MAP[tag](attrs)

		if isinstance(newctx, NPDMLBlock):
			parent = self.get_parent_block()
			if parent is not None:
				newctx._depth = parent._depth + 1
				if newctx.is_numbered:
					newctx._own_counter = parent.get_counter()

		self.ctx.append(newctx)
		return newctx

	def end(self, tag):
		return self.ctx.pop()

	def data(self, data):
		self.parent.data.append(data.strip())

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

	def get_counters(self, last=None):
		for ctx in self.ctx:
			if isinstance(ctx, NPDMLBlock) and ctx._own_counter > 0:
				yield ctx._own_counter
		if isinstance(last, NPDMLBlock) and last._own_counter > 0:
			yield last._own_counter

	def get_section_id(self):
		return 'sect-%s' % ('-'.join(str(x) for x in self.get_counters()),)

	def get_parent_block(self, ignore=None):
		for ctx in reversed(self.ctx):
			if ctx is ignore:
				continue
			if isinstance(ctx, NPDMLBlock):
				return ctx

