#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Custom database fields
# Copyright © 2013-2017 Alex Unigovsky
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

import binascii
import collections
import json
import re
import uuid

from six import PY3
from sqlalchemy import (
    schema,
    type_coerce,
    types,
    util
)
from sqlalchemy.dialects import (
    mssql,
    mysql,
    oracle,
    postgresql
)
from sqlalchemy.sql import (
    expression,
    sqltypes
)
from sqlalchemy.ext.compiler import compiles

from netprofile.db import processors
from netprofile.common import ipaddr

if PY3:
    from netprofile.db.enum3 import (  # noqa: F401
        EnumSymbol,
        EnumMeta,
        DeclEnum
    )
else:
    from netprofile.db.enum2 import (  # noqa: F401
        EnumSymbol,
        EnumMeta,
        DeclEnum
    )

_D_MYSQL = frozenset([
    mysql.mysqlconnector.dialect,
    mysql.mysqldb.dialect,
    mysql.oursql.dialect,
    mysql.pymysql.dialect,
    mysql.pyodbc.dialect,
    mysql.zxjdbc.dialect
])

_D_PGSQL = frozenset([
    postgresql.pg8000.dialect,
    postgresql.psycopg2.dialect,
    postgresql.pypostgresql.dialect,
    postgresql.zxjdbc.dialect
])

_D_ORA = frozenset([
    oracle.cx_oracle.dialect,
    oracle.zxjdbc.dialect
])

_D_MSSQL = frozenset([
    mssql.adodbapi.dialect,
    mssql.mxodbc.dialect,
    mssql.pymssql.dialect,
    mssql.pyodbc.dialect,
    mssql.zxjdbc.dialect
])

_D_STD = frozenset([
    mysql.dialect,
    postgresql.dialect,
    oracle.dialect,
    mssql.dialect
])


def _is_mysql(d):
    return d.__class__ in _D_MYSQL


def _is_pgsql(d):
    return d.__class__ in _D_PGSQL


def _is_ora(d):
    return d.__class__ in _D_ORA


def _is_mssql(d):
    return d.__class__ in _D_MSSQL


class LargeBLOB(types.TypeDecorator):
    """
    Large binary object.
    """
    impl = types.LargeBinary

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.LONGBLOB()
        return self.impl

    @property
    def python_type(self):
        return bytes


