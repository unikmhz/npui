#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-
#
# NetProfile: PDF-related tables, utility functions etc.
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

__all__ = (
	'PAGE_ORIENTATIONS',
	'PAGE_SIZES',
	'TABLE_STYLE_DEFAULT'
)

import logging
import os

from reportlab.lib import (
	colors,
	enums,
	pagesizes,
	styles
)
from reportlab.lib.units import (
	cm,
	inch
)
from reportlab.pdfbase import (
	pdfmetrics,
	ttfonts
)
from reportlab.platypus import (
	doctemplate,
	frames,
	tables
)
from pyramid.i18n import TranslationStringFactory

from netprofile.common.util import (
	as_dict,
	make_config_dict
)

logger = logging.getLogger(__name__)

_ = TranslationStringFactory('netprofile')

_pdfss = None

PAGE_SIZES = {
	'4a0'      : ('4A0 (DIN 476)',     (168.2 * cm, 237.8 * cm)),
	'2a0'      : ('2A0 (DIN 476)',     (118.9 * cm, 168.2 * cm)),

	'a0'       : ('A0 (ISO 216)',      pagesizes.A0),
	'a1'       : ('A1 (ISO 216)',      pagesizes.A1),
	'a2'       : ('A2 (ISO 216)',      pagesizes.A2),
	'a3'       : ('A3 (ISO 216)',      pagesizes.A3),
	'a4'       : ('A4 (ISO 216)',      pagesizes.A4),
	'a5'       : ('A5 (ISO 216)',      pagesizes.A5),
	'a6'       : ('A6 (ISO 216)',      pagesizes.A6),
	'a7'       : ('A7 (ISO 216)',      (pagesizes.A6[1] * 0.5, pagesizes.A6[0])),
	'a8'       : ('A8 (ISO 216)',      (pagesizes.A6[0] * 0.5, pagesizes.A6[1] * 0.5)),

	'b0'       : ('B0 (ISO 216)',      pagesizes.B0),
	'b1'       : ('B1 (ISO 216)',      pagesizes.B1),
	'b2'       : ('B2 (ISO 216)',      pagesizes.B2),
	'b3'       : ('B3 (ISO 216)',      pagesizes.B3),
	'b4'       : ('B4 (ISO 216)',      pagesizes.B4),
	'b5'       : ('B5 (ISO 216)',      pagesizes.B5),
	'b6'       : ('B6 (ISO 216)',      pagesizes.B6),
	'b7'       : ('B7 (ISO 216)',      (pagesizes.B6[1] * 0.5, pagesizes.B6[0])),
	'b8'       : ('B8 (ISO 216)',      (pagesizes.B6[0] * 0.5, pagesizes.B6[1] * 0.5)),

	'c0'       : ('C0 (ISO 269)',      (91.7 * cm, 129.7 * cm)),
	'c1'       : ('C1 (ISO 269)',      (64.8 * cm, 91.7 * cm)),
	'c2'       : ('C2 (ISO 269)',      (45.8 * cm, 64.8 * cm)),
	'c3'       : ('C3 (ISO 269)',      (32.4 * cm, 45.8 * cm)),
	'c4'       : ('C4 (ISO 269)',      (22.9 * cm, 32.4 * cm)),
	'c5'       : ('C5 (ISO 269)',      (16.2 * cm, 22.9 * cm)),
	'c6'       : ('C6 (ISO 269)',      (11.4 * cm, 16.2 * cm)),
	'c7'       : ('C7 (ISO 269)',      (8.1 * cm, 11.4 * cm)),
	'c8'       : ('C8 (ISO 269)',      (5.7 * cm, 8.1 * cm)),

	'e5'       : ('E5 (SS 014711)',    (15.5 * cm, 22 * cm)),
	'g5'       : ('G5 (SS 014711)',    (16.9 * cm, 23.9 * cm)),
	'f4'       : ('F4',                (21 * cm, 33 * cm)),
	'a3p'      : ('A3+',               (32.9 * cm, 48.3 * cm)),

	'dl'       : ('DL (ISO 269)',      (9.9 * cm, 21 * cm)),
	'dle'      : ('DLE (ISO 269)',     (11 * cm, 22 * cm)),
	'e4'       : ('E4 (ISO 269)',      (28 * cm, 40 * cm)),
	'c6c5'     : ('C6/C5 (ISO 269)',   (11.4 * cm, 22.9 * cm)),

	'jb0'      : ('JIS B0',            (103 * cm, 145.6 * cm)),
	'jb1'      : ('JIS B1',            (72.8 * cm, 103 * cm)),
	'jb2'      : ('JIS B2',            (51.5 * cm, 72.8 * cm)),
	'jb3'      : ('JIS B3',            (36.4 * cm, 51.5 * cm)),
	'jb4'      : ('JIS B4',            (25.7 * cm, 36.4 * cm)),
	'jb5'      : ('JIS B5',            (18.2 * cm, 25.7 * cm)),
	'jb6'      : ('JIS B6',            (12.8 * cm, 18.2 * cm)),
	'jb7'      : ('JIS B7',            (9.1 * cm, 12.8 * cm)),
	'jb8'      : ('JIS B8',            (6.4 * cm, 9.1 * cm)),

	'letter'   : ('Letter (ANSI A)',   pagesizes.LETTER),
	'h_letter' : ('Half Letter',       (pagesizes.LETTER[1] * 0.5, pagesizes.LETTER[0])),
	'exec'     : ('Executive',         (7 * inch, 10 * inch)),
	'g_letter' : ('Government-Letter', (8 * inch, 10.5 * inch)),
	'legal'    : ('Legal',             pagesizes.LEGAL),
	'j_legal'  : ('Junior Legal',      (5 * inch, 8 * inch)),
	'11by17'   : ('Tabloid (ANSI B)',  pagesizes.ELEVENSEVENTEEN),
	'ansi_c'   : ('ANSI C',            (17 * inch, 22 * inch)),
	'ansi_d'   : ('ANSI D',            (22 * inch, 34 * inch)),
	'ansi_e'   : ('ANSI E',            (34 * inch, 44 * inch)),

	'p1'       : ('P1 (CAN 2-9.60M)',  (56 * cm, 86 * cm)),
	'p2'       : ('P2 (CAN 2-9.60M)',  (43 * cm, 56 * cm)),
	'p3'       : ('P3 (CAN 2-9.60M)',  (28 * cm, 43 * cm)),
	'p4'       : ('P4 (CAN 2-9.60M)',  (21.5 * cm, 28 * cm)),
	'p5'       : ('P5 (CAN 2-9.60M)',  (14 * cm, 21.5 * cm)),
	'p6'       : ('P6 (CAN 2-9.60M)',  (10.7 * cm, 14 * cm)),

	'pli1'     : ('Pliego',            (70 * cm, 100 * cm)),
	'pli2'     : ('½ pliego',          (50 * cm, 70 * cm)),
	'pli4'     : ('¼ pliego',          (35 * cm, 50 * cm)),
	'pli8'     : ('⅛ pliego',          (25 * cm, 35 * cm)),
	'carta'    : ('Carta',             (21.6 * cm, 27.9 * cm)),
	'oficio'   : ('Oficio',            (21.6 * cm, 33 * cm)),
	'exttab'   : ('Extra Tabloide',    (30.48 * cm, 45.72 * cm))
}

