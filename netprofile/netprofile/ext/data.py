#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: ExtJS schema and data generation
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
import importlib
import inspect
import ipaddress
import logging
import decimal

import datetime as dt
from dateutil.tz import tzlocal
from dateutil.parser import parse as dparse
from collections import (
    defaultdict,
    Iterable,
    Mapping,
    OrderedDict
)

from sqlalchemy import (
    BigInteger,
    BINARY,
    Boolean,
    CHAR,
    Date,
    DateTime,
    Enum,
    Float,
    Integer,
    LargeBinary,
    Numeric,
    PickleType,
    Sequence,
    SmallInteger,
    String,
    Time,
    TIMESTAMP,
    UnicodeText,
    VARBINARY,

    func,
    or_
)

from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.orm.interfaces import (
    ONETOMANY,
    MANYTOONE
)
from sqlalchemy.sql.functions import Function
from sqlalchemy.orm.attributes import QueryableAttribute
from pyramid.i18n import (
    TranslationString,
    TranslationStringFactory
)

from netprofile.db.fields import (
    ASCIIFixedString,
    ASCIIString,
    ASCIIText,
    ASCIITinyText,
    DeclEnum,
    DeclEnumType,
    EnumSymbol,
    ExactUnicode,
    Int8,
    Int16,
    Int32,
    Int64,
    IPv4Address,
    IPv6Address,
    IPv6Offset,
    JSONData,
    MACAddress,
    Money,
    NPBoolean,
    Traffic,
    UInt8,
    UInt16,
    UInt32,
    UInt64
)
from netprofile.db.connection import (
    Base,
    DBSession
)
from netprofile.ext.columns import (
    HybridColumn,
    PseudoColumn
)
from netprofile.tpl import TemplateObject

_ = TranslationStringFactory('netprofile')

_INTEGER_SET = (
    Int8,
    Int16,
    Int32,
    Int64,
    Integer,
    UInt8,
    UInt16,
    UInt32,
    UInt64
)

_FLOAT_SET = (
    Float,
)

_DECIMAL_SET = (
    IPv6Offset,
    Money,
    Numeric,
    Traffic
)

_STRING_SET = (
    ASCIIString,
    ASCIIFixedString,
    CHAR,
    DeclEnumType,
    ExactUnicode,
    String
)

_ASCII_STRING_SET = (
    ASCIIString,
    ASCIIFixedString,
    ASCIIText,
    ASCIITinyText,
    DeclEnumType
)

_BOOLEAN_SET = (
    Boolean,
    NPBoolean
)

_DATE_SET = (
    Date,
    DateTime,
    Time,
    TIMESTAMP
)

_IPADDR_SET = (
    IPv4Address,
    IPv6Address
)

_BINARY_SET = (
    BINARY,
    LargeBinary,
    VARBINARY
)

_NUMBER_SET = _INTEGER_SET + _FLOAT_SET + _DECIMAL_SET

_COLUMN_XTYPE_MAP = {
    BigInteger:   'numbercolumn',  # ?
    Boolean:      'checkcolumn',
    DeclEnumType: 'enumcolumn',
    Enum:         'enumcolumn',
    Float:        'numbercolumn',
    Int8:         'numbercolumn',
    Int16:        'numbercolumn',
    Int32:        'numbercolumn',
    Int64:        'numbercolumn',  # ?
    Integer:      'numbercolumn',
    IPv6Offset:   'numbercolumn',
    Money:        'numbercolumn',  # ?
    NPBoolean:    'checkcolumn',
    Numeric:      'numbercolumn',  # ?
    SmallInteger: 'numbercolumn',
    TIMESTAMP:    'datecolumn',
    Traffic:      'numbercolumn',  # ?
    UInt8:        'numbercolumn',
    UInt16:       'numbercolumn',
    UInt32:       'numbercolumn',
    UInt64:       'numbercolumn'  # ?
}

_EDITOR_XTYPE_MAP = {
    ASCIITinyText: 'textareafield',
    ASCIIText:     'textareafield',
    BigInteger:    'numberfield',  # ?
    Boolean:       'checkbox',
    Date:          'datefield',
    DateTime:      'datetimefield',
    DeclEnumType:  'combobox',
    Enum:          'combobox',
    Float:         'numberfield',
    Int8:          'numberfield',
    Int16:         'numberfield',
    Int32:         'numberfield',
    Int64:         'numberfield',  # ?
    Integer:       'numberfield',
    IPv4Address:   'ipv4field',
    IPv6Address:   'ipv6field',
    IPv6Offset:    'numberfield',
    JSONData:      'proptreefield',
    LargeBinary:   'textareafield',
    MACAddress:    'hwaddrfield',
    Money:         'moneyfield',
    NPBoolean:     'checkbox',
    Numeric:       'numberfield',  # ?
    SmallInteger:  'numberfield',
    Time:          'timefield',
    TIMESTAMP:     'datetimefield',
    Traffic:       'numberfield',  # ?
    UInt8:         'numberfield',
    UInt16:        'numberfield',
    UInt32:        'numberfield',
    UInt64:        'numberfield',  # ?
    UnicodeText:   'textareafield'
}

# Default is 'string'
_JS_TYPE_MAP = {
    BigInteger:   'int',  # ?
    Boolean:      'boolean',
    Date:         'date',
    DateTime:     'date',
    Float:        'float',
    Money:        'float',  # ?
    NPBoolean:    'boolean',
    Numeric:      'float',  # ?
    Int8:         'int',
    Int16:        'int',
    Int32:        'int',
    Int64:        'int',  # ?
    Integer:      'int',
    IPv4Address:  'ipv4',
    IPv6Address:  'ipv6',
    IPv6Offset:   'int',  # ?
    JSONData:     'auto',
    PickleType:   'auto',
    SmallInteger: 'int',
    TIMESTAMP:    'date',
    Traffic:      'int',  # ?
    UInt8:        'int',
    UInt16:       'int',
    UInt32:       'int',
    UInt64:       'int'  # ?
}

# Default is 'string'
_FILTER_TYPE_MAP = {
    BigInteger:   'npnumber',  # ?
    Boolean:      'boolean',
    Date:         'npdate',
    DateTime:     'npdate',
    DeclEnumType: 'nplist',
    Float:        'npnumber',
    Money:        'npnumber',  # ?
    NPBoolean:    'boolean',
    Numeric:      'npnumber',  # ?
    Int8:         'npnumber',
    Int16:        'npnumber',
    Int32:        'npnumber',
    Int64:        'npnumber',  # ?
    Integer:      'npnumber',
    IPv4Address:  'ipv4',
    IPv6Address:  'ipv6',
    IPv6Offset:   'npnumber',  # ?
    JSONData:     'none',
    PickleType:   'none',
    SmallInteger: 'npnumber',
    # Time:         FIXME,
    TIMESTAMP:    'npdate',
    Traffic:      'npnumber',  # ?
    UInt8:        'npnumber',
    UInt16:       'npnumber',
    UInt32:       'npnumber',
    UInt64:       'npnumber'  # ?
}

_DATE_FMT_MAP = {
    Date:      'Y-m-d',
    DateTime:  'c',
    Time:      'H:i:s',
    TIMESTAMP: 'c'
}

logger = logging.getLogger(__name__)


def _name_to_class(xcname):
    if xcname in Base._decl_class_registry:
        return Base._decl_class_registry[xcname]
    raise KeyError(xcname)


def _table_to_class(tname):
    for cname, cls in Base._decl_class_registry.items():
        if getattr(cls, '__tablename__', None) == tname:
            mapper = getattr(cls, '__mapper__', None)
            if mapper and mapper.single:
                return mapper.base_mapper.class_
            return cls
    raise KeyError(tname)


def _recursive_update(dest, src, loc=None):
    for k, v in src.items():
        if isinstance(v, Mapping):
            dest[k] = _recursive_update(dest.get(k, {}), v, loc)
        elif isinstance(v, list):
            dest[k] = _recursive_update_list(dest.get(k, []), v, loc)
        elif v is None:
            if k in dest:
                del dest[k]
        elif loc and isinstance(v, TranslationString):
            dest[k] = loc.translate(v)
        else:
            dest[k] = v
    return dest


def _recursive_update_list(dest, src, loc=None):
    for val in src:
        if isinstance(val, Mapping):
            val = _recursive_update({}, val, loc)
        elif isinstance(val, list):
            val = _recursive_update_list([], val, loc)
        elif loc and isinstance(val, TranslationString):
            val = loc.translate(val)
        dest.append(val)
    return dest


def _get_aggregate_column(dialect, func_name, field, colname):
    if func_name == 'count_distinct':
        func_name = 'count'
        field = field.distinct()
    if func_name in ('min', 'max', 'avg', 'sum', 'count'):
        return getattr(func, func_name)(field).label(colname)
    raise ValueError('Invalid aggregate function name: %s' % (func_name,))


def _get_groupby_clause(dialect, gtype, field):
    if gtype in ('year', 'month', 'week', 'day', 'hour', 'minute'):
        return func.extract(gtype, field)
    raise ValueError('Invalid group-by clause name: %s' % (gtype,))


