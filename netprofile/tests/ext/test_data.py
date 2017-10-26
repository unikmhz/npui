#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Tests for ExtJS schema and data generation
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

import unittest
import mock

# Test body begins here

from pyramid.i18n import TranslationString
import sqlalchemy as sa
from netprofile.db import fields
from netprofile.ext.data import (
    ExtColumn,
    _get_aggregate_column,
    _get_groupby_clause,
    _name_to_class,
    _recursive_update,
    _recursive_update_list,
    _table_to_class
)


class TestExtDataHelpers(unittest.TestCase):
    @mock.patch('netprofile.ext.data.Base')
    def test_name_to_class(self, base):
        cls1 = mock.MagicMock()
        base._decl_class_registry = {'cls1': cls1}

        self.assertEqual(_name_to_class('cls1'), cls1)

        with self.assertRaises(KeyError):
            _name_to_class('cls2')

    @mock.patch('netprofile.ext.data.Base')
    def test_table_to_class(self, base):
        cls1 = mock.MagicMock()
        cls1.__tablename__ = 'tbl1'
        base._decl_class_registry = {}

        with self.assertRaises(KeyError):
            _table_to_class('tbl1')

        base._decl_class_registry = {'cls1': cls1}
        self.assertEqual(_table_to_class('tbl1'), cls1)
        with self.assertRaises(KeyError):
            _table_to_class('tbl2')

        mapper = mock.MagicMock()
        mapper.single = True
        mapper.base_mapper.class_ = 'TEST'
        cls1.__mapper__ = mapper

        self.assertEqual(_table_to_class('tbl1'), 'TEST')

    def test_recursive_update(self):
        loc = mock.MagicMock()
        ts = TranslationString('test')
        dest = {'a': 1,
                'b': {'c': 2},
                'l': [10]}
        src = {'a': None,
               'd': 3,
               'b': {'e': 4},
               'f': None,
               'l': [20],
               't': ts}
        _recursive_update(dest, src, loc)

        loc.translate.assert_called_once_with(ts)
        self.assertEqual(dest, {'b': {'c': 2, 'e': 4},
                                'd': 3,
                                'l': [10, 20],
                                't': loc.translate(ts)})

    def test_recursive_update_list(self):
        loc = mock.MagicMock()
        ts = TranslationString('test')
        dest = [0]
        src = [1, 2, {'a': 3}, [10, 20], ts]

        _recursive_update_list(dest, src, loc)

        loc.translate.assert_called_once_with(ts)
        self.assertEqual(dest, [0, 1, 2, {'a': 3}, [10, 20],
                                loc.translate(ts)])

    @mock.patch('netprofile.ext.data.func')
    def test_get_aggregate_column(self, func):
        dialect = mock.MagicMock()
        field = mock.MagicMock()

        ret = _get_aggregate_column(dialect, 'max', field, 'test')
        func.max.assert_called_once_with(field)
        func.max().label.assert_called_once_with('test')
        self.assertEqual(ret, func.max().label())

        with self.assertRaises(ValueError):
            _get_aggregate_column(dialect, 'wrong', field, 'test')

        ret = _get_aggregate_column(dialect, 'count_distinct', field, 'test')
        func.count.assert_called_once_with(field.distinct())
        self.assertEqual(ret, func.count().label())

    @mock.patch('netprofile.ext.data.func')
    def test_get_groupby_clause(self, func):
        dialect = mock.MagicMock()
        field = mock.MagicMock()

        ret = _get_groupby_clause(dialect, 'day', field)
        func.extract.assert_called_once_with('day', field)
        self.assertEqual(ret, func.extract())

        with self.assertRaises(ValueError):
            _get_groupby_clause(dialect, 'wrong', field)


