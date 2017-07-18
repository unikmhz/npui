#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: PDF-related tables, utility functions etc.
# Copyright © 2015-2017 Alex Unigovsky
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

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

import logging
import os
import re

from reportlab.lib import (
    colors,
    pagesizes,
    styles
)
from reportlab.lib.units import (
    cm,
    inch,
    mm,
    pica
)
from reportlab.lib.enums import (
    TA_LEFT,
    TA_CENTER,
    TA_RIGHT,
    TA_JUSTIFY
)
from reportlab.pdfbase import (
    pdfmetrics,
    ttfonts
)
from reportlab.platypus import (
    ActionFlowable,
    BaseDocTemplate,
    Flowable,
    TableStyle
)
from reportlab.graphics import shapes
from pyramid.i18n import TranslationStringFactory

from netprofile.common.util import (
    as_dict,
    make_config_dict
)

__all__ = (
    'PAGE_ORIENTATIONS',
    'PAGE_SIZES',
    'eval_length'
)

logger = logging.getLogger(__name__)

_ = TranslationStringFactory('netprofile')

_pdfss = None

PAGE_SIZES = {
    '4a0':      ('4A0 (DIN 476)',     (168.2 * cm, 237.8 * cm)),
    '2a0':      ('2A0 (DIN 476)',     (118.9 * cm, 168.2 * cm)),

    'a0':       ('A0 (ISO 216)',      pagesizes.A0),
    'a1':       ('A1 (ISO 216)',      pagesizes.A1),
    'a2':       ('A2 (ISO 216)',      pagesizes.A2),
    'a3':       ('A3 (ISO 216)',      pagesizes.A3),
    'a4':       ('A4 (ISO 216)',      pagesizes.A4),
    'a5':       ('A5 (ISO 216)',      pagesizes.A5),
    'a6':       ('A6 (ISO 216)',      pagesizes.A6),
    'a7':       ('A7 (ISO 216)',      (pagesizes.A6[1] * 0.5,
                                       pagesizes.A6[0])),
    'a8':       ('A8 (ISO 216)',      (pagesizes.A6[0] * 0.5,
                                       pagesizes.A6[1] * 0.5)),

    'b0':       ('B0 (ISO 216)',      pagesizes.B0),
    'b1':       ('B1 (ISO 216)',      pagesizes.B1),
    'b2':       ('B2 (ISO 216)',      pagesizes.B2),
    'b3':       ('B3 (ISO 216)',      pagesizes.B3),
    'b4':       ('B4 (ISO 216)',      pagesizes.B4),
    'b5':       ('B5 (ISO 216)',      pagesizes.B5),
    'b6':       ('B6 (ISO 216)',      pagesizes.B6),
    'b7':       ('B7 (ISO 216)',      (pagesizes.B6[1] * 0.5,
                                       pagesizes.B6[0])),
    'b8':       ('B8 (ISO 216)',      (pagesizes.B6[0] * 0.5,
                                       pagesizes.B6[1] * 0.5)),

    'c0':       ('C0 (ISO 269)',      (91.7 * cm, 129.7 * cm)),
    'c1':       ('C1 (ISO 269)',      (64.8 * cm, 91.7 * cm)),
    'c2':       ('C2 (ISO 269)',      (45.8 * cm, 64.8 * cm)),
    'c3':       ('C3 (ISO 269)',      (32.4 * cm, 45.8 * cm)),
    'c4':       ('C4 (ISO 269)',      (22.9 * cm, 32.4 * cm)),
    'c5':       ('C5 (ISO 269)',      (16.2 * cm, 22.9 * cm)),
    'c6':       ('C6 (ISO 269)',      (11.4 * cm, 16.2 * cm)),
    'c7':       ('C7 (ISO 269)',      (8.1 * cm, 11.4 * cm)),
    'c8':       ('C8 (ISO 269)',      (5.7 * cm, 8.1 * cm)),

    'e5':       ('E5 (SS 014711)',    (15.5 * cm, 22 * cm)),
    'g5':       ('G5 (SS 014711)',    (16.9 * cm, 23.9 * cm)),
    'f4':       ('F4',                (21 * cm, 33 * cm)),
    'a3p':      ('A3+',               (32.9 * cm, 48.3 * cm)),

    'dl':       ('DL (ISO 269)',      (9.9 * cm, 21 * cm)),
    'dle':      ('DLE (ISO 269)',     (11 * cm, 22 * cm)),
    'e4':       ('E4 (ISO 269)',      (28 * cm, 40 * cm)),
    'c6c5':     ('C6/C5 (ISO 269)',   (11.4 * cm, 22.9 * cm)),

    'jb0':      ('JIS B0',            (103 * cm, 145.6 * cm)),
    'jb1':      ('JIS B1',            (72.8 * cm, 103 * cm)),
    'jb2':      ('JIS B2',            (51.5 * cm, 72.8 * cm)),
    'jb3':      ('JIS B3',            (36.4 * cm, 51.5 * cm)),
    'jb4':      ('JIS B4',            (25.7 * cm, 36.4 * cm)),
    'jb5':      ('JIS B5',            (18.2 * cm, 25.7 * cm)),
    'jb6':      ('JIS B6',            (12.8 * cm, 18.2 * cm)),
    'jb7':      ('JIS B7',            (9.1 * cm, 12.8 * cm)),
    'jb8':      ('JIS B8',            (6.4 * cm, 9.1 * cm)),

    'letter':   ('Letter (ANSI A)',   pagesizes.LETTER),
    'h_letter': ('Half Letter',       (pagesizes.LETTER[1] * 0.5,
                                       pagesizes.LETTER[0])),
    'exec':     ('Executive',         (7 * inch, 10 * inch)),
    'g_letter': ('Government-Letter', (8 * inch, 10.5 * inch)),
    'legal':    ('Legal',             pagesizes.LEGAL),
    'j_legal':  ('Junior Legal',      (5 * inch, 8 * inch)),
    '11by17':   ('Tabloid (ANSI B)',  pagesizes.ELEVENSEVENTEEN),
    'ansi_c':   ('ANSI C',            (17 * inch, 22 * inch)),
    'ansi_d':   ('ANSI D',            (22 * inch, 34 * inch)),
    'ansi_e':   ('ANSI E',            (34 * inch, 44 * inch)),

    'p1':       ('P1 (CAN 2-9.60M)',  (56 * cm, 86 * cm)),
    'p2':       ('P2 (CAN 2-9.60M)',  (43 * cm, 56 * cm)),
    'p3':       ('P3 (CAN 2-9.60M)',  (28 * cm, 43 * cm)),
    'p4':       ('P4 (CAN 2-9.60M)',  (21.5 * cm, 28 * cm)),
    'p5':       ('P5 (CAN 2-9.60M)',  (14 * cm, 21.5 * cm)),
    'p6':       ('P6 (CAN 2-9.60M)',  (10.7 * cm, 14 * cm)),

    'pli1':     ('Pliego',            (70 * cm, 100 * cm)),
    'pli2':     ('½ pliego',          (50 * cm, 70 * cm)),
    'pli4':     ('¼ pliego',          (35 * cm, 50 * cm)),
    'pli8':     ('⅛ pliego',          (25 * cm, 35 * cm)),
    'carta':    ('Carta',             (21.6 * cm, 27.9 * cm)),
    'oficio':   ('Oficio',            (21.6 * cm, 33 * cm)),
    'exttab':   ('Extra Tabloide',    (30.48 * cm, 45.72 * cm))
}

