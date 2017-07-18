#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# NetProfile: Templates - Utilities
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

import filecmp
import glob
import os
import shutil
from sqlalchemy.engine.interfaces import Dialect


def _check_objtype(objtype):
    if objtype not in {'triggers', 'functions', 'events'}:
        raise ValueError('Wrong SQL schema object type: \'%s\'.' % (objtype,))


def get_sqltpl_path(mm, dialect, modname, objtype, name, rev=None):
    """
    Get absolute path to SQL schema object template file.
    """
    if modname[:11] == 'netprofile_':
        moddef = modname[11:]
    else:
        moddef = modname
        modname = 'netprofile_' + modname
    if moddef not in mm.modules:
        return None
    mod = mm.modules[moddef]
    if not mod.dist or not mod.dist.location:
        return None
    _check_objtype(objtype)
    path = [mod.dist.location, modname, 'templates', 'sql']
    fname = [name]

    if isinstance(dialect, Dialect):
        path.append(dialect.name)
    else:
        path.append(dialect)

    if rev is not None:
        fname.append(rev)
    fname.append('mak')

    path.extend((objtype, '.'.join(fname)))
    return os.path.join(*path)


def get_sqltpl_revisions(mm, dialect, moddef, objtype, name):
    glob_path = get_sqltpl_path(mm, dialect, moddef, objtype, '*')
    ret = set()
    for file_path in glob.iglob(glob_path):
        fname = os.path.split(file_path)[1].split('.')
        if len(fname) == 3:
            ret.add(fname[1])
    return ret


def diff_sqltpl(mm, dialect, moddef, objtype, name, rev):
    src_path = get_sqltpl_path(mm, dialect, moddef, objtype, name)
    dst_path = get_sqltpl_path(mm, dialect, moddef, objtype, name, rev)
    return not filecmp.cmp(src_path, dst_path, False)


def new_sqltpl_revision(mm, dialect, moddef, objtype, name, rev):
    src_path = get_sqltpl_path(mm, dialect, moddef, objtype, name)
    dst_path = get_sqltpl_path(mm, dialect, moddef, objtype, name, rev)
    shutil.copy2(src_path, dst_path)