class IPv4Address(types.TypeDecorator):
    """
    Hybrid IPv4 address.
    """
    impl = types.Integer

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.INTEGER(unsigned=True)
        if _is_pgsql(dialect):
            return postgresql.INET()
        return self.impl

    @property
    def python_type(self):
        return ipaddr.IPv4Address

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if _is_pgsql(dialect):
            return str(value)
        return int(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return ipaddr.IPv4Address(value)


class IPv6Address(types.TypeDecorator):
    """
    Hybrid IPv6 address.
    """
    impl = types.BINARY(16)

    def load_dialect_impl(self, dialect):
        if _is_pgsql(dialect):
            return postgresql.INET()
        return self.impl

    @property
    def python_type(self):
        return ipaddr.IPv6Address

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if _is_pgsql(dialect):
            return str(value)
        return value.packed

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return ipaddr.IPv6Address(value)


class IPv6Offset(types.TypeDecorator):
    """
    IPv6 address offset.
    """
    impl = types.Numeric(39, 0)
    MIN_VALUE = 0
    MAX_VALUE = 340282366920938463463374607431768211456

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.DECIMAL(precision=39, scale=0, unsigned=True)
        return self.impl

    @property
    def python_type(self):
        return int


class UUID(types.TypeDecorator):
    """
    UUID type.
    """
    impl = types.BINARY(16)

    def load_dialect_impl(self, dialect):
        if _is_pgsql(dialect):
            return postgresql.UUID(as_uuid=True)
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_pgsql(dialect):
            return isinstance(conn_type, postgresql.UUID)
        return isinstance(conn_type, types.BINARY) and conn_type.length == 16

    @property
    def python_type(self):
        return uuid.UUID

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if _is_pgsql(dialect):
            return value
        return value.bytes

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if _is_pgsql(dialect):
            return value
        return uuid.UUID(bytes=value)


class Money(types.TypeDecorator):
    """
    Money amount.
    """
    impl = types.Numeric(20, 8)


class Traffic(types.TypeDecorator):
    """
    Amount of traffic in bytes.
    """
    impl = types.Numeric(16, 0)
    MIN_VALUE = 0
    MAX_VALUE = 9999999999999999

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.DECIMAL(precision=16, scale=0, unsigned=True)
        return self.impl

    @property
    def python_type(self):
        return int


class PercentFraction(types.TypeDecorator):
    """
    Highly accurate percent fraction.
    """
    impl = types.Numeric(11, 10)

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.DECIMAL(precision=11, scale=10, unsigned=True)
        return self.impl

    @property
    def python_type(self):
        return int


class MACAddress(types.TypeDecorator):
    """
    MAC address
    """
    impl = types.BINARY(6)

    def load_dialect_impl(self, dialect):
        if _is_pgsql(dialect):
            return postgresql.MACADDR()
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_pgsql(dialect):
            return isinstance(conn_type, postgresql.MACADDR)
        return isinstance(conn_type, types.BINARY) and conn_type.length == 6

    @property
    def python_type(self):
        return str

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if _is_pgsql(dialect):
            return str(value)
        return binascii.unhexlify(bytes(value.replace(':', ''), 'utf-8'))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if _is_pgsql(dialect):
            return value
        return ':'.join('%02x' % x for x in value)


class NPBoolean(types.TypeDecorator, types.SchemaType):
    """
    An almost-normal boolean type with a special case for MySQL.
    """
    impl = types.Boolean

    def __init__(self, **kw):
        types.TypeDecorator.__init__(self, **kw)
        types.SchemaType.__init__(self, **kw)

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.ENUM('Y', 'N', charset='ascii', collation='ascii_bin')
        return types.Boolean(name='ck_boolean')

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            if not isinstance(conn_type, mysql.ENUM):
                return False
            if conn_type.enums == ('Y', 'N'):
                return True
            return False
        return isinstance(conn_type, types.Boolean)

    def _should_create_constraint(self, compiler):
        return (not compiler.dialect.supports_native_boolean
                and not _is_mysql(compiler.dialect))

    def _set_table(self, column, table):
        e = schema.CheckConstraint(
            column.in_([0, 1]),
            name=self.name,
            _create_rule=util.portable_instancemethod(
                self._should_create_constraint))
        table.append_constraint(e)

    @property
    def python_type(self):
        return bool

    def bind_processor(self, dialect):
        if _is_mysql(dialect):
            return processors.boolean_to_enum
        else:
            return None

    def result_processor(self, dialect, coltype):
        if _is_mysql(dialect):
            return processors.enum_to_boolean
        else:
            return None

    class comparator_factory(types.Boolean.Comparator):
        def __eq__(self, other):
            if isinstance(other, bool):
                other = type_coerce(other, NPBoolean)
            return types.Boolean.Comparator.__eq__(self, other)

        def __ne__(self, other):
            if isinstance(other, bool):
                other = type_coerce(other, NPBoolean)
            return types.Boolean.Comparator.__ne__(self, other)

        def is_(self, other):
            if other is None:
                return types.Boolean.Comparator.is_(self, other)
            if isinstance(other, bool):
                other = type_coerce(other, NPBoolean)
            return types.Boolean.Comparator.__eq__(self, other)

        def isnot(self, other):
            if other is None:
                return types.Boolean.Comparator.isnot(self, other)
            if isinstance(other, bool):
                other = type_coerce(other, NPBoolean)
            return types.Boolean.Comparator.__ne__(self, other)

    def process_literal_param(self, value, dialect):
        if isinstance(value, bool):
            if _is_mysql(dialect):
                if value:
                    return 'Y'
                return 'N'
            # FIXME: add SQLite check
        return value


class npbool(expression.FunctionElement):
    """
    Constant NPBoolean element.
    """
    type = NPBoolean()

    def __init__(self, val):
        self.val = val


@compiles(npbool, 'mysql')
def my_npbool(element, compiler, **kw):
    if element.val:
        return '\'Y\''
    return '\'N\''


@compiles(npbool, 'sqlite')
def sq_npbool(element, compiler, **kw):
    if element.val:
        return '1'
    return '0'


@compiles(npbool)
def compile_npbool(element, compiler, **kw):
    if element.val:
        return 'TRUE'
    return 'FALSE'


class ASCIIString(types.TypeDecorator):
    """
    ASCII-only version of normal string field.
    """
    impl = types.String

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.VARCHAR(self.impl.length,
                                 charset='ascii',
                                 collation='ascii_bin')
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            return (isinstance(conn_type, mysql.VARCHAR)
                    and conn_type.charset == 'ascii'
                    and conn_type.length == self.impl.length)
        return (isinstance(conn_type, types.String)
                and conn_type.length == self.impl.length)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, (bytes, bytearray)):
            value = value.decode('ascii')
        return value


