#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: NPDML parser - PDF output
# Copyright © 2017 Alex Unigovsky
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

import io
import math
import operator
import pyparsing as pp
from six import PY3
from reportlab.platypus import (
    Frame,
    Image,
    Indenter,
    PageBreakIfNotEmpty,
    PageTemplate,
    Paragraph,
    Table
)
from reportlab.graphics import shapes
from reportlab.lib import colors
from reportlab.lib.units import cm
from svglib import svglib
from pyramid.decorator import reify

from netprofile.pdf import (
    CanvasFlowable,
    DefaultDocTemplate,
    DefaultTableStyle,
    OutlineEntryFlowable,
    PAGE_SIZES,
    PAGE_ORIENTATIONS,
    DEFAULT_FONT,
    eval_length
)
from netprofile.tpl import npdml

if PY3:
    from urllib import parse as urlparse
    from html import escape as html_escape
else:
    import urlparse
    from cgi import escape as html_escape


class NPDMLExpressionParser(object):
    _op = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '^': operator.pow
    }
    _fn = {
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'atan': math.atan,
        'abs': abs,
        'trunc': lambda x: int(x),
        'floor': math.floor,
        'ceil': math.ceil
    }

    def __init__(self, **kwargs):
        self.stack = []
        self.vars = kwargs

    def _push_first(self, strg, loc, toks):
        self.stack.append(toks[0])

    def _push_uminus(self, strg, loc, toks):
        if toks and toks[0] == '-':
            self.stack.append('U-')

    def _eval(self):
        op = self.stack.pop()
        if op == 'U-':
            return -self._eval()
        if op in self._op:
            arg2 = self._eval()
            arg1 = self._eval()
            return self._op[op](arg1, arg2)
        if op in self._fn:
            return self._fn[op](self._eval())
        if op == 'PI':
            return math.pi
        if op == 'E':
            return math.e
        if op in self.vars:
            return self.vars[op]

        return eval_length(op)

    @reify
    def _expr_parser(self):
        point = pp.Literal('.')
        e = pp.CaselessLiteral('E')
        pi = pp.CaselessLiteral('PI')

        lengths = pp.oneOf(('pt', 'in', 'inch', 'mm',
                            'cm', 'pc', 'pica', 'px'),
                           caseless=True)

        fp_number = pp.Combine(
            pp.Word('+-' + pp.nums, pp.nums) +
            pp.Optional(point + pp.Optional(pp.Word(pp.nums))) +
            pp.Optional(e + pp.Word('+-' + pp.nums, pp.nums)) +
            pp.Optional(lengths))
        ident = pp.Word(pp.alphas, pp.alphas + pp.nums + '_')

        plus = pp.Literal('+')
        minus = pp.Literal('-')
        mult = pp.Literal('*')
        div = pp.Literal('/')
        lpar = pp.Literal('(').suppress()
        rpar = pp.Literal(')').suppress()

        addop = plus | minus
        multop = mult | div
        expop = pp.Literal('^')

        expr = pp.Forward()

        atom = (
            pp.Optional('-') + (pi | e | fp_number
                                | ident + lpar + expr + rpar
                                | ident).setParseAction(self._push_first)
            | (lpar + expr.suppress() + rpar)
        ).setParseAction(self._push_uminus)

        factor = pp.Forward()
        factor << atom + pp.ZeroOrMore(
                (expop + factor).setParseAction(self._push_first))

        term = factor + pp.ZeroOrMore(
                (multop + factor).setParseAction(self._push_first))
        expr << term + pp.ZeroOrMore(
                (addop + term).setParseAction(self._push_first))

        return expr

    def parse(self, expr):
        self.stack = []
        self._expr_parser.parseString(expr)
        return self._eval()


def _attr_str(attrs):
    return ' '.join(('%s="%s"' % (k, html_escape(v)))
                    for k, v
                    in attrs.items())


class NPDMLDocTemplate(DefaultDocTemplate):
    pass