PAGE_ORIENTATIONS = {
	'portrait'  : (_('Portrait'),  pagesizes.portrait),
	'landscape' : (_('Landscape'), pagesizes.landscape)
}

TABLE_STYLE_DEFAULT = tables.TableStyle((
	('GRID',           (0, 0),  (-1, -1), 0.2, colors.dimgrey),
	('TEXTCOLOR',      (0, 0),  (-1, 0),  colors.black),
	('BACKGROUND',     (0, 0),  (-1, 0),  colors.HexColor(0xe6e6e6)),
	('ROWBACKGROUNDS', (0, 1),  (-1, -1), (colors.white, colors.HexColor(0xf5f5f5)))
))

class DefaultDocTemplate(doctemplate.BaseDocTemplate):
	def __init__(self, filename, **kwargs):
		pgsz = kwargs.pop('pagesize', 'a4')
		if pgsz in PAGE_SIZES:
			pgsz = PAGE_SIZES[pgsz][1]
		else:
			pgsz = pagesizes.A4
		orient = kwargs.pop('orientation', 'portrait')
		if orient in PAGE_ORIENTATIONS:
			pgsz = PAGE_ORIENTATIONS[orient][1](pgsz)
		kwargs['pagesize'] = pgsz
		kwargs['creator'] = 'NetProfile'
		req = kwargs.pop('request', None)
		if req:
			u = req.user
			if u:
				kwargs['author'] = (u.name_full + ' (' + u.login + ')').strip()

		super(DefaultDocTemplate, self).__init__(filename, **kwargs)

		fr_body = frames.Frame(
			self.leftMargin,
			self.bottomMargin,
			self.width,
			self.height,
			id='body'
		)
		fr_left = frames.Frame(
			self.leftMargin,
			self.bottomMargin,
			self.width / 2,
			self.height,
			rightPadding=12,
			id='left'
		)
		fr_right = frames.Frame(
			self.leftMargin + self.width / 2,
			self.bottomMargin,
			self.width / 2,
			self.height,
			leftPadding=12,
			id='right'
		)

		self.addPageTemplates((
			doctemplate.PageTemplate(id='default', pagesize=pgsz, frames=(fr_body,)), # onPage=callback
			doctemplate.PageTemplate(id='2columns', pagesize=pgsz, frames=(fr_left, fr_right))
		))