class ASCIIFixedString(types.TypeDecorator):
    """
    ASCII-only version of fixed-length string field.
    """
    impl = types.CHAR

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.CHAR(self.impl.length,
                              charset='ascii',
                              collation='ascii_bin')
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            return (isinstance(conn_type, mysql.CHAR)
                    and conn_type.charset == 'ascii'
                    and conn_type.length == self.impl.length)
        return (isinstance(conn_type, types.CHAR)
                and conn_type.length == self.impl.length)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, (bytes, bytearray)):
            value = value.decode('ascii')
        return value


class ExactUnicode(types.TypeDecorator):
    """
    Case-honoring unicode string.
    """
    impl = types.Unicode

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.VARCHAR(self.impl.length,
                                 charset='utf8',
                                 collation='utf8_bin')
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            return (isinstance(conn_type, mysql.VARCHAR)
                    and conn_type.charset == 'utf8'
                    and conn_type.length == self.impl.length)
        return (isinstance(conn_type, types.Unicode)
                and conn_type.length == self.impl.length)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, (bytes, bytearray)):
            value = value.decode()
        return value


class JSONData(types.TypeDecorator):
    """
    Arbitrary data structures, JSON-encoded.
    """
    impl = types.UnicodeText

    def load_dialect_impl(self, dialect):
        if _is_pgsql(dialect):
            return postgresql.JSONB()
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_pgsql(dialect):
            return isinstance(conn_type, postgresql.JSONB)
        return isinstance(conn_type, types.UnicodeText)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if _is_pgsql(dialect):
            return value
        return str(json.dumps(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if _is_pgsql(dialect):
            return value
        return json.loads(value)


class Int8(types.TypeDecorator):
    """
    8-bit signed integer field.
    """
    impl = types.SmallInteger
    MIN_VALUE = -128
    MAX_VALUE = 127

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.TINYINT()
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            return (isinstance(conn_type, mysql.TINYINT)
                    and conn_type.unsigned is False)
        return isinstance(conn_type, types.SmallInteger)


class Int16(types.TypeDecorator):
    """
    16-bit signed integer field.
    """
    impl = types.SmallInteger
    MIN_VALUE = -32768
    MAX_VALUE = 32767

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.SMALLINT()
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            return (isinstance(conn_type, mysql.SMALLINT)
                    and conn_type.unsigned is False)
        return isinstance(conn_type, types.SmallInteger)


class Int32(types.TypeDecorator):
    """
    32-bit signed integer field.
    """
    impl = types.Integer
    MIN_VALUE = -2147483648
    MAX_VALUE = 2147483647

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.INTEGER()
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            return (isinstance(conn_type, mysql.INTEGER)
                    and conn_type.unsigned is False)
        return isinstance(conn_type, types.Integer)


class Int64(types.TypeDecorator):
    """
    64-bit signed integer field.
    """
    impl = types.BigInteger
    MIN_VALUE = -9223372036854775808
    MAX_VALUE = 9223372036854775807

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.BIGINT()
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            return (isinstance(conn_type, mysql.BIGINT)
                    and conn_type.unsigned is False)
        return isinstance(conn_type, types.BigInteger)


class UInt8(types.TypeDecorator):
    """
    8-bit unsigned integer field.
    """
    impl = types.SmallInteger
    MIN_VALUE = 0
    MAX_VALUE = 255

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.TINYINT(unsigned=True)
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            return (isinstance(conn_type, mysql.TINYINT)
                    and conn_type.unsigned is True)
        return isinstance(conn_type, types.SmallInteger)


class UInt16(types.TypeDecorator):
    """
    16-bit unsigned integer field.
    """
    impl = types.SmallInteger
    MIN_VALUE = 0
    MAX_VALUE = 65535

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.SMALLINT(unsigned=True)
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            return (isinstance(conn_type, mysql.SMALLINT)
                    and conn_type.unsigned is True)
        return isinstance(conn_type, types.SmallInteger)


class UInt32(types.TypeDecorator):
    """
    32-bit unsigned integer field.
    """
    impl = types.Integer
    MIN_VALUE = 0
    MAX_VALUE = 4294967295

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.INTEGER(unsigned=True)
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            return (isinstance(conn_type, mysql.INTEGER)
                    and conn_type.unsigned is True)
        return isinstance(conn_type, types.Integer)


class UInt64(types.TypeDecorator):
    """
    64-bit unsigned integer field.
    """
    impl = types.BigInteger
    MIN_VALUE = 0
    MAX_VALUE = 18446744073709551615

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.BIGINT(unsigned=True)
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            return (isinstance(conn_type, mysql.BIGINT)
                    and conn_type.unsigned is True)
        return isinstance(conn_type, types.BigInteger)


class ASCIITinyText(types.TypeDecorator):
    """
    256-byte ASCII text field.
    """
    impl = types.Text

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.TINYTEXT(charset='ascii', collation='ascii_bin')
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            return (isinstance(conn_type, mysql.TINYTEXT)
                    and conn_type.charset == 'ascii')
        return isinstance(conn_type, types.Text)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, (bytes, bytearray)):
            value = value.decode('ascii')
        return value


class ASCIIText(types.TypeDecorator):
    """
    Large ASCII text field.
    """
    impl = types.Text

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.TEXT(charset='ascii', collation='ascii_bin')
        return self.impl

    def compare_against_backend(self, dialect, conn_type):
        if _is_mysql(dialect):
            return (isinstance(conn_type, mysql.TEXT)
                    and conn_type.charset == 'ascii')
        return isinstance(conn_type, types.Text)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, (bytes, bytearray)):
            value = value.decode('ascii')
        return value