PAGE_ORIENTATIONS = {
    'portrait':  (_('Portrait'),  pagesizes.portrait),
    'landscape': (_('Landscape'), pagesizes.landscape)
}

DEFAULT_FONT = None

_re_units = re.compile(r'^(\d*(?:\.\d+)?)\s*(pt|in|inch|mm|cm|pc|pica|px)?$',
                       re.IGNORECASE)


def eval_length(length_str):
    if length_str is None:
        return None
    if isinstance(length_str, (int, float)):
        return length_str
    m = _re_units.match(length_str)
    if m is None:
        return None
    amount = float(m.group(1))
    unit = m.group(2)
    if unit is not None:
        unit = unit.lower()
    if unit in ('in', 'inch'):
        amount *= inch
    elif unit == 'mm':
        amount *= mm
    elif unit == 'cm':
        amount *= cm
    elif unit in ('pc', 'pica'):
        amount *= pica
    elif unit == 'px':
        # We use conventional DPI of 96
        amount *= 0.75
    return amount


class DefaultTableStyle(TableStyle):
    def __init__(self, cmds=None, parent=None, **kw):
        has_header = kw.pop('has_header', True)
        font = kw.pop('font', DEFAULT_FONT)
        grid_width = kw.pop('grid_width', 0.2)
        grid_color = kw.pop('grid_color', colors.dimgrey)
        header_fg = kw.pop('header_fg', colors.black)
        header_bg = kw.pop('header_bg', colors.HexColor(0xe6e6e6))
        row_bg = kw.pop('row_bg', (colors.white, colors.HexColor(0xf5f5f5)))

        super(DefaultTableStyle, self).__init__(cmds, parent, **kw)

        first_data = 1 if has_header else 0
        new_cmds = [
            ('GRID',   (0, 0),          (-1, -1), grid_width, grid_color),
            ('FONT',   (0, 0),          (-1, -1), font),
            ('VALIGN', (0, first_data), (-1, -1), 'TOP')
        ]
        if has_header:
            new_cmds.extend((('TEXTCOLOR',  (0, 0), (-1, 0), header_fg),
                             ('BACKGROUND', (0, 0), (-1, 0), header_bg)))
        if row_bg:
            new_cmds.append(('ROWBACKGROUNDS',
                             (0, first_data),
                             (-1, -1),
                             row_bg))
        self._cmds = new_cmds + self._cmds