class ExtColumn(object):
    MIN_PIXELS = 40
    MAX_PIXELS = 300
    DEFAULT_PIXELS = 200

    def __init__(self, sqla_column, sqla_model):
        self.column = sqla_column
        self.model = sqla_model
        self.alias = None

    @property
    def name(self):
        if self.alias:
            return self.alias
        return self.column.name

    @property
    def __name__(self):
        return self.name

    @property
    def header_string(self):
        return self.column.info.get('header_string', self.column.doc)

    @property
    def help_text(self):
        return self.column.info.get('help_text', None)

    @property
    def column_name(self):
        return self.column.info.get('column_name', self.header_string)

    @property
    def column_width(self):
        return self.column.info.get('column_width', None)

    @property
    def column_flex(self):
        return self.column.info.get('column_flex', None)

    @property
    def column_resizable(self):
        return self.column.info.get('column_resizable', True)

    @property
    def multivalue(self):
        return self.column.info.get('multivalue', False)

    @property
    def cell_class(self):
        return self.column.info.get('cell_class', None)

    @property
    def filter_type(self):
        typecls = self.column.type.__class__
        return self.column.info.get('filter_type',
                                    _FILTER_TYPE_MAP.get(typecls, 'string'))

    @property
    def reader(self):
        return self.column.info.get('reader')

    @property
    def writer(self):
        return self.column.info.get('writer')

    @property
    def validator(self):
        return self.column.info.get('validator')

    @property
    def pass_request(self):
        return self.column.info.get('pass_request', False)

    @property
    def template(self):
        return self.column.info.get('template', None)

    @property
    def vtype(self):
        return self.column.info.get('vtype')

    @property
    def editor_config(self):
        return self.column.info.get('editor_config')

    @property
    def length(self):
        typecls = self.column.type.__class__
        if typecls is MACAddress:
            return 17
        if typecls is IPv6Address:
            return 39
        if typecls is JSONData:
            return self.MAX_PIXELS
        try:
            if typecls is DeclEnumType:
                xlen = 0
                for sym in self.column.type.enum:
                    if len(sym.description) > xlen:
                        xlen = len(sym.description)
                return xlen
            if issubclass(typecls, _BINARY_SET):
                return self.column.type.length * 2
            return self.column.type.length
        except AttributeError:
            if issubclass(typecls, Int8):
                return 4
            if issubclass(typecls, UInt8):
                return 3
            if issubclass(typecls, Int16):
                return 6
            if issubclass(typecls, UInt16):
                return 5
            if issubclass(typecls, Int32):
                return 11
            if issubclass(typecls, UInt32):
                return 10
            if issubclass(typecls, SmallInteger):
                if getattr(self.column.type, 'unsigned', False):
                    return 6
                return 5
            if issubclass(typecls, Integer):
                if getattr(self.column.type, 'unsigned', False):
                    return 11
                return 10
            if issubclass(typecls, BigInteger):
                return 20
            return None

    @property
    def pixels(self):
        pix = self.length
        if isinstance(pix, int) and pix > 0:
            pix *= 10
            pix = max(pix, self.MIN_PIXELS)
            pix = min(pix, self.MAX_PIXELS)
        else:
            pix = self.DEFAULT_PIXELS
        return pix

    @property
    def bit_length(self):
        typecls = self.column.type.__class__
        if issubclass(typecls, (Int8, UInt8)):
            return 8
        if issubclass(typecls, (Int16, UInt16, SmallInteger)):
            return 16
        if issubclass(typecls, (Int64, UInt64)):
            return 64
        if issubclass(typecls, (Int32, UInt32, Integer)):
            return 32

    @property
    def unsigned(self):
        typecls = self.column.type.__class__
        if issubclass(typecls, (UInt8, UInt16, UInt32, UInt64)):
            return True
        return getattr(self.column.type, 'unsigned', False)

    def default(self, req):
        dv = getattr(self.column, 'default', None)
        if dv is not None and not isinstance(dv, Sequence):
            if dv.is_callable:
                return dv.arg(None)
            val = dv.arg
            if isinstance(val, TranslationString):
                return req.localizer.translate(val)
            return val
        return None

    @property
    def column_xtype(self):
        cls = self.column.info.get('column_xtype')
        if cls is not None:
            return cls
        cls = self.column.type.__class__
        if cls in _COLUMN_XTYPE_MAP:
            return _COLUMN_XTYPE_MAP[cls]
        return None

    @property
    def editor_xtype(self):
        cls = self.column.info.get('editor_xtype')
        if cls is not None:
            return cls
        cls = self.column.type.__class__
        if cls in _EDITOR_XTYPE_MAP:
            return _EDITOR_XTYPE_MAP[cls]
        return 'textfield'

    @property
    def js_type(self):
        if self.multivalue:
            return 'auto'
        cls = self.column.type.__class__
        if cls in _JS_TYPE_MAP:
            return _JS_TYPE_MAP[cls]
        return 'string'

    def _set_min_max(self, conf):
        typecls = self.column.type.__class__
        vmin = self.column.info.get('min_value', None)
        vmax = self.column.info.get('max_value', None)
        if vmin is None:
            vmin = getattr(typecls, 'MIN_VALUE')
        if vmax is None:
            vmax = getattr(typecls, 'MAX_VALUE')
        if vmax is None:
            if issubclass(typecls, SmallInteger):
                if getattr(self.column.type, 'unsigned', False):
                    vmin = UInt16.MIN_VALUE
                    vmax = UInt16.MAX_VALUE
                else:
                    vmin = Int16.MIN_VALUE
                    vmax = Int16.MAX_VALUE
            elif issubclass(typecls, Integer):
                if getattr(self.column.type, 'unsigned', False):
                    vmin = UInt32.MIN_VALUE
                    vmax = UInt32.MAX_VALUE
                else:
                    vmin = Int32.MIN_VALUE
                    vmax = Int32.MAX_VALUE
        if vmin is not None:
            conf['minValue'] = vmin
            if vmin < 0:
                conf['allowNegative'] = True
            else:
                conf['allowNegative'] = False
        if vmax is not None:
            conf['maxValue'] = vmax

    @property
    def secret_value(self):
        return self.column.info.get('secret_value', False)

    @property
    def read_only(self):
        return self.column.info.get('read_only', False)

    @property
    def read_cap(self):
        return self.column.info.get('read_cap')

    @property
    def write_cap(self):
        return self.column.info.get('write_cap')

    def get_choices(self, req):
        ch = self.column.info.get('choices')
        if ch is None:
            return None
        if inspect.isclass(ch) and issubclass(ch, DeclEnum):
            ret = dict()
            for val in ch:
                descr = val.description
                if isinstance(descr, TranslationString):
                    descr = req.localizer.translate(descr)
                ret[val.value] = descr
            return ret
        elif callable(ch):
            ch = ch(self, req)
        return ch

    def get_secret_value(self, req):
        cap = self.secret_value
        if cap:
            return True
        cap = self.read_cap
        if cap and not req.has_permission(cap):
            return True
        return False

    def get_read_only(self, req):
        cap = self.read_only
        if cap:
            return True
        cap = self.write_cap
        if cap and not req.has_permission(cap):
            return True
        return False

    def __getattr__(self, attr):
        return getattr(self.column, attr)

    def parse_param(self, param):
        if self.multivalue and isinstance(param, (list, tuple)):
            return [self.parse_param(p) for p in param]
        typecls = self.column.type.__class__
        if param is None:
            return None
        if self.column.nullable and param == '':
            return None
        if issubclass(typecls, _BOOLEAN_SET):
            if type(param) is str:
                if param.lower() in {'true', '1', 'on'}:
                    return True
                return False
            return bool(param)
        if issubclass(typecls, _BINARY_SET):
            if isinstance(param, bytes):
                return param
            if isinstance(param, str):
                return binascii.unhexlify(param)
            return None
        if issubclass(typecls, _DECIMAL_SET):
            return decimal.Decimal(str(param))
        if typecls is DeclEnumType:
            if isinstance(param, EnumSymbol):
                return param
            if not param:
                return None
            return self.column.type.enum.from_string(param.strip())
        if issubclass(typecls, _DATE_SET):
            param = dparse(param)
            if param.tzinfo is not None:
                param = param.astimezone(tzlocal())
                param = param.replace(tzinfo=None)
            return param
        if issubclass(typecls, _IPADDR_SET):
            # TODO: Axe out this nonsense as soon as both IP fields
            #       are checked in.
            if isinstance(param, dict):
                if 'octets' in param:
                    param = param['octets']
                elif 'parts' in param:
                    param = [byte
                             for word
                             in param['parts']
                             for byte
                             in (word >> 8, word % 256)]
                elif 'value' in param:
                    param = param['value']
                else:
                    return None
                if isinstance(param, (list, tuple)):
                    param = bytes(param)
            elif isinstance(param, list):
                param = bytes(param)
            if issubclass(typecls, IPv4Address):
                return ipaddress.IPv4Address(param)
            if issubclass(typecls, IPv6Address):
                return ipaddress.IPv6Address(param)
            return None
        if issubclass(typecls, _INTEGER_SET):
            if param == '':
                return None
            return int(param)
        return param

    def get_model_validations(self):
        typecls = self.column.type.__class__
        ret = {}
        if not self.nullable:
            ret['presence'] = True
        if issubclass(typecls, _INTEGER_SET):
            rng = {}
            vmin = getattr(typecls, 'MIN_VALUE')
            vmax = getattr(typecls, 'MAX_VALUE')
            if vmax is None:
                if issubclass(typecls, SmallInteger):
                    if getattr(self.column.type, 'unsigned', False):
                        vmin = UInt16.MIN_VALUE
                        vmax = UInt16.MAX_VALUE
                    else:
                        vmin = Int16.MIN_VALUE
                        vmax = Int16.MAX_VALUE
                elif issubclass(typecls, Integer):
                    if getattr(self.column.type, 'unsigned', False):
                        vmin = UInt32.MIN_VALUE
                        vmax = UInt32.MAX_VALUE
                    else:
                        vmin = Int32.MIN_VALUE
                        vmax = Int32.MAX_VALUE
            if vmin is not None:
                rng['min'] = vmin
            if vmax is not None:
                rng['max'] = vmax
            if len(rng) > 0:
                ret['range'] = rng
        if issubclass(typecls, _STRING_SET):
            ll = {}
            val = self.length
            if val is not None:
                ll['max'] = val
            if not self.nullable:
                ll['min'] = 1
            if len(ll) > 0:
                ret['length'] = ll
        if typecls is DeclEnumType:
            ret['inclusion'] = {'list': self.column.type.enum.values()}
        return ret

    def get_editor_multivalue(self, req, cfg):
        mcfg = {'xtype': 'multifield'}
        if 'name' in cfg:
            mcfg['name'] = cfg['name']
            del cfg['name']
        if 'fieldLabel' in cfg:
            mcfg['fieldLabel'] = cfg['fieldLabel']
            del cfg['fieldLabel']
        if 'value' in cfg:
            mcfg['value'] = cfg['value']
            del cfg['value']
            if not isinstance(mcfg['value'], (list, tuple)):
                mcfg['value'] = [mcfg['value']]
        mcfg['templateCfg'] = cfg
        return mcfg

    def get_editor_cfg(self, req, initval=None, in_form=False):
        loc = req.localizer
        ed_xtype = self.editor_xtype
        if ed_xtype is None:
            return None
        choices = self.get_choices(req)
        if choices:
            ed_xtype = 'combobox'
        if ed_xtype == 'combobox' and self.column.nullable:
            ed_xtype = 'nullablecombobox'
        # TODO: Add check for read-only non-pk fields.
        if self.column.primary_key or len(self.column.foreign_keys) > 0:
            hret = {
                'xtype':      'hidden' if in_form else 'numberfield',
                'editable':   False,
                'allowBlank': self.nullable,
                'name':       self.name
            }
            if initval is not None:
                if isinstance(initval, int):
                    hret['value'] = initval
                elif (len(self.column.foreign_keys) > 0):
                    fk = self.column.foreign_keys.copy().pop()
                    ftable = fk.column.table
                    fclass = _table_to_class(ftable.name)
                    fprop = fclass.__mapper__.get_property_by_column(fk.column)
                    hret['value'] = getattr(initval, fprop.key, None)
            return hret
        conf = {
            'xtype':      ed_xtype,
            'allowBlank': self.nullable,
            'name':       self.name
        }
        typecls = self.column.type.__class__
        val = self.length
        if val is not None:
            conf['maxLength'] = val
        ro = self.get_read_only(req)
        if ro:
            conf['readOnly'] = True
        if choices:
            conf.update({
                'queryMode':      'local',
                'displayField':   'value',
                'valueField':     'id',
                'forceSelection': True,
                'store':          {
                    'xtype':  'simplestore',
                    'fields': ('id', 'value'),
                    'data':   [{'id': k, 'value': v}
                               for k, v
                               in choices.items()]
                }
            })
            if 'minLength' in conf:
                del conf['minLength']
            if 'maxLength' in conf:
                del conf['maxLength']
        val = self.default(req)
        if isinstance(val, Function):
            val = None
        if initval is not None:
            conf['value'] = initval
        elif val is not None or self.nullable:
            conf['value'] = val
        val = self.help_text
        if val is not None:
            conf['emptyText'] = val
        val = self.vtype
        if val is not None:
            conf['vtype'] = val
        if issubclass(typecls, _BOOLEAN_SET):
            conf.update({
                'inputValue':     'true',
                'uncheckedValue': 'false'
            })
            val = self.default(req)
            if isinstance(initval, bool) and initval:
                conf['checked'] = initval
            elif isinstance(val, bool) and val:
                conf['checked'] = True
        elif issubclass(typecls, _INTEGER_SET):
            conf.update({
                'allowDecimals': False
            })
            self._set_min_max(conf)
        elif issubclass(typecls, _DECIMAL_SET):
            conf.update({
                'allowDecimals': True if self.column.type.scale > 0 else False
            })
            if self.unsigned:
                conf['allowNegative'] = False
            else:
                conf['allowNegative'] = True
        elif typecls is DeclEnumType:
            if 'maxLength' in conf:
                del conf['maxLength']
            chx = []
            for sym in self.column.type.enum:
                chx.append({
                    'id':    sym.value,
                    'value': loc.translate(sym.description)
                })
            conf.update({
                'format':         'string',
                'displayField':   'value',
                'hiddenName':     self.name,
                'valueField':     'id',
                'queryMode':      'local',
                'editable':       False,
                'forceSelection': True,
                'store':          {
                    'xtype':  'simplestore',
                    'fields': ('id', 'value'),
                    'data':   chx
                }
            })
        elif issubclass(typecls, _DATE_SET):
            conf['submitFormat'] = _DATE_FMT_MAP[typecls]
            # FIXME: configurable formats
            init_fmt = None
            if issubclass(typecls, (DateTime, TIMESTAMP, Date)):
                if issubclass(typecls, Date):
                    init_fmt = '%d.%m.%Y'
                else:
                    conf['altFormats'] = 'c'
            if issubclass(typecls, Time):
                conf['format'] = 'H:i:s'
                init_fmt = '%H:%M:%S'
            if ('value' in conf) and isinstance(conf['value'], dt.datetime):
                if init_fmt is None:
                    conf['value'] = conf['value'].isoformat()
                else:
                    conf['value'] = conf['value'].strftime(init_fmt)
        if ed_xtype in ('tinymce_field', 'tinymce_textarea'):
            tinymce_cfg = {
                'theme':                  'modern',
                'schema':                 'html5',
                'language':               req.current_locale.language,
                'spellchecker_language':  req.current_locale.language,
                'spellchecker_languages': ','.join('%s=%s' % (
                    req.current_locale.languages[lang],
                    lang,
                ) for lang in req.locales),
                'plugins': [
                    'advlist', 'anchor', 'autolink', 'charmap', 'code',
                    'colorpicker', 'contextmenu', 'fullscreen', 'hr', 'image',
                    'insertdatetime', 'link', 'lists', 'media', 'nonbreaking',
                    'pagebreak', 'paste', 'preview', 'print', 'searchreplace',
                    'tabfocus', 'table', 'textcolor', 'visualblocks',
                    'visualchars', 'wordcount'
                ],
                'toolbar': [
                    ('undo redo | '
                     'print preview searchreplace | '
                     'styleselect | '
                     'bold italic underline strikethrough '
                     'forecolor backcolor | '
                     'alignleft aligncenter alignright alignjustify '
                     'subscript superscript | '
                     'fullscreen code'),
                    ('bullist numlist outdent indent | '
                     'image media | '
                     'link anchor | '
                     'table hr nonbreaking')
                ],
                'image_advtab': True
            }
            conf['tinyMCEConfig'] = tinymce_cfg
        if in_form:
            conf['fieldLabel'] = loc.translate(self.header_string)
            val = self.pixels
            if val is not None:
                conf['width'] = val + 125
                if (not choices
                        and 'xtype' in conf
                        and conf['xtype'] in {'numberfield',
                                              'combobox',
                                              'nullablecombobox'}):
                    conf['width'] += 30
        val = self.editor_config
        if val:
            _recursive_update(conf, val, req.localizer)
        return conf

    def get_reader_cfg(self, req):
        typecls = self.column.type.__class__
        conf = {
            'name':       self.name,
            'allowBlank': self.nullable,
            'allowNull':  self.nullable,
            'type':       self.js_type
        }
        if conf['type'] == 'date':
            conf['dateFormat'] = _DATE_FMT_MAP[typecls]
        val = self.default(req)
        if val is not None:
            if type(val) in {int, str, list, dict, bool}:
                conf['defaultValue'] = val
        fks = self.column.foreign_keys
        if self.model.__mapper__.polymorphic_on is not None:
            if self.model.__mapper__.polymorphic_on.name == self.name:
                conf.update({
                    'allowBlank':   False,
                    'allowNull':    False,
                    'defaultValue': self.model.__mapper__.polymorphic_identity
                })
        elif len(fks) == 1:
            fk = list(fks)[0]
            cls = _table_to_class(fk.column.table.name)
            conf['reference'] = 'NetProfile.model.{0}.{1}'.format(
                cls.__moddef__,
                cls.__name__)
        return conf

    def get_column_cfg(self, req):
        loc = req.localizer
        conf = {
            'header':     loc.translate(self.header_string),
            'tooltip':    loc.translate(self.column_name),
            'menuText':   loc.translate(self.column_name),
            'name':       self.name,
            'sortable':   True,
            'filterable': True,
            'dataIndex':  self.name
        }
        editor = self.get_editor_cfg(req)
        if self.multivalue:
            editor = self.get_editor_multivalue(req, editor)
        conf['editor'] = editor
        typecls = self.column.type.__class__
        xt = self.column_xtype
        if xt is not None:
            conf['xtype'] = xt
        if xt == 'checkcolumn':
            # FIXME: maybe selectively allow in-place editing?
            conf['readOnly'] = True
        tpl = self.template
        if tpl:
            if isinstance(tpl, TemplateObject):
                conf['tpl'] = tpl.render(req)
            else:
                conf['tpl'] = tpl
            if 'xtype' not in conf:
                conf['xtype'] = 'templatecolumn'
        cw = self.column_width
        if cw is not None:
            conf['width'] = cw
        cw = self.column_flex
        if cw is not None:
            conf['flex'] = cw
        cw = self.column_resizable
        if isinstance(cw, bool):
            conf['resizable'] = cw
            if not cw and 'width' in conf:
                conf['minWidth'] = conf['maxWidth'] = conf['width']
        cw = self.cell_class
        if cw is not None:
            conf['tdCls'] = cw
        ftype = self.filter_type
        filter_conf = None
        if ftype == 'none':
            conf['filterable'] = False
        else:
            filter_conf = {'type': ftype}
        choices = self.get_choices(req)
        if not choices:
            if issubclass(typecls, _DECIMAL_SET):
                conf.update({
                    'align':  'right',
                    'format': '0.00' if self.column.type.scale > 0 else '0'
                })
            if issubclass(typecls, _INTEGER_SET):
                conf.update({
                    'align':  'right',
                    'format': '0'
                })
        if issubclass(typecls, _DATE_SET):
            def_width = 80
            # FIXME: configurable formats
            if issubclass(typecls, (DateTime, TIMESTAMP)):
                conf['format'] = loc.translate(_('Y-m-d H:i:s'))
                def_width = 115
            if issubclass(typecls, Date):
                conf['format'] = loc.translate(_('Y-m-d'))
            if issubclass(typecls, Time):
                conf['format'] = loc.translate(_('H:i:s'))
                def_width = 70
            if 'width' not in conf:
                conf['width'] = def_width
        if filter_conf:
            conf['filter'] = filter_conf
        if typecls is DeclEnumType:
            chx = {}
            chf = []
            for sym in self.column.type.enum:
                tdescr = loc.translate(sym.description)
                chx[sym.value] = tdescr
                chf.append({'id': sym.value, 'value': tdescr})
            if 'filter' in conf and conf['filter']['type'] == 'nplist':
                conf['valueMap'] = chx
                conf['filter'].update({
                    'idField':    'id',
                    'labelField': 'value',
                    'options':    chf
                })
        if choices:
            chx = {}
            chf = []
            for k, v in choices.items():
                chx[k] = v
                chf.append({'id': k, 'value': v})
            conf.update({
                'xtype':    'enumcolumn',
                'valueMap': chx,
                'filter':   {
                    'type':       'nplist',
                    'idField':    'id',
                    'labelField': 'value',
                    'options':    chf
                }
            })
        return conf

    def append_data(self, obj):
        pass

    def append_field(self):
        pass

    def apply_data(self, obj, data):
        pass

    def get_aggregates(self):
        if self.column.primary_key or len(self.column.foreign_keys) > 0:
            return None
        ret = ['count', 'count_distinct']
        typecls = self.column.type.__class__
        if issubclass(typecls, _NUMBER_SET):
            ret.extend(('min', 'max', 'avg', 'sum'))
        elif issubclass(typecls, _DATE_SET):
            ret.extend(('min', 'max', 'avg'))
        return ret

    def get_groupby_groups(self):
        if self.column.primary_key:
            return False
        if len(self.column.foreign_keys) > 0 and self.filter_type != 'nplist':
            return False
        ret = True
        typecls = self.column.type.__class__
        if issubclass(typecls, _DATE_SET):
            ret = ['year', 'month', 'week', 'day', 'hour', 'minute']
        return ret