class PDFParseTarget(npdml.NPDMLParseTarget):
    def __init__(self, req, buf=None, **kwargs):
        super(PDFParseTarget, self).__init__()
        self.req = req
        if buf is None:
            buf = io.BytesIO()
        self.buf = buf
        self.story = []
        self._indent_step = kwargs.pop('indent_step', 1 * cm)
        self._opts = kwargs
        self._doc = None
        self._title = None
        self._page_tpls = {}
        self._cur_page_tpl = None

    @property
    def doc(self):
        if self._doc is None:
            doc = self._doc = NPDMLDocTemplate(
                self.buf,
                request=self.req,
                pagesize=self._opts.get('pagesize', 'a4'),
                orientation=self._opts.get('orientation', 'portrait'),
                topMargin=self._opts.get('topMargin', 2.0 * cm),
                leftMargin=self._opts.get('leftMargin', 1.8 * cm),
                rightMargin=self._opts.get('rightMargin', 1.8 * cm),
                bottomMargin=self._opts.get('bottomMargin', 2.0 * cm),
                title=self._title)
            parser = NPDMLExpressionParser(
                width=doc.width,
                height=doc.height,
                topMargin=doc.topMargin,
                leftMargin=doc.leftMargin,
                rightMargin=doc.rightMargin,
                bottomMargin=doc.bottomMargin)
            pages = []
            if len(self._page_tpls) == 0:
                self._page_tpls = {'default': {'frames': []}}
            for tplid, tpl in self._page_tpls.items():
                page_size = tpl.get('size')
                if page_size in PAGE_SIZES:
                    page_size = PAGE_SIZES[page_size][1]
                else:
                    page_size = doc.pagesize

                orient = tpl.get('orientation')
                if orient in PAGE_ORIENTATIONS:
                    page_size = PAGE_ORIENTATIONS[orient][1](page_size)

                parser.vars['width'] = (page_size[0]
                                        - doc.leftMargin
                                        - doc.rightMargin)
                parser.vars['height'] = (page_size[1]
                                         - doc.topMargin
                                         - doc.bottomMargin)

                frames = []
                framedef = tpl['frames']
                if len(framedef) == 0:
                    framedef.append({})
                for frame in framedef:
                    kwargs = dict((k, parser.parse(v))
                                  for k, v
                                  in frame.items()
                                  if k in {'topPadding',
                                           'leftPadding',
                                           'rightPadding',
                                           'bottomPadding'})
                    frames.append(Frame(
                        parser.parse(frame['x']) if 'x' in frame
                        else doc.leftMargin,
                        parser.parse(frame['y']) if 'y' in frame
                        else doc.bottomMargin,
                        parser.parse(frame['width']) if 'width' in frame
                        else parser.vars['width'],
                        parser.parse(frame['height']) if 'height' in frame
                        else parser.vars['height'],
                        id=frame.get('id', 'body'),
                        **kwargs))

                next_page = tpl.get('next')
                if next_page is not None:
                    next_page = next_page.split(',')
                pages.append(PageTemplate(id=tplid,
                                          pagesize=page_size,
                                          autoNextPageTemplate=next_page,
                                          frames=frames))
            doc.addPageTemplates(pages)
        return self._doc

    def start(self, tag, attrs):
        # Need to get parent before inserting context.
        parent = self.parent
        curctx = super(PDFParseTarget, self).start(tag, attrs)
        ss = self.req.pdf_styles

        if (isinstance(curctx, npdml.NPDMLBlock)
                and isinstance(parent, npdml.NPDMLBlock)
                and parent.data):
            para = parent.get_data()
            if para:
                para = Paragraph(para, ss[parent.get('style', 'body')])
                self.story.append(para)
            parent.data = []

        if isinstance(curctx, npdml.NPDMLPageContext):
            if isinstance(parent, npdml.NPDMLPageTemplateContext):
                curctx.setdefault('id', 'default')
                curctx['frames'] = []
            elif isinstance(parent, npdml.NPDMLDocumentContext):
                tpl = ['default']
                if 'template' in curctx:
                    tpl = curctx['template']
                    if ',' in tpl:
                        tpl = tpl.split(',')
                    else:
                        tpl = [tpl]
                elif self._cur_page_tpl is not None:
                    tpl = [self._cur_page_tpl.get('next', 'default')]
                if len(tpl) == 1:
                    try:
                        self._cur_page_tpl = self._page_tpls[tpl[0]]
                    except KeyError:
                        self._cur_page_tpl = None
                else:
                    self._cur_page_tpl = None
                self.story.append(PageBreakIfNotEmpty(*tpl))
        elif isinstance(curctx, npdml.NPDMLCanvasContext):
            curctx.canvas = CanvasFlowable(
                eval_length(curctx['x']),
                eval_length(curctx['y']),
                width=eval_length(curctx.get('width', 0)),
                height=eval_length(curctx.get('height', 0)),
                position=curctx.get('position', 'absolute'))

        if (isinstance(curctx, npdml.NPDMLBlock)
                and not isinstance(parent, npdml.NPDMLCanvasContext)):
            if curctx.is_numbered:
                curctx._indenter = Indenter(self._indent_step)
                self.story.append(curctx._indenter)

    def end(self, tag):
        curctx = super(PDFParseTarget, self).end(tag)
        parent = self.parent
        ss = self.req.pdf_styles

        if (isinstance(curctx, npdml.NPDMLPageContext)
                and isinstance(parent, npdml.NPDMLPageTemplateContext)):
            self._page_tpls[curctx['id']] = curctx
        elif (isinstance(curctx, npdml.NPDMLFrameContext)
                and isinstance(parent, npdml.NPDMLPageContext)):
            parent['frames'].append(curctx)
        elif isinstance(curctx, npdml.NPDMLParagraphContext):
            btext = None
            if curctx.is_numbered:
                btext = self.get_bullet(curctx)
            para = Paragraph(curctx.get_data(),
                             ss[curctx.get('style', 'body')],
                             bulletText=btext)
            if isinstance(parent, npdml.NPDMLCanvasContext):
                parent.canvas.add((curctx, para))
            else:
                self.story.append(para)
        elif isinstance(curctx, npdml.NPDMLTableCellContext):
            para_style = 'body'
            if isinstance(parent, npdml.NPDMLTableHeaderContext):
                para_style = 'table_header'
            if 'width' in curctx:
                parent.widths.append(eval_length(curctx['width']))
            else:
                parent.widths.append(None)
            para = Paragraph(curctx.get_data(),
                             ss[curctx.get('style', para_style)])

            colspan = 1
            rowspan = 1
            if 'colspan' in curctx:
                try:
                    colspan = int(curctx['colspan'])
                except (TypeError, ValueError):
                    pass
            if 'rowspan' in curctx:
                try:
                    rowspan = int(curctx['rowspan'])
                except (TypeError, ValueError):
                    pass
            para.colspan = colspan
            para.rowspan = rowspan
            parent.cells.append(para)
            if colspan > 1:
                parent.cells.extend([''] * (colspan - 1))
        elif isinstance(curctx, npdml.NPDMLTableRowContext):
            parent.rows.append(curctx.cells)
            if isinstance(curctx, npdml.NPDMLTableHeaderContext):
                parent.has_header = True
            if len(parent.widths) < len(curctx.widths):
                parent.widths = curctx.widths
        elif isinstance(curctx, npdml.NPDMLTableContext):
            # FIXME: unhardcode spacing
            kwargs = {
                'colWidths':   curctx.widths,
                'spaceBefore': 8
            }
            if 'repeatRows' in curctx:
                try:
                    kwargs['repeatRows'] = int(curctx['repeatRows'])
                except (TypeError, ValueError):
                    pass
            if 'align' in curctx:
                value = curctx['align'].upper()
                if value in ('LEFT', 'RIGHT', 'CENTER'):
                    kwargs['hAlign'] = value

            extra_style = []
            rowspans = {}

            for rowidx, row in enumerate(curctx.rows):
                for colidx in list(rowspans):
                    rowspans[colidx] -= 1
                    if rowspans[colidx] == 0:
                        del rowspans[colidx]
                    row.insert(colidx, '')
                for colidx, col in enumerate(row):
                    if not isinstance(col, Paragraph):
                        continue
                    if col.colspan > 1 or col.rowspan > 1:
                        extra_style.append(('SPAN',
                                            (colidx, rowidx),
                                            (colidx + col.colspan - 1,
                                             rowidx + col.rowspan - 1)))
                        if col.rowspan > 1:
                            # FIXME: proper backgrounds of spanned cells
                            extra_style.append(('ROWBACKGROUNDS',
                                                (colidx, rowidx),
                                                (colidx + col.colspan - 1,
                                                 rowidx + col.rowspan - 1),
                                                (colors.white,)))
                            for idx in range(colidx, colidx + col.colspan):
                                rowspans[idx] = col.rowspan - 1

            table = Table(curctx.rows, **kwargs)
            table.setStyle(DefaultTableStyle(extra_style,
                                             has_header=curctx.has_header))
            self.story.append(table)
        elif isinstance(curctx, npdml.NPDMLAnchorContext):
            curctx.setdefault('color', 'blue')
            markup = '<a %s>%s</a>' % (_attr_str(curctx), curctx.get_data())
            parent.data.append(markup)
        elif isinstance(curctx, npdml.NPDMLBoldContext):
            markup = '<b>%s</b>' % (curctx.get_data(),)
            parent.data.append(markup)
        elif isinstance(curctx, npdml.NPDMLItalicContext):
            markup = '<i>%s</i>' % (curctx.get_data(),)
            parent.data.append(markup)
        elif isinstance(curctx, npdml.NPDMLUnderlineContext):
            markup = '<u>%s</u>' % (curctx.get_data(),)
            parent.data.append(markup)
        elif isinstance(curctx, npdml.NPDMLStrikethroughContext):
            markup = '<strike>%s</strike>' % (curctx.get_data(),)
            parent.data.append(markup)
        elif isinstance(curctx, npdml.NPDMLSuperscriptContext):
            markup = '<super>%s</super>' % (curctx.get_data(),)
            parent.data.append(markup)
        elif isinstance(curctx, npdml.NPDMLSubscriptContext):
            markup = '<sub>%s</sub>' % (curctx.get_data(),)
            parent.data.append(markup)
        elif isinstance(curctx, npdml.NPDMLFontContext):
            kwargs = {}
            for attr in ('name', 'size', 'color'):
                if attr in curctx:
                    kwargs[attr] = curctx[attr]
            if len(kwargs):
                markup = '<font %s>%s</font>' % (_attr_str(kwargs),
                                                 curctx.get_data())
                parent.data.append(markup)
            else:
                parent.data.append(curctx.get_data())
        elif isinstance(curctx, npdml.NPDMLImageContext):
            kwargs = {}
            src = urlparse.urlparse(curctx['src'])
            # TODO: Support http, https, and vfs URLs
            if src.scheme != 'file':
                raise NotImplementedError('Only "file://" URLs '
                                          'are implemented.')
            image = src.path
            if image.endswith('.svg') or image.endswith('.svgz'):
                image = svglib.svg2rlg(image)
            if isinstance(parent, npdml.NPDMLCanvasContext):
                if isinstance(image, shapes.Drawing):
                    parent.canvas.add((curctx, image))
                else:
                    x = eval_length(curctx.get('x', 0))
                    y = eval_length(curctx.get('y', 0))
                    # FIXME: we fail to position image properly when
                    #        width/height are not given.
                    width = eval_length(curctx.get('width', 0))
                    height = eval_length(curctx.get('height', 0))
                    image = shapes.Image(x, - y - height, width, height, image)
                    parent.canvas.add(image)
            else:
                # TODO: support different scaling modes (kind=)
                if 'width' in curctx:
                    kwargs['width'] = eval_length(curctx['width'])
                if 'height' in curctx:
                    kwargs['height'] = eval_length(curctx['height'])
                if 'align' in curctx:
                    value = curctx['align'].upper()
                    if value in ('LEFT', 'RIGHT', 'CENTER'):
                        kwargs['hAlign'] = value
                # TODO: vAlign
                if isinstance(image, shapes.Drawing):
                    for k, v in kwargs.items():
                        setattr(image, k, v)
                    self.story.append(image)
                else:
                    self.story.append(Image(image, **kwargs))
        elif isinstance(curctx, npdml.NPDMLTitleContext):
            if isinstance(parent, npdml.NPDMLPageContext):
                para = Paragraph(curctx.get_data(),
                                 ss[curctx.get('style', 'title')])
                self.story.append(para)
            elif isinstance(parent, npdml.NPDMLMetadataContext):
                self._title = curctx.get_data()
            elif isinstance(parent, npdml.NPDMLSectionContext):
                text = curctx.get_data()
                para_text = text
                sect_id = self.get_section_id()
                dlevel = parent.depth
                btext = None
                if parent.is_numbered:
                    btext = self.get_bullet(curctx)

                    if parent.in_toc and dlevel > 0:
                        para_text = '<a name="%s"/>%s' % (sect_id,
                                                          text)
                        outline = '%s%s' % (
                            '' if btext is None else btext + ' ',
                            text)
                        self.story.append(OutlineEntryFlowable(outline,
                                                               sect_id,
                                                               dlevel - 1))

                para = Paragraph(para_text,
                                 ss[curctx.get('style',
                                               'heading' + str(dlevel))],
                                 bulletText=btext)
                self.story.append(para)
        elif isinstance(curctx, npdml.NPDMLCanvasContext):
            self.story.append(curctx.canvas)

        # Process canvas-only elements
        if isinstance(parent, npdml.NPDMLCanvasContext):
            canvas = parent.canvas
            if isinstance(curctx, npdml.NPDMLLineContext):
                x1 = eval_length(curctx.pop('x1', 0))
                y1 = eval_length(curctx.pop('y1', 0))
                x2 = eval_length(curctx.pop('x2'))
                y2 = eval_length(curctx.pop('y2'))
                canvas.add(shapes.Line(x1, -y1, x2, -y2, **curctx))
            elif isinstance(curctx, npdml.NPDMLRectangleContext):
                x = eval_length(curctx.pop('x', 0))
                y = eval_length(curctx.pop('y', 0))
                width = eval_length(curctx.pop('width'))
                height = eval_length(curctx.pop('height', width))
                rx = eval_length(curctx.pop('rx', 0))
                ry = eval_length(curctx.pop('ry', 0))
                curctx.setdefault('fillColor', None)
                canvas.add(shapes.Rect(x, - y - height,
                                       width, height,
                                       rx, ry,
                                       **curctx))
            elif isinstance(curctx, npdml.NPDMLLabelContext):
                x = eval_length(curctx.pop('x', 0))
                y = eval_length(curctx.pop('y', 0))
                curctx.setdefault('fontName', DEFAULT_FONT)
                canvas.add(shapes.String(x, -y, curctx.get_data(), **curctx))
            elif isinstance(curctx, npdml.NPDMLCircleContext):
                cx = eval_length(curctx.pop('cx'))
                cy = eval_length(curctx.pop('cy'))
                radius = eval_length(curctx.pop('radius'))
                curctx.setdefault('fillColor', None)
                canvas.add(shapes.Circle(cx, -cy, radius, **curctx))
            elif isinstance(curctx, npdml.NPDMLEllipseContext):
                cx = eval_length(curctx.pop('cx'))
                cy = eval_length(curctx.pop('cy'))
                rx = eval_length(curctx.pop('rx'))
                ry = eval_length(curctx.pop('ry'))
                curctx.setdefault('fillColor', None)
                canvas.add(shapes.Ellipse(cx, -cy, rx, ry, **curctx))

        if isinstance(curctx, npdml.NPDMLBlock) and curctx._indenter:
            self.story.append(Indenter(-curctx._indenter.left,
                                       -curctx._indenter.right))

    def data(self, data):
        self.parent.data.append(html_escape(data.strip()))

    def close(self):
        self.doc.multiBuild(self.story)
        buf_len = self.buf.tell()
        self.buf.seek(0)
        return (self.buf, buf_len)

    def get_bullet(self, ctx):
        prefix = ctx.get('prefix')
        def_fmt = '{}.'
        def_join = '.'
        counters = self.get_counters(last=ctx)
        if counters is None:
            return None
        if prefix == 'indent':
            return ''
        elif prefix == 'roman':
            pass
        elif prefix == 'uc-roman':
            pass
        elif prefix == 'latin':
            pass
        elif prefix == 'uc-latin':
            pass
        else:
            counters = (str(x) for x in counters)

        prefix_fmt = ctx.get('prefixFormat', def_fmt)
        prefix_join = ctx.get('prefixJoin', def_join)

        return prefix_fmt.format(prefix_join.join(counters))
