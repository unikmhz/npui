#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Custom ExtJS data filters
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


class Filter(object):
    def __init__(self, name, hdl, **kwargs):
        self.name = name
        self.title = kwargs.get('title', name)
        self.handler = hdl

    def get_cfg(self, req):
        raise NotImplementedError('No layout can be generated '
                                  'from abstract base filter.')

    def process(self, cls, query, value):
        hdl = self.handler.__get__(self.handler, cls)
        if callable(hdl):
            return hdl(query, value)
        return query


class TextFilter(Filter):
    def __init__(self, name, hdl, **kwargs):
        super(TextFilter, self).__init__(name, hdl, **kwargs)
        self.length = kwargs.get('length')
        self.length_err = kwargs.get('length_err')
        self.regex = kwargs.get('regex')
        self.regex_text = kwargs.get('regex_err')

    def get_cfg(self, req):
        cfg = {
            'xtype':      'textfield',
            'name':       self.name,
            'fieldLabel': req.localizer.translate(self.title)
        }
        # TODO: add config
        return cfg


class NumberFilter(TextFilter):
    pass


class SelectFilter(Filter):
    def __init__(self, name, hdl, **kwargs):
        super(SelectFilter, self).__init__(name, hdl, **kwargs)
        self.data = kwargs.get('data')
        self.value_field = kwargs.get('value_field')
        self.display_field = kwargs.get('display_field')

    def get_cfg(self, req):
        cfg = {
            'xtype':      'combo',
            'name':       self.name,
            'fieldLabel': req.localizer.translate(self.title),
            'editable':   False,
            'autoSelect': False
        }
        if isinstance(self.data, str):
            cfg['store'] = self.data
        if self.value_field:
            cfg['valueField'] = self.value_field
        if self.display_field:
            cfg['displayField'] = self.display_field
        return cfg


class GroupFilter(Filter):
    pass


class RadioGroupFilter(GroupFilter):
    pass


class CheckboxGroupFilter(GroupFilter):
    def __init__(self, name, hdl, **kwargs):
        super(CheckboxGroupFilter, self).__init__(name, hdl, **kwargs)
        self.data = kwargs.get('data')
        self.value_field = kwargs.get('value_field')
        self.display_field = kwargs.get('display_field')
        self.columns = kwargs.get('columns', 2)
        self.vertical = kwargs.get('vertical', True)

    def get_cfg(self, req):
        cfg = {
            'xtype':      'dyncheckboxgroup',
            'name':       self.name,
            'fieldLabel': req.localizer.translate(self.title),
            'vertical':   self.vertical,
            'layout':     {
                'type':    'table',
                'columns': self.columns
            },
            'defaults':   {
                'margin':     3,
                'labelAlign': 'left'
            }
        }
        if isinstance(self.data, str):
            cfg['store'] = self.data
        if self.value_field:
            cfg['valueField'] = self.value_field
        if self.display_field:
            cfg['displayField'] = self.display_field
        return cfg
