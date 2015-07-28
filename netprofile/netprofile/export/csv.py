#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: Data export support for CSV files
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

import csv
import datetime
import io
import urllib

from netprofile import PY3
from netprofile.ext.columns import PseudoColumn
from netprofile.export import ExportFormat
from pyramid.i18n import (
	TranslationStringFactory,
	get_localizer
)
from pyramid.response import Response

_ = TranslationStringFactory('netprofile')

_encodings = {
	'ascii'           : ('US-ASCII',         'US ASCII'),
	'big5'            : ('Big5',             'Big5'),
	'big5hkscs'       : ('Big5-HKSCS',       'Big5 HKSCS'),
	'cp037'           : ('IBM037',           'IBM 037'),
	'cp424'           : ('IBM424',           'IBM 424'),
	'cp437'           : ('IBM437',           'IBM 437'),
	'cp500'           : ('IBM500',           'IBM 500'),
	'cp720'           : ('IBM720',           'IBM 720'),
	'cp737'           : ('IBM737',           'IBM 737'),
	'cp775'           : ('IBM775',           'IBM 775'),
	'cp850'           : ('IBM850',           'IBM 850'),
	'cp852'           : ('IBM852',           'IBM 852'),
	'cp855'           : ('IBM855',           'IBM 855'),
	'cp856'           : ('IBM856',           'IBM 856'),
	'cp857'           : ('IBM857',           'IBM 857'),
	'cp858'           : ('IBM00858',         'IBM 858'),
	'cp860'           : ('IBM860',           'IBM 860'),
	'cp861'           : ('IBM861',           'IBM 861'),
	'cp862'           : ('IBM862',           'IBM 862'),
	'cp863'           : ('IBM863',           'IBM 863'),
	'cp864'           : ('IBM864',           'IBM 864'),
	'cp865'           : ('IBM865',           'IBM 865'),
	'cp866'           : ('IBM866',           'IBM 866'),
	'cp869'           : ('IBM869',           'IBM 869'),
	'cp874'           : ('windows-874',      'WINDOWS-874'),
	'cp875'           : ('IBM875',           'IBM 875'),
	'cp932'           : ('Windows-31J',      'WINDOWS-31J'),
	'cp949'           : ('KS_C_5601-1987',   'MS 949 / UHC'),
	'cp950'           : ('CP950',            'MS 950'),
	'cp1026'          : ('IBM1026',          'IBM 1026'),
	'cp1140'          : ('IBM01140',         'IBM 1140'),
	'cp1250'          : ('windows-1250',     'WINDOWS-1250'),
	'cp1251'          : ('windows-1251',     'WINDOWS-1251'),
	'cp1252'          : ('windows-1252',     'WINDOWS-1252'),
	'cp1253'          : ('windows-1253',     'WINDOWS-1253'),
	'cp1254'          : ('windows-1254',     'WINDOWS-1254'),
	'cp1255'          : ('windows-1255',     'WINDOWS-1255'),
	'cp1256'          : ('windows-1256',     'WINDOWS-1256'),
	'cp1257'          : ('windows-1257',     'WINDOWS-1257'),
	'cp1258'          : ('windows-1258',     'WINDOWS-1258'),
	'euc_jp'          : ('EUC-JP',           'EUC-JP'),
	'euc_jis_2004'    : ('EUC-JIS-2004',     'EUC-JIS2004'),
	'euc_jisx0213'    : ('EUC-JISX0213',     'EUC-JISX0213'),
	'euc_kr'          : ('EUC-KR',           'EUC-KR'),
	'gb2312'          : ('GB2312',           'EUC-CN GB2312'),
	'gbk'             : ('GBK',              'GBK'),
	'gb18030'         : ('GB18030',          'GB18030'),
	'hz'              : ('HZ-GB-2312',       'HZ GB2312'),
	'iso2022_jp'      : ('ISO-2022-JP',      'ISO 2022-JP'),
	'iso2022_jp_1'    : ('ISO-2022-JP-1',    'ISO 2022-JP-1'),
	'iso2022_jp_2'    : ('ISO-2022-JP-2',    'ISO 2022-JP-2'),
	'iso2022_jp_3'    : ('ISO-2022-JP-3',    'ISO 2022-JP-3'),
	'iso2022_jp_2004' : ('ISO-2022-JP-2004', 'ISO 2022-JP-2004'),
	'iso2022_jp_ext'  : ('ISO-2022-JP-EXT',  'ISO 2022-JP-EXT'),
	'iso2022_kr'      : ('ISO-2022-KR',      'ISO 2022-KR'),
	'latin_1'         : ('ISO-8859-1',       'ISO 8859-1 (Latin-1)'),
	'iso8859_2'       : ('ISO-8859-2',       'ISO 8859-2 (Latin-2)'),
	'iso8859_3'       : ('ISO-8859-3',       'ISO 8859-3 (Latin-3)'),
	'iso8859_4'       : ('ISO-8859-4',       'ISO 8859-4 (Latin-4)'),
	'iso8859_5'       : ('ISO-8859-5',       'ISO 8859-5 (Cyrillic)'),
	'iso8859_6'       : ('ISO-8859-6',       'ISO 8859-6'),
	'iso8859_7'       : ('ISO-8859-7',       'ISO 8859-7 (Greek8)'),
	'iso8859_8'       : ('ISO-8859-8',       'ISO 8859-8'),
	'iso8859_9'       : ('ISO-8859-9',       'ISO 8859-9 (Latin-5)'),
	'iso8859_10'      : ('ISO-8859-10',      'ISO 8859-10 (Latin-6)'),
	'iso8859_13'      : ('ISO-8859-13',      'ISO 8859-13 (Latin-7)'),
	'iso8859_14'      : ('ISO-8859-14',      'ISO 8859-14 (Latin-8)'),
	'iso8859_15'      : ('ISO-8859-15',      'ISO 8859-15 (Latin-9)'),
	'iso8859_16'      : ('ISO-8859-16',      'ISO 8859-16 (Latin-10)'),
	'johab'           : ('JOHAB',            'JOHAB KS X 1001'),
	'koi8_r'          : ('KOI8-R',           'KOI8-R'),
	'koi8_u'          : ('KOI8-U',           'KOI8-U'),
	'mac_cyrillic'    : ('x-mac-cyrillic',   'MacOS Cyrillic'),
	'mac_greek'       : ('x-mac-greek',      'MacOS Greek'),
	'mac_iceland'     : ('x-mac-icelandic',  'MacOS Iceland'),
	'mac_latin2'      : ('x-mac-ce',         'MacOS Latin-2'),
	'mac_roman'       : ('macintosh',        'MacOS Roman'),
	'mac_turkish'     : ('x-mac-turkish',    'MacOS Turkish'),
	'ptcp154'         : ('PTCP154',          'PTCP154'),
	'shift_jis'       : ('Shift_JIS',        'Shift JIS'),
	'shift_jis_2004'  : ('SHIFT_JIS-2004',   'Shift JIS2004'),
	'shift_jisx0213'  : ('SHIFT_JISX0213',   'Shift JISX0213'),
	'utf_7'           : ('UTF-7',            'UTF-7'),
	'utf_8'           : ('UTF-8',            'UTF-8'),
	'utf_8_sig'       : ('UTF-8',            'UTF-8 + BOM'),
	'utf_16'          : ('UTF-16',           'UTF-16'),
	'utf_16_be'       : ('UTF-16BE',         'UTF-16 BE'),
	'utf_16_le'       : ('UTF-16LE',         'UTF-16 LE'),
	'utf_32'          : ('UTF-32',           'UTF-32'),
	'utf_32_be'       : ('UTF-32BE',         'UTF-32 BE'),
	'utf_32_le'       : ('UTF-32LE',         'UTF-32 LE')
}