class ExtPseudoColumn(ExtColumn):
    @property
    def reader(self):
        return None

    @property
    def writer(self):
        return None

    @property
    def validator(self):
        return None

    @property
    def length(self):
        return None

    @property
    def pixels(self):
        return self.MAX_PIXELS

    @property
    def bit_length(self):
        return None

    @property
    def unsigned(self):
        return False

    def default(self, req):
        return None

    @property
    def editor_xtype(self):
        return self.column.editor_xtype

    @property
    def js_type(self):
        return self.column.js_type

    def _set_min_max(self, conf):
        # FIXME: add smth here
        raise NotImplementedError('Validation support is missing '
                                  'for pseudo columns.')

    def __getattr__(self, attr):
        return getattr(self.column, attr)

    def parse_param(self, param):
        if not hasattr(self.column.info, 'parse'):
            return param
        if not callable(self.column.parse):
            return param
        return self.column.parse(param)

    def get_model_validations(self):
        # FIXME: add smth here
        raise NotImplementedError('Validation support is missing '
                                  'for pseudo columns.')
        return {}

    def get_editor_cfg(self, req, initval=None, in_form=False):
        # FIXME: add smth here
        return None

    def get_reader_cfg(self, req):
        return None

    def get_column_cfg(self, req):
        loc = req.localizer
        conf = {
            'header':     loc.translate(self.column.header_string),
            'tooltip':    loc.translate(self.column.column_name),
            'menuText':   loc.translate(self.column.column_name),
            'name':       self.name,
            'sortable':   self.sortable,
            'filterable': (False
                           if self.column.filter_type == 'none'
                           else True),
            'dataIndex':  self.name,
            'editor':     self.get_editor_cfg(req),
            'xtype':      self.column.column_xtype
        }
        if not conf['sortable'] and not conf['filterable']:
            conf['menuDisabled'] = True
        tpl = self.column.template
        if tpl:
            if isinstance(tpl, TemplateObject):
                conf['tpl'] = tpl.render(req)
            else:
                conf['tpl'] = tpl
            conf['xtype'] = 'templatecolumn'
        cw = self.column_width
        if cw is not None:
            conf['width'] = cw
        cw = self.column_flex
        if cw is not None:
            conf['flex'] = cw
        cw = self.column_resizable
        if isinstance(cw, bool):
            conf['resizable'] = cw
            if not cw and 'width' in conf:
                conf['minWidth'] = conf['maxWidth'] = conf['width']
        cw = self.cell_class
        if cw is not None:
            conf['tdCls'] = cw
        return conf

    def append_data(self, obj):
        pass

    def append_field(self):
        pass

    def apply_data(self, obj, data):
        pass

    def get_aggregates(self):
        return None

    def get_groupby_groups(self):
        return False