class TestExtColumn(unittest.TestCase):
    def setUp(self):
        col = mock.MagicMock()
        col.name = 'col1'
        col.doc = 'docstr'
        col.info = {}

        model = mock.MagicMock()

        self.column = col
        self.model = model
        self.xc = ExtColumn(col, model)

    def test_init(self):
        self.assertEqual(self.xc.column, self.column)
        self.assertEqual(self.xc.model, self.model)
        self.assertIsNone(self.xc.alias)

    def test_name(self):
        self.assertEqual(self.xc.name, 'col1')
        self.assertEqual(self.xc.__name__, 'col1')
        self.xc.alias = 'alias1'
        self.assertEqual(self.xc.name, 'alias1')
        self.assertEqual(self.xc.__name__, 'alias1')

    def test_header_string(self):
        self.assertEqual(self.xc.header_string, 'docstr')
        self.xc.column.info['header_string'] = 'head'
        self.assertEqual(self.xc.header_string, 'head')

    def test_help_text(self):
        self.assertIsNone(self.xc.help_text)
        self.xc.column.info['help_text'] = 'helpstr'
        self.assertEqual(self.xc.help_text, 'helpstr')

    def test_column_name(self):
        self.assertEqual(self.xc.column_name, 'docstr')
        self.xc.column.info['header_string'] = 'head'
        self.assertEqual(self.xc.column_name, 'head')
        self.xc.column.info['column_name'] = 'cname'
        self.assertEqual(self.xc.column_name, 'cname')

    def test_column_width(self):
        self.assertIsNone(self.xc.column_width)
        self.xc.column.info['column_width'] = 20
        self.assertEqual(self.xc.column_width, 20)

    def test_column_flex(self):
        self.assertIsNone(self.xc.column_flex)
        self.xc.column.info['column_flex'] = 3
        self.assertEqual(self.xc.column_flex, 3)

    def test_column_resizable(self):
        self.assertTrue(self.xc.column_resizable)
        self.xc.column.info['column_resizable'] = False
        self.assertFalse(self.xc.column_resizable)

    def test_multivalue(self):
        self.assertFalse(self.xc.multivalue)
        self.xc.column.info['multivalue'] = True
        self.assertTrue(self.xc.column_resizable)

    def test_cell_class(self):
        self.assertIsNone(self.xc.cell_class)
        self.xc.column.info['cell_class'] = 'cls'
        self.assertEqual(self.xc.cell_class, 'cls')

    def test_filter_type(self):
        self.assertEqual(self.xc.filter_type, 'string')
        self.xc.column.type = fields.Int32()
        self.assertEqual(self.xc.filter_type, 'npnumber')
        self.xc.column.info['filter_type'] = 'testft'
        self.assertEqual(self.xc.filter_type, 'testft')

    def test_reader(self):
        self.assertIsNone(self.xc.reader)
        self.xc.column.info['reader'] = 'READER'
        self.assertEqual(self.xc.reader, 'READER')

    def test_writer(self):
        self.assertIsNone(self.xc.writer)
        self.xc.column.info['writer'] = 'WRITER'
        self.assertEqual(self.xc.writer, 'WRITER')

    def test_validator(self):
        self.assertIsNone(self.xc.validator)
        self.xc.column.info['validator'] = 'VALIDATOR'
        self.assertEqual(self.xc.validator, 'VALIDATOR')

    def test_pass_request(self):
        self.assertFalse(self.xc.pass_request)
        self.xc.column.info['pass_request'] = True
        self.assertTrue(self.xc.pass_request)

    def test_template(self):
        self.assertIsNone(self.xc.template)
        self.xc.column.info['template'] = 'TPL'
        self.assertEqual(self.xc.template, 'TPL')

    def test_vtype(self):
        self.assertIsNone(self.xc.vtype)
        self.xc.column.info['vtype'] = 'VTYPE'
        self.assertEqual(self.xc.vtype, 'VTYPE')

    def test_editor_config(self):
        self.assertIsNone(self.xc.editor_config)
        self.xc.column.info['editor_config'] = 'CFG'
        self.assertEqual(self.xc.editor_config, 'CFG')

    def test_length(self):
        self.xc.column.type.length = 10
        self.assertEqual(self.xc.length, 10)
        del self.xc.column.type.length
        self.assertIsNone(self.xc.length)

        self.xc.column.type = fields.MACAddress()
        self.assertEqual(self.xc.length, 17)

        self.xc.column.type = fields.JSONData()
        self.assertEqual(self.xc.length, 300)

        class TestEnum(fields.DeclEnum):
            a = 'a', 'Descr 1', 10
            b = 'b', 'Longer Descr 2', 20
            c = 'c', 'Shorter 3', 30

        self.xc.column.type = TestEnum.db_type()
        self.assertEqual(self.xc.length, 14)

        self.xc.column.type = sa.BINARY(30)
        self.assertEqual(self.xc.length, 60)

        self.xc.column.type = fields.Int8()
        self.assertEqual(self.xc.length, 4)
        self.xc.column.type = fields.UInt8()
        self.assertEqual(self.xc.length, 3)
        self.xc.column.type = fields.Int16()
        self.assertEqual(self.xc.length, 6)
        self.xc.column.type = fields.UInt16()
        self.assertEqual(self.xc.length, 5)
        self.xc.column.type = fields.Int32()
        self.assertEqual(self.xc.length, 11)
        self.xc.column.type = fields.UInt32()
        self.assertEqual(self.xc.length, 10)
        self.xc.column.type = sa.SmallInteger()
        self.assertEqual(self.xc.length, 6)
        self.xc.column.type = sa.Integer()
        self.assertEqual(self.xc.length, 11)
        self.xc.column.type = sa.BigInteger()
        self.assertEqual(self.xc.length, 20)
        self.xc.column.type = sa.dialects.mysql.SMALLINT(unsigned=True)
        self.assertEqual(self.xc.length, 5)
        self.xc.column.type = sa.dialects.mysql.INTEGER(unsigned=True)
        self.assertEqual(self.xc.length, 10)

    def test_pixels(self):
        self.xc.column.type.length = 10
        self.assertEqual(self.xc.pixels, 100)
        self.xc.column.type.length = 1
        self.assertEqual(self.xc.pixels, 40)
        self.xc.column.type.length = 50
        self.assertEqual(self.xc.pixels, 300)

        del self.xc.column.type.length
        self.assertEqual(self.xc.pixels, 200)

    def test_bit_length(self):
        self.xc.column.type = fields.Int8()
        self.assertEqual(self.xc.bit_length, 8)
        self.xc.column.type = fields.UInt16()
        self.assertEqual(self.xc.bit_length, 16)
        self.xc.column.type = sa.dialects.mysql.SMALLINT()
        self.assertEqual(self.xc.bit_length, 16)
        self.xc.column.type = fields.Int32()
        self.assertEqual(self.xc.bit_length, 32)
        self.xc.column.type = sa.dialects.mysql.INTEGER(unsigned=True)
        self.assertEqual(self.xc.bit_length, 32)
        self.xc.column.type = fields.UInt64()
        self.assertEqual(self.xc.bit_length, 64)
        self.xc.column.type = sa.Unicode(255)
        self.assertIsNone(self.xc.bit_length)