@compiles(EnumSymbol)
def compile_enumsym(element, compiler, **kw):
    return compiler.sql_compiler.render_literal_value(element.value,
                                                      sqltypes.STRINGTYPE)


class DeclEnumType(types.SchemaType, types.TypeDecorator):
    """
    Enum type which is auto-configured based on provided DeclEnum class.
    """
    def __init__(self, enum=None, name=None, values=None):
        self.enum = enum
        if enum:
            self.name = enum.__name__
            self.values = list(enum.values())
        else:
            self.name = name
            self.values = values
        if self.name:
            self.name = 'ck%s' % re.sub(
                '([A-Z][^A-Z]|[A-Z]+(?=[A-Z][^A-Z]))',
                lambda m: '_' + m.group(1).lower(),
                self.name)
        self.impl = types.Enum(*self.values, name=self.name)

    def update_impl(self):
        if self.enum:
            self.values = list(self.enum.values())
        self.impl = types.Enum(*self.values, name=self.name)

    def load_dialect_impl(self, dialect):
        if _is_mysql(dialect):
            return mysql.ENUM(*self.values,
                              charset='ascii',
                              collation='ascii_bin')
        return self.impl

    def _set_table(self, column, table):
        self.impl._set_table(column, table)

    @property
    def python_type(self):
        return EnumSymbol

    def copy(self):
        return DeclEnumType(enum=self.enum, name=self.name, values=self.values)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, EnumSymbol):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, (bytes, bytearray)):
            value = value.decode('ascii')
        if isinstance(value, str):
            value = value.strip()
            if self.enum:
                return self.enum.from_string(value)
        return value

    def coerce_compared_value(self, op, value):
        if isinstance(value, str):
            return ASCIIString()
        return self

    class comparator_factory(types.Enum.Comparator):
        def in_(self, other):
            if isinstance(other, collections.Iterable):
                ret = []
                for elem in other:
                    if isinstance(elem, EnumSymbol):
                        elem = type_coerce(elem, DeclEnum)
                    ret.append(elem)
                other = ret
            return types.Enum.Comparator.in_(self, other)

    def process_literal_param(self, value, dialect):
        if isinstance(value, EnumSymbol):
            return value.value
        return value


def render_variants(query):
    ret = {}
    for dcls in _D_STD:
        dialect = dcls()
        ret[dialect.name] = str(query.statement.compile(
            compile_kwargs={'literal_binds': True},
            dialect=dialect))
    return ret