class OutlineEntryFlowable(ActionFlowable):
    def __init__(self, title, key, level=0, closed=None, bookmark=False):
        self.title = title
        self.key = key
        self.level = level
        self.closed = closed
        self.bookmark = bookmark

    def apply(self, doc):
        canvas = doc.canv
        if self.bookmark:
            canvas.bookmarkPage(self.key, fit='FitH')
        canvas.addOutlineEntry(self.title, self.key, self.level, self.closed)


CANVAS_ABSOLUTE = 0
CANVAS_RELATIVE = 1

_CANVAS_POS = {
    CANVAS_RELATIVE: CANVAS_RELATIVE,
    CANVAS_ABSOLUTE: CANVAS_ABSOLUTE,
    'relative': CANVAS_RELATIVE,
    'absolute': CANVAS_ABSOLUTE
}


class CanvasFlowable(Flowable):
    def __init__(self, x=0, y=0, width=0, height=0, position=CANVAS_ABSOLUTE):
        self.contents = []
        self.offset_x = x
        self.offset_y = y
        self.width = width
        self.height = height
        self.position = _CANVAS_POS[position]
        self._drawing = None

    @property
    def drawing(self):
        if self._drawing is None:
            self._drawing = shapes.Drawing(self.width, self.height,
                                           initialFontName=DEFAULT_FONT)
        return self._drawing

    def add(self, obj):
        if isinstance(obj, shapes.Shape):
            self.drawing.add(obj)
        else:
            self.contents.append(obj)

    def coord(self, pgsz, x, y):
        return (self.offset_x + x, pgsz[1] - self.offset_y - y)

    def drawOn(self, canvas, x, y, _sW=0):
        pgsz = canvas._doctemplate.pageTemplate.pagesize

        pos_x = self.offset_x
        pos_y = pgsz[1] - self.offset_y
        max_width = pgsz[0] - self.offset_x
        max_height = pgsz[1] - self.offset_y
        if self.position == CANVAS_RELATIVE:
            pos_x = x + self.offset_x
            pos_y = y - self.offset_y
            max_width -= x
            max_height -= (pgsz[1] - y)
        if self.width > 0 and self.height > 0:
            max_width = self.width
            max_height = self.height

        for cont in self.contents:
            ctx, obj = cont
            ox = eval_length(ctx.get('x', 0))
            oy = eval_length(ctx.get('y', 0))
            owidth = min(eval_length(ctx.get('width', max_width)),
                         max_width)
            oheight = min(eval_length(ctx.get('height', max_height)),
                          max_height)
            wwidth, wheight = obj.wrapOn(canvas, owidth, oheight)
            obj.drawOn(canvas, pos_x + ox, pos_y - oy - wheight)

        if self._drawing is not None:
            self._drawing.wrapOn(canvas, max_width, max_height)
            self._drawing.drawOn(canvas, pos_x, pos_y)


class DefaultDocTemplate(BaseDocTemplate):
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
        kwargs['initialFontName'] = DEFAULT_FONT
        req = kwargs.pop('request', None)
        if req:
            u = req.user
            if u:
                kwargs['author'] = (u.name_full + ' (' + u.login + ')').strip()

        super(DefaultDocTemplate, self).__init__(filename, **kwargs)


def _register_fonts(settings):
    global DEFAULT_FONT

    first_fname = None
    default_fontdir = settings.get('netprofile.fonts.directory', '')
    default_family = settings.get('netprofile.fonts.default_family', 'tinos')
    fontcfg = make_config_dict(settings, 'netprofile.fonts.family.')
    fontcfg = as_dict(fontcfg)
    for fname, cfg in fontcfg.items():
        if 'normal' not in cfg:
            continue
        fname = cfg.get('name', fname)
        if first_fname is None:
            first_fname = fname
        fontdir = cfg.get('directory', default_fontdir)
        pdfmetrics.registerFont(ttfonts.TTFont(
            fname,
            os.path.join(fontdir, cfg['normal'])))
        reg = {'normal': fname}

        if 'bold' in cfg:
            reg['bold'] = fname + '_b'
            pdfmetrics.registerFont(ttfonts.TTFont(
                reg['bold'],
                os.path.join(fontdir, cfg['bold'])))
        else:
            reg['bold'] = fname

        if 'italic' in cfg:
            reg['italic'] = fname + '_i'
            pdfmetrics.registerFont(ttfonts.TTFont(
                reg['italic'],
                os.path.join(fontdir, cfg['italic'])))
        else:
            reg['italic'] = fname

        if 'bold_italic' in cfg:
            reg['boldItalic'] = fname + '_bi'
            pdfmetrics.registerFont(ttfonts.TTFont(
                reg['boldItalic'],
                os.path.join(fontdir, cfg['bold_italic'])))
        else:
            reg['boldItalic'] = fname

        pdfmetrics.registerFontFamily(fname, **reg)

    DEFAULT_FONT = 'Times-Roman'
    if default_family in fontcfg:
        DEFAULT_FONT = fontcfg[default_family].get('name', default_family)
    elif first_fname:
        DEFAULT_FONT = first_fname
    return DEFAULT_FONT