class ExtRelationshipColumn(ExtColumn):
    def __init__(self, sqla_prop, sqla_model):
        self.prop = sqla_prop
        self.column = sqla_prop.local_columns.copy().pop()
        self.model = sqla_model
        self.value_attr = None

    @property
    def filter_type(self):
        return self.column.info.get('filter_type', 'none')

    def get_column_cfg(self, req):
        conf = super(ExtRelationshipColumn, self).get_column_cfg(req)
        conf['dataIndex'] = self.prop.key
        if 'align' in conf:
            del conf['align']
        return conf

    def get_aggregates(self):
        return None

    def get_groupby_groups(self):
        return False


class ExtManyToOneRelationshipColumn(ExtRelationshipColumn):
    @property
    def column_xtype(self):
        return None

    def append_data(self, obj):
        k = self.prop.key
        data = getattr(obj, k)
        if (data is not None) and hasattr(obj, '__req__'):
            data.__req__ = obj.__req__
        if self.value_attr:
            data = getattr(data, self.value_attr, data)
        if data is not None:
            return {k: str(data)}
        return dict()

    def append_field(self):
        return self.column.name

    def get_related_by_value(self, value):
        relcol = self.prop.remote_side.copy().pop()
        relcls = _table_to_class(self.prop.target.name)
        relprop = relcls.__mapper__.get_property_by_column(relcol)

        sess = DBSession()
        return sess.query(relcls).filter(
                getattr(relcls, relprop.key) == value).one()

    def get_column_cfg(self, req):
        conf = super(ExtManyToOneRelationshipColumn, self).get_column_cfg(req)

        ftype = self.filter_type
        if ftype == 'nplist':
            rcol = self.prop.remote_side.copy().pop()
            if rcol is not None:
                rmodel = _table_to_class(rcol.table.name)
                if rmodel is not None:
                    conf['filter'] = {
                        'type':       'nplist',
                        'optStore':   'NetProfile.store.{0}.{1}'.format(
                                          rmodel.__moddef__, rmodel.__name__),
                        'idField':    rcol.name,
                        'labelField': '__str__'
                    }

        return conf

    def get_editor_cfg(self, req, initval=None, in_form=False):
        conf = super(ExtManyToOneRelationshipColumn,
                     self).get_editor_cfg(req,
                                          initval=initval,
                                          in_form=in_form)
        if conf is None:
            return None
        conf['name'] = self.prop.key
        if len(self.column.foreign_keys) > 0:
            fk = self.column.foreign_keys.copy().pop()
            cls = _table_to_class(fk.column.table.name)
            xtype = 'modelselect'
            if 'editor_xtype' in self.column.info:
                xtype = self.column.info['editor_xtype']
            conf.update({
                'xtype':       xtype,
                'apiModule':   cls.__moddef__,
                'apiClass':    cls.__name__,
                'disabled':    False,
                'editable':    False,
                'hiddenField': self.name
            })
            if self.get_read_only(req):
                conf.update({
                    'readOnly': True
                })
            if in_form:
                loc = req.localizer
                conf['fieldLabel'] = loc.translate(self.header_string)
                val = self.pixels
                conf['width'] = self.MAX_PIXELS + 125
            if initval is not None:
                conf['value'] = str(initval)
        val = self.editor_config
        if val:
            _recursive_update(conf, val, req.localizer)
        return conf

    def get_reader_cfg(self, req):
        return {
            'name':       self.prop.key,
            'allowBlank': self.nullable,
            'allowNull':  self.nullable,
            'type':       'string',
            'persist':    False
        }

    def get_aggregates(self):
        if self.filter_type == 'nplist':
            return ['count', 'count_distinct']
        return None


class ExtOneToManyRelationshipColumn(ExtRelationshipColumn):
    @property
    def columns(self):
        return self.prop.info.get('columns', 2)

    def append_field(self):
        return None

    def append_data(self, obj):
        k = self.prop.key
        data = getattr(obj, k)
        newdata = []
        for i in data:
            if self.value_attr:
                i = getattr(i, self.value_attr, None)
            if i.__class__:
                i = i.__class__.__mapper__.primary_key_from_instance(i)
                if len(i) > 0:
                    newdata.append(i[0])
        return {self.name: newdata}

    def apply_data(self, obj, data):
        cont = getattr(obj, self.name)
        if data is None:
            return
        for relobj in data:
            if relobj not in cont:
                cont.append(relobj)
        for relobj in cont:
            if relobj not in data:
                cont.remove(relobj)

    def get_editor_cfg(self, req, initval=None, in_form=False):
        loc = req.localizer
        relcls = _table_to_class(self.prop.target.name)
        if self.value_attr:
            relcls = getattr(relcls, self.value_attr).property.mapper.class_
        relname = relcls.__table__.info.get('menu_name', self.header_string)
        relpk = relcls.__mapper__.primary_key
        if len(relpk) > 0:
            relpk = relpk[0]
            relprop = relcls.__mapper__.get_property_by_column(relpk)
        conf = {
            'xtype':          'dyncheckboxgroup',
            'allowBlank':     True,
            'name':           self.name,
            'columns':        self.columns,
            'vertical':       True,
            'store':          'NetProfile.store.%s.%s' % (
                                  relcls.__moddef__,
                                  relcls.__name__),
            'valueField':     relpk.name,
            'formCheckboxes': False
        }
        if in_form:
            conf['fieldLabel'] = loc.translate(relname)
        if (initval is not None) and relprop:
            conf['value'] = [getattr(el, relprop.key) for el in initval]
        val = self.editor_config
        if val:
            conf.update(val)
        return conf

    def get_reader_cfg(self, req):
        return {
            'name':       self.name,
            'allowBlank': True,
            'allowNull':  True,
            'type':       'auto'
        }

    def get_related_by_value(self, value):
        if not isinstance(value, list):
            return None
        if len(value) == 0:
            return []
        relcls = _table_to_class(self.prop.target.name)
        if self.value_attr:
            relcls = getattr(relcls, self.value_attr).property.mapper.class_
        relprop = relcls.__mapper__.primary_key
        if len(relprop) > 0:
            relprop = relprop[0]
            relprop = relcls.__mapper__.get_property_by_column(relprop)

        sess = DBSession()
        return sess.query(relcls).filter(
                getattr(relcls, relprop.key).in_(value)).all()

    def parse_param(self, param):
        return self.get_related_by_value(param)


