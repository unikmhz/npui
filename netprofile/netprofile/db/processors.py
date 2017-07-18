#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Misc. callback functions for SQLAlchemy
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


def boolean_to_enum(value):
    if value is None:
        return None
    if value == 'FALSE':
        return 'N'
    if value:
        return 'Y'
    return 'N'


def enum_to_boolean(value):
    if value is None:
        return None
    if value == 'Y':
        return True
    if value == b'Y':
        return True
    return False