class CSVExportFormat(ExportFormat):
	"""
	Export data as CSV files.
	"""
	@property
	def name(self):
		return _('CSV')

	@property
	def icon(self):
		return 'ico-csv'

	def options(self, req, name):
		loc = get_localizer(req)
		return ({
			'name'           : 'csv_dialect',
			'fieldLabel'     : _('Dialect'),
			'xtype'          : 'combobox',
			'displayField'   : 'value',
			'valueField'     : 'id',
			'format'         : 'string',
			'queryMode'      : 'local',
			'grow'           : True,
			'shrinkWrap'     : True,
			'value'          : 'excel',
			'allowBlank'     : False,
			'forceSelection' : True,
			'editable'       : False,
			'store'          : {
				'xtype'   : 'simplestore',
				'sorters' : [{ 'property' : 'value', 'direction' : 'ASC' }],
				'fields'  : ('id', 'value'),
				'data'    : ({
					'id'    : 'excel',
					'value' : loc.translate(_('Excel'))
				}, {
					'id'    : 'excel-tab',
					'value' : loc.translate(_('Excel with TAB delimiters'))
				}, {
					'id'    : 'unix',
					'value' : loc.translate(_('UNIX'))
				})
			}
		}, {
			'name'           : 'csv_encoding',
			'fieldLabel'     : loc.translate(_('Encoding')),
			'xtype'          : 'combobox',
			'displayField'   : 'value',
			'valueField'     : 'id',
			'format'         : 'string',
			'queryMode'      : 'local',
			'grow'           : True,
			'shrinkWrap'     : True,
			'value'          : 'utf_8',
			'allowBlank'     : False,
			'forceSelection' : True,
			'editable'       : False,
			'store'          : {
				'xtype'   : 'simplestore',
				'sorters' : [{ 'property' : 'value', 'direction' : 'ASC' }],
				'fields'  : ('id', 'value'),
				'data'    : tuple({ 'id' : k, 'value' : v[1] } for k, v in _encodings.items())
			}
		})

	def export(self, extm, params, req):
		csv_dialect = params.pop('csv_dialect', 'excel')
		csv_encoding = params.pop('csv_encoding', 'utf_8')
		fields = []
		for field in extm.export_view:
			if isinstance(field, PseudoColumn):
				continue
			fields.append(field)

		if csv_encoding not in _encodings:
			raise ValueError('Unknown encoding specified')
		res = Response()
		loc = get_localizer(req)
		now = datetime.datetime.now()
		res.last_modified = now
		if csv_dialect in ('excel', 'excel-tab'):
			res.content_type = 'application/vnd.ms-excel'
		else:
			res.content_type = 'text/csv'
		res.charset = _encodings[csv_encoding][0]
		res.cache_control.no_cache = True
		res.cache_control.no_store = True
		res.cache_control.private = True
		res.cache_control.must_revalidate = True
		res.headerlist.append(('X-Frame-Options', 'SAMEORIGIN'))
		if PY3:
			res.content_disposition = \
				'attachment; filename*=UTF-8\'\'%s-%s.csv' % (
					urllib.parse.quote(loc.translate(extm.menu_name), ''),
					now.date().isoformat()
				)
		else:
			res.content_disposition = \
				'attachment; filename*=UTF-8\'\'%s-%s.csv' % (
					urllib.quote(loc.translate(extm.menu_name).encode(), ''),
					now.date().isoformat()
				)

		for prop in ('__page', '__start', '__limit'):
			if prop in params:
				del params[prop]
		data = extm.read(params, req)['records']

		res.app_iter = csv_generator(
			data, fields, csv_dialect,
			encoding=csv_encoding,
			localizer=loc,
			model=extm
		)
		return res

def csv_generator(data, fields, dialect, encoding='utf_8', localizer=None, model=None, batch=100, write_header=True):
	cnt = 0
	field_def = ()
	with io.StringIO() as buf:
		writer = csv.writer(buf, dialect)
		if model and localizer and write_header:
			writer.writerow(tuple(
				localizer.translate(model.get_column(field).header_string)
				for field in fields
			))
		for row in data:
			writer.writerow(tuple(row[field] for field in fields))
			cnt += 1
			if (cnt % batch) == 0:
				yield bytes(buf.getvalue(), encoding)
				buf.truncate(0)
		yield bytes(buf.getvalue(), encoding)