class ExtModel(object):
    def __init__(self, sqla_model):
        self.model = sqla_model
        self.u_idx = []
        for tbl in sqla_model.__mapper__.tables:
            for idx in tbl.indexes:
                if not idx.unique:
                    continue
                self.u_idx.append([c.name for c in idx.columns])

    @property
    def name(self):
        return self.model.__name__

    @property
    def __name__(self):
        return self.name

    @property
    def pk(self):
        pkcon = getattr(self.model.__table__, 'primary_key', None)
        if pkcon is None:
            return None
        for col in pkcon:
            return col.name
        return None

    @property
    def object_pk(self):
        pkcol = getattr(self.model.__mapper__, 'primary_key', None)
        if pkcol is None or len(pkcol) == 0:
            return None
        pkprop = self.model.__mapper__.get_property_by_column(pkcol[0])
        if pkprop:
            return pkprop.key

    @property
    def is_tree(self):
        return ('tree_property' in self.model.__table__.info)

    @property
    def is_polymorphic(self):
        root_mapper = self.model.__mapper__
        if root_mapper.polymorphic_on is None:
            return False
        for submap in root_mapper.polymorphic_map.values():
            if submap.tables != root_mapper.tables:
                return True
        return False

    @property
    def easy_search(self):
        return self.model.__table__.info.get('easy_search', ())

    @property
    def default_sort(self):
        return self.model.__table__.info.get('default_sort', ())

    @property
    def extra_search(self):
        return self.model.__table__.info.get('extra_search', ())

    @property
    def show_in_menu(self):
        return self.model.__table__.info.get('show_in_menu', False)

    @property
    def menu_name(self):
        return self.model.__table__.info.get('menu_name', self.model.__name__)

    @property
    def menu_section(self):
        return self.model.__table__.info.get('menu_section')

    @property
    def menu_parent(self):
        return self.model.__table__.info.get('menu_parent')

    @property
    def menu_main(self):
        return self.model.__table__.info.get('menu_main', False)

    @property
    def cap_menu(self):
        return self.model.__table__.info.get('cap_menu')

    @property
    def cap_read(self):
        return self.model.__table__.info.get('cap_read')

    @property
    def cap_create(self):
        return self.model.__table__.info.get('cap_create')

    @property
    def cap_edit(self):
        return self.model.__table__.info.get('cap_edit')

    @property
    def cap_delete(self):
        return self.model.__table__.info.get('cap_delete')

    @property
    def detail_pane(self):
        return self.model.__table__.info.get('detail_pane')

    @property
    def create_wizard(self):
        return self.model.__table__.info.get('create_wizard')

    @property
    def wizards(self):
        return self.model.__table__.info.get('wizards')

    @property
    def grid_hidden(self):
        return self.model.__table__.info.get('grid_hidden', ())

    @property
    def grid_view(self):
        return self.model.__table__.info.get('grid_view', ())

    @property
    def form_view(self):
        return self.model.__table__.info.get(
            'form_view',
            self.model.__table__.info.get('grid_view', ()))

    @property
    def export_view(self):
        return self.model.__table__.info.get(
            'export_view',
            self.model.__table__.info.get('grid_view', ()))

    @property
    def extra_data(self):
        return self.model.__table__.info.get('extra_data', ())

    @property
    def row_class_field(self):
        return self.model.__table__.info.get('row_class_field')

    def get_extra_actions(self, req):
        extra = list(self.model.__table__.info.get('extra_actions', []))
        req.run_hook('np.model.actions', extra, req, self)
        req.run_hook('np.model.actions.%s.%s' % (self.model.__moddef__,
                                                 self.name),
                     extra, req, self)
        return extra

    def get_column(self, colname):
        if isinstance(colname, PseudoColumn):
            return ExtPseudoColumn(colname, self.model)
        cols = self.model.__table__.columns
        o_prop = getattr(self.model, colname, None)
        if isinstance(o_prop, AssociationProxy):
            ret = self.get_column(o_prop.local_attr.key)
            ret.alias = colname
            ret.value_attr = o_prop.value_attr
            return ret
        if isinstance(o_prop, QueryableAttribute):
            prop = o_prop.property
            pdir = getattr(prop, 'direction', None)
            if pdir == MANYTOONE:
                return ExtManyToOneRelationshipColumn(prop, self.model)
            if pdir == ONETOMANY:
                return ExtOneToManyRelationshipColumn(prop, self.model)
            if len(o_prop.property.columns) > 0:
                ret = ExtColumn(o_prop.property.columns[0], self.model)
                ret.alias = colname
                return ret
            raise ValueError('Unknown type of column %s' % colname)
        if self.is_polymorphic:
            for tbl in self.model.__mapper__.tables:
                if colname in tbl.columns:
                    return ExtColumn(tbl.columns[colname], self.model)
        elif colname in cols:
            return ExtColumn(cols[colname], self.model)
        raise ValueError('Unknown type of column %s' % colname)

    def get_columns(self):
        ret = OrderedDict()
        for tbl in self.model.__mapper__.tables:
            for ck in tbl.columns.keys():
                ret[ck] = ExtColumn(tbl.columns[ck], self.model)
        return ret

    def get_read_columns(self):
        ret = OrderedDict()
        cols = []
        for tbl in self.model.__mapper__.tables:
            cols.extend(tbl.columns.keys())
        try:
            gcols = self.model.__table__.info['grid_view']
            for col in gcols:
                if col in cols:
                    continue
                cols.append(col)
        except KeyError:
            pass
        try:
            fcols = self.model.__table__.info['form_view']
            for col in fcols:
                if col in cols:
                    continue
                cols.append(col)
        except KeyError:
            pass
        pk = self.pk
        if pk not in cols:
            ret[pk] = self.get_column(pk)
        for col in cols:
            ret[col] = self.get_column(col)
        return ret

    def get_form_columns(self):
        ret = OrderedDict()
        fcols = self.form_view
        pk = self.pk
        if pk not in fcols:
            ret[pk] = self.get_column(pk)
        for fcol in fcols:
            ret[fcol] = self.get_column(fcol)
            extra = ret[fcol].append_field()
            if extra and extra not in ret:
                ret[extra] = self.get_column(extra)
        return ret

    def get_column_cfg(self, req):
        ret = []
        hidden = self.grid_hidden
        try:
            cols = self.model.__table__.info['grid_view']
        except KeyError:
            cols = self.model.__table__.columns.keys()
        for col in cols:
            column = self.get_column(col)
            cdef = column.get_column_cfg(req)
            if cdef is not None:
                if col in hidden:
                    cdef['hidden'] = True
                if isinstance(column, ExtPseudoColumn):
                    cdef['allowMarkup'] = True
                ret.append(cdef)
        return ret

    def get_reader_cfg(self, req):
        ret = []
        str_added = False
        for cname, col in self.get_read_columns().items():
            cfg = col.get_reader_cfg(req)
            if cfg is None:
                continue
            if cfg['name'] == '__str__':
                str_added = True
            ret.append(cfg)
        if not str_added:
            ret.append({
                'name':       '__str__',
                'allowBlank': True,
                'allowNull':  True,
                'type':       'string',
                'persist':    False
            })
        if self.is_polymorphic:
            ret.append({
                'name':       '__poly',
                'allowBlank': True,
                'allowNull':  True,
                'type':       'auto',
                'persist':    False
            })
        for extra in self.extra_data:
            ret.append({
                'name':       extra,
                'allowBlank': True,
                'allowNull':  True,
                'type':       'auto',
                'persist':    False
            })
        return ret

    def get_extra_search_cfg(self, req):
        xs = self.extra_search
        if xs is not None:
            ret = []
            for xf in xs:
                ret.append(xf.get_cfg(req))
            return ret

    def get_model_validations(self):
        ret = []
        for cname, col in self.get_read_columns().items():
            if isinstance(col, ExtRelationshipColumn):
                continue
            v = col.get_model_validations()
            # <- INSERT CUSTOM VALIDATORS HERE
            for vkey, vdata in v.items():
                vitem = {'field': cname, 'type':  vkey}
                if isinstance(vdata, dict):
                    vitem.update(vdata)
                ret.append(vitem)
        return ret

    def get_aggregates(self, req):
        ret = []
        loc = req.localizer
        for cname, col in self.get_read_columns().items():
            agg = col.get_aggregates()
            if agg is None:
                continue
            ret.append({
                'name':  cname,
                'title': loc.translate(col.header_string),
                'func':  agg
            })
        return ret

    def get_groupby_groups(self, req):
        ret = []
        loc = req.localizer
        for cname, col in self.get_read_columns().items():
            grp = col.get_groupby_groups()
            if not grp:
                continue
            grpdict = {
                'name':  cname,
                'title': loc.translate(col.header_string)
            }
            if grp is not True:
                grpdict['func'] = grp
            ret.append(grpdict)
        return ret

    def _apply_pagination(self, query, trans, params):
        if '__start' in params:
            val = int(params['__start'])
            if val > 0:
                query = query.offset(val)
        if '__limit' in params:
            val = int(params['__limit'])
            if val > 0:
                query = query.limit(val)
        return query

    def _apply_sorting(self, query, trans, params):
        slist = params['__sort']
        if not isinstance(slist, list):
            return query
        for sdef in slist:
            if not isinstance(sdef, dict) or len(sdef) != 2:
                continue
            if sdef['property'] not in trans:
                continue
            prop = getattr(self.model, trans[sdef['property']].key)
            if sdef['direction'] == 'DESC':
                prop = prop.desc()
            query = query.order_by(prop)
        return query

    def _apply_sstr(self, query, trans, params):
        fields = self.easy_search
        if len(fields) == 0:
            return query
        sstr = params['__sstr']
        cond = []
        is_ascii = True
        try:
            sstr.encode('ascii')
        except UnicodeEncodeError:
            is_ascii = False
        for f in fields:
            prop = trans[f]
            coldef = self.model.__mapper__.c[prop.key]
            col = getattr(self.model, prop.key)
            colcls = coldef.type.__class__
            if issubclass(colcls, _STRING_SET):
                if not is_ascii and issubclass(colcls, _ASCII_STRING_SET):
                    continue
                cond.append(col.contains(sstr))
        if len(cond) > 0:
            query = query.filter(or_(*cond))
        return query

    def _apply_xfilters(self, query, params, pname='__xfilter'):
        xs = self.extra_search
        if len(xs) == 0:
            return query
        flist = params[pname]
        for xf in xs:
            if xf.name in flist:
                query = xf.process(self.model, query, flist[xf.name])
        return query

    def _apply_filters(self, query, trans, params, pname='__filter'):
        flist = params[pname]
        for fltr in flist:
            fcol = fltr.get('property', None)
            operator = fltr.get('operator', 'eq')
            value = fltr.get('value', None)
            if fcol in trans:
                prop = trans[fcol]
                coldef = self.model.__mapper__.c[prop.key]
                colcls = coldef.type.__class__
                col = getattr(self.model, prop.key)
                extcol = self.get_column(fcol)

                if isinstance(value, list):
                    if operator == 'in':
                        query = query.filter(col.in_(value))
                        continue
                    if operator == 'notin':
                        query = query.filter(not col.in_(value))
                        continue
                    # FIXME: parse_param chokes on list values
                    continue

                value = extcol.parse_param(value)
                if operator in ('eq', '=', '==', '==='):
                    query = query.filter(col == value)
                    continue
                if operator in ('ne', '!=', '!=='):
                    query = query.filter(col != value)
                    continue
                if issubclass(colcls, _DATE_SET):
                    if value.tzinfo is not None:
                        value = value.astimezone(tzlocal())
                    if value is None:
                        continue
                    if operator in ('gt', '>'):
                        query = query.filter(col > value)
                    if operator in ('lt', '<'):
                        query = query.filter(col < value)
                    if operator in ('ge', '>='):
                        query = query.filter(col >= value)
                    if operator in ('le', '<='):
                        query = query.filter(col <= value)
                    continue
                if (issubclass(colcls, _INTEGER_SET)
                        or issubclass(colcls, _DECIMAL_SET)
                        or issubclass(colcls, _IPADDR_SET)):
                    if value is None:
                        continue
                    if operator in ('gt', '>'):
                        query = query.filter(col > value)
                    if operator in ('lt', '<'):
                        query = query.filter(col < value)
                    if operator in ('ge', '>='):
                        query = query.filter(col >= value)
                    if operator in ('le', '<='):
                        query = query.filter(col <= value)
                    continue
                if issubclass(colcls, _STRING_SET):
                    if value is None:
                        continue
                    if operator in ('contains', 'like'):
                        query = query.filter(col.contains(value))
                    if operator in ('ncontains', 'notlike'):
                        query = query.filter(not col.contains(value))
                    if operator == 'startswith':
                        query = query.filter(col.startswith(value))
                    if operator == 'nstartswith':
                        query = query.filter(not col.startswith(value))
                    if operator == 'endswith':
                        query = query.filter(col.endswith(value))
                    if operator == 'nendswith':
                        query = query.filter(not col.endswith(value))
                    continue
        return query

    def _get_trans(self, cols):
        trans = {}
        for cname, col in cols.items():
            if isinstance(col, ExtPseudoColumn):
                continue
            trans[cname] = self.model.__mapper__.get_property_by_column(
                    col.column)
        return trans

    def read(self, params, request):
        logger.debug('Running API call, class:%s method:read params:%r',
                     self.name, params)
        res = {
            'records': [],
            'success': True,
            'total':   0
        }
        records = []
        tot = 0
        cols = self.get_read_columns()
        trans = self._get_trans(cols)
        sess = DBSession()
        # Cache total?
        q = sess.query(func.count('*')).select_from(self.model)
        if '__ffilter' in params:
            q = self._apply_filters(q, trans, params, pname='__ffilter')
        if '__filter' in params:
            q = self._apply_filters(q, trans, params)
        if '__xfilter' in params:
            q = self._apply_xfilters(q, params)
        if '__sstr' in params:
            q = self._apply_sstr(q, trans, params)
        tot = q.scalar()
        q = sess.query(self.model)
        if '__ffilter' in params:
            q = self._apply_filters(q, trans, params, pname='__ffilter')
        if '__filter' in params:
            q = self._apply_filters(q, trans, params)
        if '__xfilter' in params:
            q = self._apply_xfilters(q, params)
        if '__sstr' in params:
            q = self._apply_sstr(q, trans, params)
        if '__sort' in params:
            q = self._apply_sorting(q, trans, params)
        helper = getattr(self.model, '__augment_query__', None)
        if callable(helper):
            q = helper(sess, q, params, request)
        q = self._apply_pagination(q, trans, params)
        helper = getattr(self.model, '__augment_pg_query__', None)
        if callable(helper):
            q = helper(sess, q, params, request)
        helper = getattr(self.model, '__augment_result__', None)
        if callable(helper):
            q = helper(sess, q.all(), params, request)
        if params.get('__empty', False):
            row = {}
            for cname, col in cols.items():
                if isinstance(cname, PseudoColumn):
                    if col.get_secret_value(request):
                        continue
                    if isinstance(cname, HybridColumn):
                        row[cname.name] = None
                    continue
                if col.get_secret_value(request):
                    continue
                if trans[cname].deferred:
                    continue
                if isinstance(col, ExtRelationshipColumn):
                    continue
                row[cname] = ''
            row['__str__'] = ''
            records.append(row)
        for obj in q:
            obj.__req__ = request
            row = {}
            for cname, col in cols.items():
                if isinstance(cname, PseudoColumn):
                    if col.get_secret_value(request):
                        continue
                    if isinstance(cname, HybridColumn):
                        row[cname.name] = getattr(obj, cname.name)
                    continue
                if col.get_secret_value(request):
                    continue
                if trans[cname].deferred:
                    continue
                if isinstance(col, ExtRelationshipColumn):
                    extra = col.append_data(obj)
                    if extra is not None:
                        row.update(extra)
                else:
                    reader = col.reader
                    if reader:
                        reader = getattr(obj, reader, None)
                        if callable(reader):
                            if col.pass_request:
                                row[cname] = reader(params, request)
                            else:
                                row[cname] = reader(params)
                        else:
                            row[cname] = reader
                    else:
                        row[cname] = getattr(obj, trans[cname].key)
            row['__str__'] = str(obj)
            if self.is_polymorphic:
                row['__poly'] = (obj.__class__.__moddef__,
                                 obj.__class__.__name__)
            for extra in self.extra_data:
                edata = getattr(obj, extra, None)
                if callable(edata):
                    row[extra] = edata(request)
                else:
                    row[extra] = edata
            request.run_hook('np.object.read', obj, row, params, request, self)
            records.append(row)
        res['records'] = records
        res['total'] = tot
        return res

    def read_one(self, params, request):
        logger.debug('Running API call, class:%s method:read_one params:%r',
                     self.name, params)
        raise NotImplementedError('read_one() not implemented')

    def set_values(self, obj, values, request, is_create=False):
        obj.__req__ = request
        cols = self.get_columns()
        rcols = self.get_read_columns()
        trans = self._get_trans(rcols)
        helper = None
        if is_create:
            helper = getattr(self.model, '__augment_create__', None)
        else:
            helper = getattr(self.model, '__augment_update__', None)
        if callable(helper) and not helper(DBSession(), obj, values, request):
            return
        for p, val in values.items():
            if p not in cols:
                if (p in rcols
                        and isinstance(rcols[p],
                                       ExtOneToManyRelationshipColumn)):
                    cols[p] = rcols[p]
                else:
                    continue
            if cols[p].get_read_only(request):
                continue
            choices = cols[p].get_choices(request)
            if choices:
                chosen_val = cols[p].parse_param(val)
                if chosen_val not in choices:
                    continue
            writer = cols[p].writer
            if writer:
                writer = getattr(obj, writer, None)
                if callable(writer):
                    if cols[p].pass_request:
                        writer(cols[p].parse_param(val), values, request)
                    else:
                        writer(cols[p].parse_param(val), values)
            elif isinstance(cols[p], ExtOneToManyRelationshipColumn):
                cols[p].apply_data(obj, cols[p].parse_param(val))
            else:
                setattr(obj, trans[p].key, cols[p].parse_param(val))
        request.run_hook('np.object.set_values', obj, values, request, self)

    def create(self, params, request):
        logger.debug('Running API call, class:%s method:create params:%r',
                     self.name, params)
        res = {
            'records': [],
            'success': True,
            'total':   0
        }
        cols = self.get_columns()
        rcols = self.get_read_columns()
        trans = self._get_trans(rcols)

        sess = DBSession()

        for pt in params['records']:
            p = self.pk
            if p in pt:
                del pt[p]
            p = self.object_pk
            if p in pt:
                del pt[p]
            obj = self.model()
            obj.__req__ = request
            apply_onetomany = []
            helper = getattr(self.model, '__augment_create__', None)
            if callable(helper) and not helper(sess, obj, pt, request):
                continue
            for p in pt:
                if p not in cols:
                    if (p in rcols
                            and isinstance(rcols[p],
                                           ExtOneToManyRelationshipColumn)):
                        cols[p] = rcols[p]
                    elif p in self.model.__mapper__.attrs:
                        attr = self.model.__mapper__.attrs[p]
                        # FIXME: wtf is this?
                        if hasattr(attr, 'columns') and len(attr.columns) > 0:
                            cols[p] = self.get_column(p)
                        else:
                            continue
                    else:
                        continue
                if cols[p].get_read_only(request):
                    continue
                choices = cols[p].get_choices(request)
                if choices:
                    chosen_val = cols[p].parse_param(pt[p])
                    if chosen_val not in choices:
                        continue
                writer = cols[p].writer
                if writer:
                    writer = getattr(obj, writer, None)
                    if callable(writer):
                        if cols[p].pass_request:
                            writer(cols[p].parse_param(pt[p]), pt, request)
                        else:
                            writer(cols[p].parse_param(pt[p]), pt)
                elif isinstance(cols[p], ExtOneToManyRelationshipColumn):
                    apply_onetomany.append((cols[p],
                                            cols[p].parse_param(pt[p])))
                else:
                    setattr(obj, trans[p].key, cols[p].parse_param(pt[p]))
            sess.add(obj)
            sess.flush()
            request.run_hook('np.object.create', obj, pt, request, self)
            for otm in apply_onetomany:
                otm[0].apply_data(obj, otm[1])
            p = {}
            if '_clid' in pt:
                p['_clid'] = pt['_clid']
            pt = p
            for cname, col in rcols.items():
                if isinstance(cname, PseudoColumn):
                    if col.get_secret_value(request):
                        continue
                    if isinstance(cname, HybridColumn):
                        pt[cname.name] = getattr(obj, cname.name)
                    continue
                if col.get_secret_value(request):
                    continue
                if trans[cname].deferred:
                    continue
                if isinstance(col, ExtRelationshipColumn):
                    extra = col.append_data(obj)
                    if extra is not None:
                        pt.update(extra)
                else:
                    reader = col.reader
                    if reader:
                        reader = getattr(obj, reader, None)
                        if callable(reader):
                            if col.pass_request:
                                pt[cname] = reader(params, request)
                            else:
                                pt[cname] = reader(params)
                        else:
                            pt[cname] = reader
                    else:
                        pt[cname] = getattr(obj, trans[cname].key)
            pt[self.pk] = getattr(obj, self.object_pk)
            pt['__str__'] = str(obj)
            if self.is_polymorphic:
                pt['__poly'] = (obj.__class__.__moddef__,
                                obj.__class__.__name__)
            for extra in self.extra_data:
                edata = getattr(obj, extra, None)
                if callable(edata):
                    pt[extra] = edata(request)
                else:
                    pt[extra] = edata
            request.run_hook('np.object.read', obj, pt, None, request, self)
            res['records'].append(pt)
            res['total'] += 1
        return res

    def update(self, params, request):
        logger.debug('Running API call, class:%s method:update params:%r',
                     self.name, params)
        res = {
            'records': [],
            'success': True,
            'total':   0
        }
        cols = self.get_columns()
        rcols = self.get_read_columns()
        trans = self._get_trans(rcols)

        sess = DBSession()

        for pt in params['records']:
            if self.pk not in pt:
                raise Exception('Can\'t find primary key in record parameters')
            obj = sess.query(self.model).get(pt[self.pk])
            obj.__req__ = request
            helper = getattr(self.model, '__augment_update__', None)
            if callable(helper) and not helper(sess, obj, pt, request):
                continue
            for p in pt:
                if p in (self.pk, self.object_pk):
                    continue
                if p not in cols:
                    if (p in rcols
                            and isinstance(rcols[p],
                                           ExtOneToManyRelationshipColumn)):
                        cols[p] = rcols[p]
                    elif p in self.model.__mapper__.attrs:
                        attr = self.model.__mapper__.attrs[p]
                        # FIXME: wtf is this?
                        if hasattr(attr, 'columns') and len(attr.columns) > 0:
                            cols[p] = self.get_column(p)
                        else:
                            continue
                    else:
                        continue
                if cols[p].get_read_only(request):
                    continue
                choices = cols[p].get_choices(request)
                if choices:
                    chosen_val = cols[p].parse_param(pt[p])
                    if chosen_val not in choices:
                        continue
                writer = cols[p].writer
                if writer:
                    writer = getattr(obj, writer, None)
                    if callable(writer):
                        if cols[p].pass_request:
                            writer(cols[p].parse_param(pt[p]), pt, request)
                        else:
                            writer(cols[p].parse_param(pt[p]), pt)
                elif isinstance(cols[p], ExtOneToManyRelationshipColumn):
                    cols[p].apply_data(obj, cols[p].parse_param(pt[p]))
                else:
                    setattr(obj, trans[p].key, cols[p].parse_param(pt[p]))
            request.run_hook('np.object.update', obj, pt, request, self)
            pt = {}
            for cname, col in rcols.items():
                if isinstance(cname, PseudoColumn):
                    if col.get_secret_value(request):
                        continue
                    if isinstance(cname, HybridColumn):
                        pt[cname.name] = getattr(obj, cname.name)
                    continue
                if col.get_secret_value(request):
                    continue
                if trans[cname].deferred:
                    continue
                if isinstance(col, ExtRelationshipColumn):
                    extra = col.append_data(obj)
                    if extra is not None:
                        pt.update(extra)
                else:
                    pt[cname] = getattr(obj, trans[cname].key)
            pt['__str__'] = str(obj)
            if self.is_polymorphic:
                pt['__poly'] = (obj.__class__.__moddef__,
                                obj.__class__.__name__)
            for extra in self.extra_data:
                edata = getattr(obj, extra, None)
                if callable(edata):
                    pt[extra] = edata(request)
                else:
                    pt[extra] = edata
            request.run_hook('np.object.read', obj, pt, None, request, self)
            res['records'].append(pt)
            res['total'] += 1
        return res

    def delete(self, params, request):
        logger.debug('Running API call, class:%s method:delete params:%r',
                     self.name, params)
        res = {
            'success': True,
            'total':   0
        }
        sess = DBSession()
        for pt in params['records']:
            if self.pk not in pt:
                raise Exception('Can\'t find primary key in record parameters')
            obj = sess.query(self.model).get(pt[self.pk])
            obj.__req__ = request
            helper = getattr(self.model, '__augment_delete__', None)
            if callable(helper) and not helper(sess, obj, pt, request):
                continue
            sess.delete(obj)
            res['total'] += 1
            request.run_hook('np.object.delete', res, obj, pt, request, self)
        return res

    def get_fields(self, request):
        logger.debug('Running API call, class:%s method:get_fields', self.name)
        fields = []
        for cname, col in self.get_form_columns().items():
            fdef = col.get_editor_cfg(request, in_form=True)
            if fdef is not None:
                if col.multivalue:
                    fdef = col.get_editor_multivalue(request, fdef)
                fields.append(fdef)
        is_ro = False
        if self.cap_edit and not request.has_permission(self.cap_edit):
            is_ro = True
        request.run_hook('np.fields.get', fields, request, self)
        return {
            'success': True,
            'fields':  fields,
            'rvalid':  True if len(self.u_idx) > 0 else False,
            'ro':      is_ro
        }

    def validate_fields(self, values, request):
        logger.debug('Running API call, '
                     'class:%s method:validate_fields values:%r',
                     self.name, values)
        loc = request.localizer
        cols = self.get_columns()
        trans = self._get_trans(cols)
        sess = DBSession()
        if self.is_polymorphic:
            poly_name = self.model.__mapper__.polymorphic_on.name
            poly_val = self.model.__mapper__.polymorphic_identity
            if (poly_name
                    and poly_val is not None
                    and poly_name in cols
                    and poly_name not in values):
                values[poly_name] = poly_val
        pkey = None
        if (self.pk in values) and values[self.pk]:
            pkey = cols[self.pk].parse_param(values[self.pk])
        fields = defaultdict(list)
        for name, col in cols.items():
            valid = col.validator
            if callable(valid) and name in values:
                vres = valid(self, name, values, request)
                if vres:
                    if isinstance(vres, Iterable):
                        fields[name].extend(vres)
                    else:
                        fields[name].append(vres)
        for index in self.u_idx:
            has_all = True
            has_defined = False
            for ifld in index:
                if ifld not in cols or ifld not in trans:
                    has_all = False
                    break
                colval = values.get(ifld)
                if colval is not None:
                    has_defined = True
                elif not cols[ifld].nullable:
                    has_all = False
                    break
            if not has_all or not has_defined:
                continue
            q = sess.query(func.count('*')).select_from(self.model)
            for ifld in index:
                prop = trans[ifld]
                extcol = cols[ifld]
                col = getattr(self.model, prop.key)
                q = q.filter(col == extcol.parse_param(values.get(ifld)))
            if pkey is not None:
                col = getattr(self.model, self.object_pk)
                q = q.filter(col != pkey)
            num = q.scalar()
            if num is not None and num > 0:
                for ifld in index:
                    fields[ifld].append(
                            loc.translate(_('This field must be unique.')))
        request.run_hook('np.fields.validate', fields, values, request, self)
        return {
            'success': True,
            'errors':  fields
        }

    def get_create_wizard(self, request):
        logger.debug('Running API call, class:%s method:get_create_wizard',
                     self.name)
        wiz = self.create_wizard
        if wiz:
            if not wiz.init_done:
                request.run_hook('np.wizard.init.%s.%s' % (
                        self.model.__moddef__,
                        self.name),
                    wiz, self, request)
                wiz.init_done = True
            title = wiz.title
            if title:
                loc = request.localizer
                title = loc.translate(title)
            ret = {
                'success': True,
                'fields':  wiz.get_cfg(self, request, use_defaults=True),
                'title':   title
            }
            if wiz.validator:
                ret['validator'] = wiz.validator
            request.run_hook('np.create_wizard.get', ret, wiz, request, self)
            return ret
        return {'success': False, 'fields': []}

    def get_wizard(self, wname, request):
        logger.debug('Running API call, class:%s method:get_wizard wname:%s',
                     self.name, wname)
        wizdict = self.wizards
        if wizdict and wname in wizdict:
            wiz = wizdict[wname]
            if not wiz.init_done:
                request.run_hook('np.wizard.init.%s.%s' % (
                        self.model.__moddef__,
                        self.name),
                    wiz, self, request)
                wiz.init_done = True
            title = wiz.title
            if title:
                loc = request.localizer
                title = loc.translate(title)
            ret = {
                'success': True,
                'fields':  wiz.get_cfg(self, request, use_defaults=True),
                'title':   title
            }
            if wiz.validator:
                ret['validator'] = wiz.validator
            request.run_hook('np.wizard.get', ret, wiz, request, self)
            return ret
        return {'success': False, 'fields': []}

    def create_wizard_action(self, pane_id, act, values, request):
        logger.debug('Running API call, '
                     'class:%s method:create_wizard_action pane_id:%r '
                     'act:%r values:%r',
                     self.name, pane_id, act, values)
        wiz = self.create_wizard
        if wiz:
            if not wiz.init_done:
                request.run_hook('np.wizard.init.%s.%s' % (
                        self.model.__moddef__,
                        self.name),
                    wiz, self, request)
                wiz.init_done = True
            ret = wiz.action(self, pane_id, act, values, request)
            if ret:
                request.run_hook('np.create_wizard.action',
                                 ret, wiz, pane_id, act, values,
                                 request, self)
                return {'success': True, 'action':  ret}
        return {'success': False}

    def wizard_action(self, wname, pane_id, act, values, request):
        logger.debug('Running API call, '
                     'class:%s method:wizard_action wname:%s pane_id:%r '
                     'act:%r values:%r',
                     self.name, wname, pane_id, act, values)
        wizdict = self.wizards
        if wizdict and wname in wizdict:
            wiz = wizdict[wname]
            if not wiz.init_done:
                request.run_hook('np.wizard.init.%s.%s' % (
                        self.model.__moddef__,
                        self.name),
                    wiz, self, request)
                wiz.init_done = True
            ret = wiz.action(self, pane_id, act, values, request)
            if ret:
                request.run_hook('np.wizard.action',
                                 ret, wiz, pane_id, act, values,
                                 request, self)
                return {'success': True, 'action': ret}
        return {'success': False}

    def get_menu_tree(self, req, name):
        if self.show_in_menu == name:
            loc = req.localizer
            xname = self.name.lower()
            ret = {
                'id':      xname,
                'text':    loc.translate(self.menu_name),
                'leaf':    True,
                'iconCls': 'ico-mod-%s' % xname,
                'xview':   'grid_%s_%s' % (self.__parent__.moddef, self.name)
            }
            xsect = self.menu_section
            if xsect is not None:
                ret['section'] = xsect
            xpa = self.menu_parent
            if xpa is not None:
                ret['parent'] = xpa
            if self.menu_main:
                ret['main'] = True
            return ret

    def get_detail_pane(self, req):
        dpview = self.detail_pane
        if dpview is None:
            return None
        if len(dpview) != 2:
            raise ValueError('Wrong detail pane specification')
        mod = getattr(self, '_dpane', None)
        if mod is None:
            mod = self._dpane = importlib.import_module(dpview[0])
        dpview = getattr(mod, dpview[1])
        if callable(dpview):
            return dpview(self, req)

    def report(self, params, request):
        logger.debug('Running API call, class:%s method:report params:%r',
                     self.name, params)
        res = {
            'records': [],
            'success': True,
            'total':   0
        }
        q_colnames = []
        q_columns = []
        q_groupby = []
        records = []
        tot = 0
        cols = self.get_read_columns()
        trans = self._get_trans(cols)
        sess = DBSession()
        engine = sess.get_bind(self.model)

        if '__aggregates' in params:
            for qcol in params['__aggregates']:
                if qcol[1] not in trans:
                    continue
                prop = getattr(self.model, trans[qcol[1]].key)
                q_colnames.append(qcol[2])
                q_columns.append(_get_aggregate_column(engine.dialect,
                                                       qcol[0],
                                                       prop, qcol[2]))
        if len(q_columns) == 0:
            q_colnames.append('cnt')
            q_columns.append(func.count('*').label('cnt'))
        if '__groupby' in params:
            for gbcol in params['__groupby']:
                if isinstance(gbcol, str):
                    if gbcol not in trans:
                        continue
                    prop = getattr(self.model, trans[gbcol].key)
                    q_colnames.append(gbcol)
                    q_columns.append(prop.label(gbcol))
                    q_groupby.append(prop)
                    continue
                if gbcol[1] not in trans:
                    continue
                prop = getattr(self.model, trans[gbcol[1]].key)
                colname = '_'.join((gbcol[1], gbcol[0]))
                q_colnames.append(colname)
                q_columns.append(_get_groupby_clause(engine.dialect,
                                                     gbcol[0],
                                                     prop).label(colname))
                q_groupby.append(_get_groupby_clause(engine.dialect,
                                                     gbcol[0], prop))

        q = sess.query(*q_columns).select_from(self.model)
        if '__ffilter' in params:
            q = self._apply_filters(q, trans, params, pname='__ffilter')
        if '__filter' in params:
            q = self._apply_filters(q, trans, params)
        if '__xfilter' in params:
            q = self._apply_xfilters(q, params)
        if '__sstr' in params:
            q = self._apply_sstr(q, trans, params)
        # TODO: __sort
        if len(q_groupby) > 0:
            q = q.group_by(*q_groupby).order_by(*q_groupby)
        helper = getattr(self.model, '__augment_query__', None)
        if callable(helper):
            q = helper(sess, q, params, request)
        # TODO: need additional augment-style hook to filter report resultset

        for obj in q:
            tot += 1
            records.append(dict((colname, getattr(obj, colname))
                                for colname
                                in q_colnames))

        res['records'] = records
        res['total'] = tot
        return res


