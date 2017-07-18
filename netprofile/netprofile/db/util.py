#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Various DB-related helper functions
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

from itertools import groupby
from sqlalchemy.orm import attributes


def populate_related(parents, id_key, res_key, reltype, subq,
                     flt=None, relid_key='id'):
    ids = []
    for p in parents:
        if callable(flt) and not flt(p):
            continue
        keyval = getattr(p, id_key, None)
        if keyval and keyval not in ids:
            ids.append(keyval)
    if len(ids) > 0:
        for rel in subq.filter(getattr(reltype, relid_key).in_(ids)):
            for p in parents:
                if callable(flt) and not flt(p):
                    continue
                keyval = getattr(p, id_key, None)
                if keyval and keyval == getattr(rel, relid_key):
                    attributes.set_committed_value(p, res_key, rel)


def populate_related_list(parents, id_key, res_key, reltype, subq,
                          flt=None, relid_key='id'):
    ids = []
    for p in parents:
        if callable(flt) and not flt(p):
            continue
        keyval = getattr(p, id_key, None)
        if keyval and keyval not in ids:
            ids.append(keyval)
    if len(ids) > 0:
        ch = dict((k, list(v)) for k, v in groupby(
            subq.filter(getattr(reltype, relid_key).in_(ids)),
            lambda c: getattr(c, relid_key)))
    for p in parents:
        if callable(flt) and not flt(p):
            continue
        keyval = getattr(p, id_key, None)
        if keyval:
            attributes.set_committed_value(p, res_key, ch.get(keyval, ()))
