#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Geo module - Filters
# Copyright © 2013 Nikita Andriyanov
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

from pyramid.i18n import get_localizer

from netprofile.ext.filters import Filter


class AddressFilter(Filter):
    def __init__(self, name, hdl, **kwargs):
        super(AddressFilter, self).__init__(name, hdl, **kwargs)
        self.show_cities = kwargs.get('show_cities', True)
        self.show_districts = kwargs.get('show_districts', True)
        self.show_streets = kwargs.get('show_streets', True)
        self.show_houses = kwargs.get('show_houses', True)
        self.show_places = kwargs.get('show_places', False)

    def get_cfg(self, req):
        loc = get_localizer(req)
        cfg = {
            'xtype':           'address',
            'name':            self.name,
            'fieldLabel':      loc.translate(self.title),
            'displayCity':     self.show_cities,
            'displayDistrict': self.show_districts,
            'displayStreet':   self.show_streets,
            'displayHouse':    self.show_houses,
            'displayPlace':    self.show_places
        }
        return cfg