def _register_fonts(settings):
	default_fontdir = settings.get('netprofile.fonts.directory', '')
	default_family = settings.get('netprofile.fonts.default_family', 'tinos')
	fontcfg = make_config_dict(settings, 'netprofile.fonts.family.')
	fontcfg = as_dict(fontcfg)
	for fname, cfg in fontcfg.items():
		if 'normal' not in cfg:
			continue
		fname = cfg.get('name', fname)
		fontdir = cfg.get('directory', default_fontdir)
		pdfmetrics.registerFont(ttfonts.TTFont(
			fname,
			os.path.join(fontdir, cfg['normal'])
		))
		reg = { 'normal' : fname }

		if 'bold' in cfg:
			reg['bold'] = fname + '_b'
			pdfmetrics.registerFont(ttfonts.TTFont(
				reg['bold'],
				os.path.join(fontdir, cfg['bold'])
			))
		else:
			reg['bold'] = fname

		if 'italic' in cfg:
			reg['italic'] = fname + '_i'
			pdfmetrics.registerFont(ttfonts.TTFont(
				reg['italic'],
				os.path.join(fontdir, cfg['italic'])
			))
		else:
			reg['italic'] = fname

		if 'bold_italic' in cfg:
			reg['boldItalic'] = fname + '_bi'
			pdfmetrics.registerFont(ttfonts.TTFont(
				reg['boldItalic'],
				os.path.join(fontdir, cfg['bold_italic'])
			))
		else:
			reg['boldItalic'] = fname

		pdfmetrics.registerFontFamily(fname, **reg)

	if default_family in fontcfg:
		return default_family
	return 'Times-Roman'

def _add_custom_ss(ss, custom_cfg, name):
	pass

def _pdf_style_sheet(cfg):
	settings = cfg.registry.settings
	try:
		ffamily = _register_fonts(settings)
	except ttfonts.TTFError:
		logger.error('Can\'t find or register configured fonts. PDF generation will be disabled.')
		return None
	if ffamily == 'Times-Roman':
		fonts = ('Times-Roman', 'Times-Bold', 'Times-Italic', 'Times-BoldItalic')
	else:
		fonts = (ffamily, ffamily + '_b', ffamily + '_i', ffamily + '_bi')

	ss = styles.StyleSheet1()

	ss.add(styles.ParagraphStyle(
		name='default',
		fontName=fonts[0],
		fontSize=10,
		leading=12
	))
	ss.add(styles.ParagraphStyle(
		name='body',
		parent=ss['default'],
		spaceBefore=6
	))
	ss.add(styles.ParagraphStyle(
		name='bold',
		parent=ss['body'],
		fontName=fonts[1],
		alias='strong'
	))
	ss.add(styles.ParagraphStyle(
		name='italic',
		parent=ss['body'],
		fontName=fonts[2],
		alias='em'
	))
	ss.add(styles.ParagraphStyle(
		name='title',
		parent=ss['body'],
		fontName=fonts[1],
		fontSize=14
	))
	ss.add(styles.ParagraphStyle(
		name='table_header',
		parent=ss['body'],
		fontName=fonts[1],
		alias='th'
	))

	custom_ss = make_config_dict(settings, 'netprofile.pdf_styles.')
	if len(custom_ss) > 0:
		custom_ss = as_dict(custom_ss)
		for name in custom_ss:
			pass # FIXME: write this

	logger.info('Loaded preconfigured PDF fonts and styles.')
	return ss

def _get_pdfss(req):
	global _pdfss
	return _pdfss

def includeme(config):
	"""
	For inclusion by Pyramid.
	"""
	global _pdfss

	_pdfss = _pdf_style_sheet(config)
	config.add_request_method(_get_pdfss, 'pdf_styles', reify=True)