class ExtModuleBrowser(object):
    def __init__(self, mmgr, moddef):
        if moddef not in mmgr.modules:
            raise KeyError('Unknown module: \'%s\'')
        self.mmgr = mmgr
        self.moddef = moddef

    @property
    def __name__(self):
        return self.moddef

    def __getitem__(self, name):
        sqla_model = self.mmgr.models[self.moddef][name]
        mod = ExtModel(sqla_model)
        mod.__parent__ = self
        return mod

    def __iter__(self):
        return iter(self.mmgr.models[self.moddef])


class ExtBrowser(object):
    def __init__(self, mmgr):
        self.mmgr = mmgr

    def __getitem__(self, moddef):
        modbr = ExtModuleBrowser(self.mmgr, moddef)
        modbr.__parent__ = self
        return modbr

    def __iter__(self):
        return iter(self.mmgr.loaded)

    def get_menu_data(self, request):
        ret = []
        for menu in self.mmgr.menu_generator(request):
            if menu.perm and not request.has_permission(menu.perm):
                continue
            ret.append(menu)
        return sorted(ret, key=lambda m: m.order)

    def get_menu_tree(self, req, name):
        loc = req.localizer
        menu = []
        id_cache = {}
        module_mains = {}
        module_sections = defaultdict(dict)
        module_children = defaultdict(list)
        direct_children = defaultdict(list)

        for module in self:
            extmodule = self[module]
            for model in extmodule:
                em = extmodule[model]

                if em.cap_menu and not req.has_permission(em.cap_menu):
                    continue
                if em.cap_read and not req.has_permission(em.cap_read):
                    continue

                item = em.get_menu_tree(req, name)
                if not item:
                    continue

                id_cache[item['id']] = item

                if item.get('main'):
                    del item['main']
                    module_mains[module] = item
                    continue
                if 'section' in item:
                    sect_name = item['section']
                    del item['section']
                    sections = module_sections[module]
                    if sect_name not in sections:
                        # TODO: Make iconCls customizable.
                        sections[sect_name] = {
                            'text':     loc.translate(sect_name),
                            'expanded': True,
                            'children': [],
                            'iconCls':  'ico-node'
                        }
                    sections[sect_name]['children'].append(item)
                elif 'parent' in item:
                    parent = item['parent']
                    del item['parent']
                    direct_children[parent].append(item)
                else:
                    module_children[module].append(item)

        for parent_id, items in direct_children.items():
            if parent_id not in id_cache:
                continue
            parent = id_cache[parent_id]
            if 'children' not in parent:
                parent['children'] = []
            if 'expanded' not in parent:
                parent['expanded'] = True
            if 'leaf' in parent:
                del parent['leaf']
            parent['children'].extend(sorted(items, key=lambda mt: mt['text']))

        # TODO: implement per-user (or global) storable weights, and use them
        #       in addition to these lambdas

        for module in self:
            children = module_children[module]
            if module in module_mains:
                module_menu = module_mains[module]
                if 'leaf' in module_menu:
                    del module_menu['leaf']
                module_menu['expanded'] = True
            else:
                # TODO: Make iconCls customizable.
                module_menu = {
                    'id':       module,
                    'text':     loc.translate(self.mmgr.loaded[module].name),
                    'expanded': True,
                    'iconCls':  'ico-module'
                }

            for sect in module_sections[module].values():
                sect['children'] = sorted(sect['children'],
                                          key=lambda mt: mt['text'])
                children.append(sect)

            if module in direct_children:
                children.extend(direct_children[module])

            if len(children) > 0 or module in module_mains:
                if 'children' not in module_menu:
                    module_menu['children'] = []
                module_menu['children'].extend(children)
                module_menu['children'] = sorted(module_menu['children'],
                                                 key=lambda mt: mt['text'])
                menu.append(module_menu)

        req.run_hook('np.menu', name, menu, req, self)
        return sorted(menu, key=lambda mt: mt['text'])

    def get_export_menu(self, req):
        return tuple(fmt.export_panel(req, name)
                     for name, fmt
                     in sorted(self.mmgr.get_export_formats().items(),
                               key=lambda x: x[0])
                     if fmt.enabled(req))
