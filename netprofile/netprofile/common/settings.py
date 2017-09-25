#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Global/user settings
# Copyright © 2016-2017 Alex Unigovsky
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

__all__ = [
    'Setting',
    'SettingSection'
]

from collections import MutableMapping


class SettingSection(MutableMapping):
    def __init__(self, name, *settings, vhost='MAIN', scope='global',
                 title=None, read_cap=None, help_text=None):
        self.name = name
        self.settings = dict((setting.name, setting) for setting in settings)
        self.vhost = vhost
        self.scope = scope
        self.title = title
        self.read_cap = read_cap
        self.help_text = help_text

    def __iter__(self):
        for key in self.settings:
            yield key

    def __getitem__(self, name):
        return self.settings[name]

    def __setitem__(self, name, value):
        self.settings[name] = value

    def __delitem__(self, name):
        del self.settings[name]

    def __contains__(self, name):
        return name in self.settings

    def __len__(self):
        return len(self.settings)

    def keys(self):
        return self.settings.keys()

    def get_tree_cfg(self, req, moddef, handler=None):
        if self.read_cap and not req.has_permission(self.read_cap):
            return None
        loc = req.localizer
        ret = {
            'id': '.'.join((moddef, self.name)),
            'text': loc.translate(self.title) if self.title else self.name,
            'leaf': True,
            'iconCls': 'ico-cog'
        }
        if handler:
            ret['xhandler'] = handler
        return ret

    def get_form_cfg(self, req, moddef, values={}):
        if self.read_cap and not req.has_permission(self.read_cap):
            return None
        fields = []
        for setting_name, setting in self.settings.items():
            fld = setting.get_form_cfg(
                req, moddef, self,
                values.get('%s.%s.%s' % (moddef, self.name, setting_name))
            )
            if fld:
                fields.append(fld)

            if setting.additional_fields:
                add = setting.additional_fields
                if callable(add):
                    add = add(req, self, moddef, fields, values)
                for addfld in add:
                    if 'name' in addfld and '.' not in addfld['name']:
                        addfld['name'] = '.'.join((moddef,
                                                   self.name,
                                                   addfld['name']))
                    fields.append(addfld)
        loc = req.localizer
        return {
            'success': True,
            'fields': fields,
            'section': {
                'id': '.'.join((moddef, self.name)),
                'name': loc.translate(self.title) if self.title else self.name,
                'descr': loc.translate(
                    self.help_text) if self.help_text else None
            }
        }


class Setting(object):
    def __init__(self, name, title=None, type='string', pass_to_client=True,
                 read_cap=None, write_cap=None, default=None, help_text=None,
                 field_cfg=None, field_extra=None, nullable=False,
                 additional_fields=None):
        self.name = name
        self.title = title
        self.type = type
        self.client_ok = pass_to_client
        self.read_cap = read_cap
        self.write_cap = write_cap
        self.default = default
        self.help_text = help_text
        self.nullable = nullable
        self.additional_fields = additional_fields

        if field_cfg is None:
            if self.type == 'bool':
                field_cfg = self.field_bool
            elif self.type == 'int':
                field_cfg = self.field_int
            elif self.type == 'string':
                field_cfg = self.field_string
            else:
                raise ValueError('Unrecognized setting type: %r.' %
                                 (self.type,))

        self.field_cfg = field_cfg
        self.field_extra = field_extra

    def parse_param(self, param):
        if self.nullable and param in {'', None}:
            return None
        if self.type == 'bool':
            if isinstance(param, bool):
                return param
            return param.lower() in {'true', '1', 'on', 'yes'}
        if self.type == 'int':
            return int(param)
        if self.type == 'float':
            return float(param)
        return param

    def format_param(self, param):
        if self.nullable and param in {'', None}:
            return None
        if self.type == 'bool':
            return 'true' if param else 'false'
        return str(param)

    def field_bool(self, req, moddef, section, value):
        return {
            'xtype': 'checkbox',
            'inputValue': 'true',
            'uncheckedValue': 'false'
        }

    def field_int(self, req, moddef, section, value):
        return {
            'xtype': 'numberfield',
            'allowDecimals': False
        }

    def field_string(self, req, moddef, section, value):
        return {
            'xtype': 'textfield',
            'maxLength': 255
        }

    def get_form_cfg(self, req, moddef, section, value=None):
        if self.read_cap and not req.has_permission(self.read_cap):
            return None
        loc = req.localizer
        if callable(self.field_cfg):
            cfg = self.field_cfg(req, moddef, section, value)
        else:
            cfg = self.field_cfg.copy()
        field_name = '.'.join((moddef,
                               section.name,
                               cfg.get('name', self.name)))
        cfg.update({
            'name': field_name,
            'fieldLabel': loc.translate(
                self.title) if self.title else self.name,
            'description': loc.translate(
                self.help_text) if self.help_text else None
        })
        if value is None and self.default is not None:
            value = self.default
        if value is not None and self.client_ok:
            cfg['value'] = self.format_param(value)
            if self.type == 'bool':
                cfg['checked'] = value
        extra = self.field_extra
        if extra:
            if callable(extra):
                extra = extra(req, moddef, section, value)
            cfg.update(extra)
        return cfg
