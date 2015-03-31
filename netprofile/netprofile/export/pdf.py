#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Data export support for PDF files
# © Copyright 2015 Alex 'Unik' Unigovsky
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

import datetime
import io
import urllib

from netprofile import PY3
from netprofile.ext.columns import PseudoColumn
from netprofile.export import ExportFormat
from netprofile.pdf import (
	DefaultDocTemplate,
	PAGE_ORIENTATIONS,
	PAGE_SIZES,
	TABLE_STYLE_DEFAULT
)
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)
from pyramid.response import Response
from reportlab.platypus import (
	Paragraph,
	LongTable
)
from reportlab.lib.units import (
	cm,
	inch
)
from babel.dates import format_datetime

_ = TranslationStringFactory('netprofile')

class PDFExportFormat(ExportFormat):
	"""
	Export data as PDF files.
	"""
	@property
	def name(self):
		return _('PDF')

	@property
	def icon(self):
		return 'ico-pdf'

	def enabled(self, req):
		if req.pdf_styles is None:
			return False
		return True

	def options(self, req, name):
		loc = get_localizer(req)
		return ({
			'name'           : 'pdf_pagesz',
			'fieldLabel'     : loc.translate(_('Page size')),
			'xtype'          : 'combobox',
			'displayField'   : 'value',
			'valueField'     : 'id',
			'format'         : 'string',
			'queryMode'      : 'local',
			'grow'           : True,
			'shrinkWrap'     : True,
			'value'          : 'a4',
			'allowBlank'     : False,
			'forceSelection' : True,
			'editable'       : False,
			'store'          : {
				'xtype'   : 'simplestore',
				'sorters' : [{ 'property' : 'value', 'direction' : 'ASC' }],
				'fields'  : ('id', 'value'),
				'data'    : tuple({ 'id' : k, 'value' : v[0] } for k, v in PAGE_SIZES.items())
			}
		}, {
			'name'           : 'pdf_orient',
			'fieldLabel'     : loc.translate(_('Orientation')),
			'xtype'          : 'combobox',
			'displayField'   : 'value',
			'valueField'     : 'id',
			'format'         : 'string',
			'queryMode'      : 'local',
			'grow'           : True,
			'shrinkWrap'     : True,
			'value'          : 'portrait',
			'allowBlank'     : False,
			'forceSelection' : True,
			'editable'       : False,
			'store'          : {
				'xtype'   : 'simplestore',
				'sorters' : [{ 'property' : 'value', 'direction' : 'ASC' }],
				'fields'  : ('id', 'value'),
				'data'    : tuple({ 'id' : k, 'value' : loc.translate(v[0]) } for k, v in PAGE_ORIENTATIONS.items())
			}
		}, {
			'name'           : 'pdf_hmargins',
			'fieldLabel'     : loc.translate(_('Horizontal Margins')),
			'xtype'          : 'numberfield',
			'allowBlank'     : False,
			'autoStripChars' : True,
			'minValue'       : 0.0,
			'step'           : 0.2,
			'value'          : 1.8
		}, {
			'name'           : 'pdf_vmargins',
			'fieldLabel'     : loc.translate(_('Vertical Margins')),
			'xtype'          : 'numberfield',
			'allowBlank'     : False,
			'autoStripChars' : True,
			'minValue'       : 0.0,
			'step'           : 0.2,
			'value'          : 2.0
		})

	def export(self, extm, params, req):
		pdf_pagesz = params.pop('pdf_pagesz', 'a4')
		pdf_orient = params.pop('pdf_orient', 'portrait')
		try:
			pdf_hmargins = float(params.pop('pdf_hmargins', 1.8))
		except ValueError:
			pdf_hmargins = 1.8
		try:
			pdf_vmargins = float(params.pop('pdf_vmargins', 2.0))
		except ValueError:
			pdf_vmargins = 2.0
		fields = []
		flddef = []
		col_widths = []
		col_flexes = []
		total_width = 0
		total_flex = 0
		for field in extm.export_view:
			if isinstance(field, PseudoColumn):
				fld = field
				field = fld.name
			else:
				fld = extm.get_column(field)
			fields.append(field)
			flddef.append(fld)
			width = fld.column_width
			flex = fld.column_flex

			if not width:
				width = fld.pixels
			if not width:
				width = 200
			width = width / 200 * inch
			col_widths.append(width)

			if flex:
				col_flexes.append(flex)
				total_flex += flex
			else:
				col_flexes.append(None)
				total_width += width

		if pdf_pagesz not in PAGE_SIZES:
			raise ValueError('Unknown page size specified')
		if pdf_orient not in ('portrait', 'landscape'):
			raise ValueError('Unknown page orientation specified')
		res = Response()
		loc = get_localizer(req)
		now = datetime.datetime.now()
		res.last_modified = now
		res.content_type = 'application/pdf'

		res.cache_control.no_cache = True
		res.cache_control.no_store = True
		res.cache_control.private = True
		res.cache_control.must_revalidate = True
		res.headerlist.append(('X-Frame-Options', 'SAMEORIGIN'))
		if PY3:
			res.content_disposition = \
				'attachment; filename*=UTF-8\'\'%s-%s.pdf' % (
					urllib.parse.quote(loc.translate(extm.menu_name), ''),
					now.date().isoformat()
				)
		else:
			res.content_disposition = \
				'attachment; filename*=UTF-8\'\'%s-%s.pdf' % (
					urllib.quote(loc.translate(extm.menu_name).encode(), ''),
					now.date().isoformat()
				)

		for prop in ('__page', '__start', '__limit'):
			if prop in params:
				del params[prop]
		data = extm.read(params, req)['records']

		doc = DefaultDocTemplate(
			res,
			request=req,
			pagesize=pdf_pagesz,
			orientation=pdf_orient,
			topMargin=pdf_vmargins * cm,
			leftMargin=pdf_hmargins * cm,
			rightMargin=pdf_hmargins * cm,
			bottomMargin=pdf_vmargins * cm,
			title=loc.translate(_('{0}, exported at {1}')).format(
				loc.translate(extm.menu_name),
				format_datetime(now, locale=req.current_locale)
			)
		)

		total_width = doc.width - total_width - 12
		if total_flex > 0:
			width_per_flex = total_width / total_flex
		else:
			width_per_flex = 0.0
		table_widths = []
		for idx, field in enumerate(fields):
			if col_flexes[idx]:
				table_widths.append(col_flexes[idx] * width_per_flex)
			else:
				table_widths.append(col_widths[idx])

		ss = req.pdf_styles
		if ss is None:
			raise RuntimeError('PDF subsystem is not configured. See application .INI files.')
		# TODO: add custom extmodel option to specify rowHeights, as an
		# optimization measure. Otherwise reportlab takes +Inf time on huge
		# tables.
		# Crude hack: rowHeights=([0.5 * inch] * (len(data) + 1)
		table = LongTable(
			tuple(storyteller(data, fields, flddef, localizer=loc, model=extm, styles=ss)),
			colWidths=table_widths,
			repeatRows=1
		)
		table.setStyle(TABLE_STYLE_DEFAULT)
		story = [table]

		doc.build(story)
		return res

def storyteller(data, fields, flddef, localizer=None, model=None, styles=None, write_header=True):
	if model and localizer and write_header:
		yield tuple(
			Paragraph(localizer.translate(flddef[idx].header_string), styles['table_header'])
			for idx, field in enumerate(fields)
		)
	for row in data:
		pdfrow = []
		for field in fields:
			if (field not in row) or (row[field] is None):
				pdfrow.append('')
				continue
			pdfrow.append(Paragraph(str(row[field]), styles['body']))
		yield pdfrow