def _add_custom_ss(ss, custom_cfg, name):
    pass


def _pdf_style_sheet(cfg):
    settings = cfg.registry.settings
    try:
        ffamily = _register_fonts(settings)
    except ttfonts.TTFError:
        logger.error('Can\'t find or register configured fonts. '
                     'PDF generation will be disabled.')
        return None
    if ffamily == 'Times-Roman':
        fonts = ('Times-Roman',
                 'Times-Bold',
                 'Times-Italic',
                 'Times-BoldItalic')
    else:
        fonts = (ffamily, ffamily + '_b', ffamily + '_i', ffamily + '_bi')

    ss = styles.StyleSheet1()

    ss.add(styles.ParagraphStyle(
        name='default',
        fontName=fonts[0],
        fontSize=10,
        leading=12,
        bulletFontName=fonts[0],
        bulletFontSize=10,
        bulletAnchor='start',
        bulletIndent=-1 * cm
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
        bulletFontName=fonts[1]
    ), alias='strong')
    ss.add(styles.ParagraphStyle(
        name='italic',
        parent=ss['body'],
        fontName=fonts[2],
        bulletFontName=fonts[2]
    ), alias='em')
    ss.add(styles.ParagraphStyle(
        name='left',
        parent=ss['body'],
        alignment=TA_LEFT
    ))
    ss.add(styles.ParagraphStyle(
        name='center',
        parent=ss['body'],
        alignment=TA_CENTER
    ))
    ss.add(styles.ParagraphStyle(
        name='right',
        parent=ss['body'],
        alignment=TA_RIGHT
    ))
    ss.add(styles.ParagraphStyle(
        name='justify',
        parent=ss['body'],
        alignment=TA_JUSTIFY
    ))
    ss.add(styles.ParagraphStyle(
        name='heading',
        parent=ss['default'],
        spaceBefore=14
    ))
    ss.add(styles.ParagraphStyle(
        name='title',
        parent=ss['heading'],
        fontName=fonts[1],
        bulletFontName=fonts[1],
        fontSize=16,
        bulletFontSize=16,
        alignment=TA_CENTER
    ))
    ss.add(styles.ParagraphStyle(
        name='heading1',
        parent=ss['heading'],
        fontName=fonts[1],
        bulletFontName=fonts[1],
        fontSize=14,
        bulletFontSize=14
    ), alias='h1')
    ss.add(styles.ParagraphStyle(
        name='heading2',
        parent=ss['heading'],
        fontName=fonts[1],
        bulletFontName=fonts[1],
        fontSize=12,
        bulletFontSize=12
    ), alias='h2')
    ss.add(styles.ParagraphStyle(
        name='heading3',
        parent=ss['heading'],
        fontName=fonts[1],
        bulletFontName=fonts[1],
        fontSize=11,
        bulletFontSize=11
    ), alias='h3')
    ss.add(styles.ParagraphStyle(
        name='heading4',
        parent=ss['heading'],
        fontName=fonts[1],
        bulletFontName=fonts[1]
    ), alias='h4')
    ss.add(styles.ParagraphStyle(
        name='heading5',
        parent=ss['heading'],
        fontName=fonts[2],
        bulletFontName=fonts[2]
    ), alias='h5')
    ss.add(styles.ParagraphStyle(
        name='caption',
        parent=ss['body'],
        fontName=fonts[2],
        bulletFontName=fonts[2]
    ))
    ss.add(styles.ParagraphStyle(
        name='table_header',
        parent=ss['body'],
        fontName=fonts[1],
        bulletFontName=fonts[1]
    ), alias='th')

    custom_ss = make_config_dict(settings, 'netprofile.pdf_styles.')
    if len(custom_ss) > 0:
        custom_ss = as_dict(custom_ss)
        for name in custom_ss:
            pass  # FIXME: write this

    logger.debug('Loaded preconfigured PDF fonts and styles.')
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
